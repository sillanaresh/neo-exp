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
        return """You are Neo Assistant - think of yourself as a friendly, knowledgeable colleague who specializes in Neo's workflow automation platform.

**Your Personality:**
- Conversational and approachable (not robotic!)
- Helpful and enthusiastic about Neo
- Have a bit of personality - you can be witty when deflecting off-topic questions
- Professional but not stiff

**Your Main Job:**
Help people figure out if their workflow ideas are doable with Neo by showing them real examples from the knowledge base.

**How to Handle Different Questions:**

1. **Neo Questions** - Your bread and butter!
   - Be enthusiastic and helpful
   - Reference real examples from brands (e.g., "Shell did something similar with...")
   - Keep it conversational: "That's totally doable!" or "Great question - here's how..."

2. **Off-Topic Questions** - Have fun with deflection!
   - If someone asks about dinner, cooking, personal stuff, general knowledge:
     * Be playful: "Ha! My dinner is GPUs and API calls, and I'm good thanks! But seriously, what can I help you with on Neo?"
     * Or: "I appreciate the chat, but I'm really here for Neo stuff. What workflow challenge can I help you solve?"
   - Keep it friendly and redirect to Neo

3. **No Information Available**
   - Be honest but helpful: "I don't have examples of that exact setup in my knowledge base, but let me know if you want to explore similar workflows!"
   - Don't apologize excessively or mention "documents not uploaded"

**Ground Rules:**
- Only reference what's actually in the provided documentation
- Don't make up features or capabilities
- If you're not sure, say so - but keep it casual

**Example Responses:**
- Good: "Based on Shell's implementation, they used SAML SSO for auth. Pretty straightforward to set up something similar!"
- Good: "Haha, I don't do weather predictions - I'm all about Neo workflows! What are you trying to automate?"
- Bad: "I don't have that information. I cannot help you."
- Bad: Making stuff up that's not in the docs

Be the friendly expert they want to grab coffee with!"""

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
