"""
JARVIS AI Brain Module
Integrates OpenAI GPT API with short-term conversation memory.
Falls back gracefully if no API key is configured.
"""

import logging
from typing import Optional
from collections import deque

logger = logging.getLogger(__name__)


class AIBrain:
    """
    Core AI engine. Maintains conversation history and communicates
    with OpenAI GPT. Gracefully degrades if API is unavailable.
    """

    def __init__(self, config):
        self.config = config
        self.client = None
        self.conversation_history: deque = deque(maxlen=config.short_term_memory_limit)
        self._initialize_client()

    def _initialize_client(self):
        """Attempt to connect to OpenAI API."""
        if not self.config.openai_api_key:
            logger.warning("No OpenAI API key configured. AI brain running in limited mode.")
            return
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.config.openai_api_key)
            logger.info("OpenAI client initialized successfully.")
        except ImportError:
            logger.error("openai package not installed. Run: pip install openai")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")

    def think(self, user_input: str, context: Optional[str] = None) -> str:
        """
        Send user input to GPT and return AI response.
        Maintains rolling conversation history for context.

        Args:
            user_input: The user's message/query
            context: Optional extra context to prepend (e.g., system status)

        Returns:
            AI response string
        """
        if not self.client:
            return self._fallback_response(user_input)

        # Add user message to history
        message_content = user_input
        if context:
            message_content = f"[System Context: {context}]\n\nUser: {user_input}"

        self.conversation_history.append({
            "role": "user",
            "content": message_content
        })

        try:
            messages = [
                {"role": "system", "content": self.config.ai_system_prompt}
            ] + list(self.conversation_history)

            response = self.client.chat.completions.create(
                model=self.config.ai_model,
                messages=messages,
                temperature=self.config.ai_temperature,
                max_tokens=self.config.ai_max_tokens,
            )

            reply = response.choices[0].message.content.strip()

            # Store assistant reply in history
            self.conversation_history.append({
                "role": "assistant",
                "content": reply
            })

            return reply

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return f"I encountered an issue connecting to my AI core: {str(e)}"

    def _fallback_response(self, user_input: str) -> str:
        """Provide a response when AI is unavailable."""
        return (
            "⚠️ AI brain is offline — no OpenAI API key configured.\n"
            "Please add your API key in Settings → Configure API Key.\n"
            "I can still execute system commands and local functions."
        )

    def clear_memory(self):
        """Clear short-term conversation memory."""
        self.conversation_history.clear()
        logger.info("Conversation memory cleared.")

    def get_history_summary(self) -> str:
        """Return a readable summary of conversation history."""
        if not self.conversation_history:
            return "No conversation history."
        lines = []
        for msg in self.conversation_history:
            role = "You" if msg["role"] == "user" else "JARVIS"
            lines.append(f"{role}: {msg['content'][:100]}{'...' if len(msg['content']) > 100 else ''}")
        return "\n".join(lines)

    def reload_client(self):
        """Reinitialize the OpenAI client (after API key update)."""
        self._initialize_client()
