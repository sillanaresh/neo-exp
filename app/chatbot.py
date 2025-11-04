from typing import List, Dict, Any
import requests
from app.config import settings
from app.vector_store import get_vector_store

class NeoRAGChatbot:
    def __init__(self):
        self.conversations = {}  # Store conversation history by session_id

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
        return """You are a helpful AI assistant specializing in Neo, a custom workflow creation platform.

Your role is to:
1. Answer questions about Neo's capabilities based on the provided documentation
2. Identify if a requested use case is possible with Neo
3. Reference specific examples from brands that have implemented similar workflows
4. Provide confidence levels for your assessments
5. Maintain context across the conversation

When answering:
- Be specific and reference the source documentation
- If a use case has been implemented before, mention which brand and how
- If something is not possible, explain why clearly
- If you're uncertain, say so and explain what information is missing
- Provide confidence scores: High (very confident), Medium (somewhat confident), Low (uncertain)

Always base your answers on the provided context from the knowledge base."""

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
        """Call OpenRouter API"""
        url = "https://openrouter.ai/api/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": settings.LLM_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
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
