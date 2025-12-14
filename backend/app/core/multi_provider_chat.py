"""Multi-provider chat service supporting Ollama, OpenAI, and Anthropic."""

from typing import AsyncGenerator, Optional
import ollama
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from ..config import settings
from ..utils.logger import logger


class MultiProviderChat:
    """Chat service that supports multiple AI providers."""

    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None

        # Initialize clients if API keys are available
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your_key_here":
            self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        if settings.ANTHROPIC_API_KEY and settings.ANTHROPIC_API_KEY != "your_key_here":
            self.anthropic_client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def chat_stream_ollama(
        self, messages: list, model: str
    ) -> AsyncGenerator[str, None]:
        """Stream chat responses from Ollama."""
        try:
            stream = ollama.chat(model=model, messages=messages, stream=True)

            for chunk in stream:
                if "message" in chunk and "content" in chunk["message"]:
                    content = chunk["message"]["content"]
                    if content:
                        yield content

        except Exception as e:
            logger.error(f"Ollama chat error: {e}")
            yield f"\n\nError: {str(e)}"

    async def chat_stream_openai(
        self, messages: list, model: str
    ) -> AsyncGenerator[str, None]:
        """Stream chat responses from OpenAI."""
        if not self.openai_client:
            yield "\n\nError: OpenAI API key not configured"
            return

        try:
            stream = await self.openai_client.chat.completions.create(
                model=model, messages=messages, stream=True, temperature=0.7
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"OpenAI chat error: {e}")
            yield f"\n\nError: {str(e)}"

    async def chat_stream_anthropic(
        self, messages: list, model: str
    ) -> AsyncGenerator[str, None]:
        """Stream chat responses from Anthropic Claude."""
        if not self.anthropic_client:
            yield "\n\nError: Anthropic API key not configured"
            return

        try:
            # Convert messages format (Anthropic needs system separate)
            system_message = None
            converted_messages = []

            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    converted_messages.append(
                        {"role": msg["role"], "content": msg["content"]}
                    )

            kwargs = {
                "model": model,
                "messages": converted_messages,
                "max_tokens": 4096,
                "stream": True,
            }

            if system_message:
                kwargs["system"] = system_message

            async with self.anthropic_client.messages.stream(**kwargs) as stream:
                async for text in stream.text_stream:
                    yield text

        except Exception as e:
            logger.error(f"Anthropic chat error: {e}")
            yield f"\n\nError: {str(e)}"

    async def chat_stream(
        self, messages: list, provider: str = "ollama", model: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat responses from the specified provider.

        Args:
            messages: List of message dicts with 'role' and 'content'
            provider: 'ollama', 'openai', or 'anthropic'
            model: Model name (uses default if None)

        Yields:
            Response chunks as they arrive
        """
        # Set default models if not specified
        if model is None:
            if provider == "ollama":
                model = settings.OLLAMA_LLM_MODEL
            elif provider == "openai":
                model = "gpt-4o-mini"
            elif provider == "anthropic":
                model = "claude-3-5-sonnet-20241022"

        logger.info(f"Chat request - Provider: {provider}, Model: {model}")

        # Route to appropriate provider
        if provider == "ollama":
            async for chunk in self.chat_stream_ollama(messages, model):
                yield chunk
        elif provider == "openai":
            async for chunk in self.chat_stream_openai(messages, model):
                yield chunk
        elif provider == "anthropic":
            async for chunk in self.chat_stream_anthropic(messages, model):
                yield chunk
        else:
            yield f"\n\nError: Unknown provider '{provider}'"
