from typing import List, Dict, Any
import requests
from openai import OpenAI
from app.config import settings
from app.vector_store import get_vector_store

class NeoRAGChatbot:
    def __init__(self):
        self.conversations = {}  # Store conversation history by session_id
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def chat(self, message: str, session_id: str = "default") -> Dict[str, Any]:
        """
        Main chat method with RAG
        Returns: {
            'response': str,
            'sources': List[Dict],
            'confidence': str
        }
        """
        # Get or create conversation history
        if session_id not in self.conversations:
            self.conversations[session_id] = []

        # Search for relevant context
        vector_store = get_vector_store()
        search_results = vector_store.search(message, top_k=5)

        # Build context from search results
        context = self._build_context(search_results)

        # Build conversation history
        conversation_history = self._build_history(session_id)

        # Create prompt
        system_prompt = self._create_system_prompt()
        user_prompt = self._create_user_prompt(message, context, conversation_history)

        # Call LLM via OpenRouter
        response = self._call_llm(system_prompt, user_prompt)

        # Store in conversation history
        self.conversations[session_id].append({
            'role': 'user',
            'content': message
        })
        self.conversations[session_id].append({
            'role': 'assistant',
            'content': response
        })

        # Limit history to last 10 exchanges
        if len(self.conversations[session_id]) > 20:
            self.conversations[session_id] = self.conversations[session_id][-20:]

        return {
            'response': response,
            'sources': self._format_sources(search_results),
            'session_id': session_id
        }

    def _build_context(self, search_results: List[Dict[str, Any]]) -> str:
        """Build context string from search results"""
        if not search_results:
            return "No relevant documentation found in the knowledge base."

        context_parts = []
        for i, result in enumerate(search_results, 1):
            doc_name = result.get('document_name', 'Unknown')
            text = result.get('text', '')
            score = result.get('score', 0)

            context_parts.append(f"[Source {i}: {doc_name} (relevance: {score:.2f})]\n{text}\n")

        return "\n".join(context_parts)

    def _build_history(self, session_id: str) -> str:
        """Build conversation history string"""
        if session_id not in self.conversations or not self.conversations[session_id]:
            return ""

        history_parts = []
        for msg in self.conversations[session_id][-6:]:  # Last 3 exchanges
            role = "User" if msg['role'] == 'user' else "Assistant"
            history_parts.append(f"{role}: {msg['content']}")

        return "\n".join(history_parts)

    def _create_system_prompt(self) -> str:
        """Create system prompt for the chatbot"""
        return """You are Neo Assistant, an AI helper specializing in the Neo workflow automation platform.

**Your Purpose:**
Help solution architects and users understand if their custom workflow use cases are feasible with Neo by referencing real-world implementations from our knowledge base.

**How to Respond:**
1. **Stay focused on Neo**: Only answer questions related to Neo platform, workflow automation, integrations, and implementation examples. If someone asks unrelated questions (like general knowledge, personal topics, or inappropriate content), politely say: "I'm here to help with Neo workflow questions. How can I assist you with Neo today?"

2. **Be helpful and conversational**: Don't be robotic. Chat naturally, use friendly language, and ask clarifying questions when needed.

3. **Ground your answers in documentation**: Always base responses on the provided context. If you find relevant examples, mention the brand name and how they implemented it (e.g., "Shell implemented this using...").

4. **Be honest about limitations**: If the documentation doesn't have enough info, say something like: "I don't have specific examples of this in the knowledge base, but let me know if you'd like to explore similar use cases."

5. **Don't make things up**: Never invent features, capabilities, or examples that aren't in the documentation.

**Example Responses:**
- Good: "Based on Shell's implementation, they handled authentication using SAML SSO. You could do something similar for your use case."
- Bad: "I don't have all the documents uploaded yet, so I can't help."
- Bad: Making up features or examples not in the docs.

Keep responses concise but informative. Be the helpful colleague they can rely on!"""

    def _create_user_prompt(self, message: str, context: str, history: str) -> str:
        """Create the full user prompt with context"""
        prompt_parts = []

        if history:
            prompt_parts.append(f"Previous conversation:\n{history}\n")

        prompt_parts.append(f"Relevant documentation:\n{context}\n")
        prompt_parts.append(f"User question: {message}\n")
        prompt_parts.append("""Please answer the question based on the documentation provided.
If the documentation doesn't contain enough information, say so clearly.
Format your response in a friendly, conversational way.""")

        return "\n".join(prompt_parts)

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Call OpenAI API with GPT-4o"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error calling LLM: {str(e)}"

    def _format_sources(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Format sources for response"""
        sources = []
        for result in search_results[:3]:  # Top 3 sources
            sources.append({
                'document': result.get('document_name', 'Unknown'),
                'relevance': f"{result.get('score', 0):.2f}",
                'snippet': result.get('text', '')[:200] + "..."
            })
        return sources

    def clear_conversation(self, session_id: str):
        """Clear conversation history for a session"""
        if session_id in self.conversations:
            del self.conversations[session_id]

# Global instance
chatbot = NeoRAGChatbot()
