"""
Token Counter - Accurate token counting for multiple LLM providers

This module demonstrates local token estimation and provider token-counting APIs.

For exact production counts, use the provider's token-counting endpoint with the
complete request, including instructions, tools, images, and other input items.
"""

import tiktoken
from typing import List, Dict, Any

try:
    from anthropic import Anthropic
except ImportError:  # Anthropic support is optional.
    Anthropic = None


class TokenCounter:
    """Universal token counter supporting multiple providers."""

    def __init__(self):
        self.anthropic_client = None
        self._encoding_cache = {}

    def get_openai_encoding(self, model: str):
        """Return a local tiktoken encoding, or None when none is cached."""
        if model in self._encoding_cache:
            return self._encoding_cache[model]

        try:
            encoding = tiktoken.encoding_for_model(model)
            self._encoding_cache[model] = encoding
            return encoding
        except (KeyError, OSError):
            pass

        for encoding_name in ("o200k_base", "cl100k_base"):
            try:
                encoding = tiktoken.get_encoding(encoding_name)
                self._encoding_cache[model] = encoding
                return encoding
            except Exception:
                continue

        self._encoding_cache[model] = None
        return None

    def count_openai_tokens(
        self,
        text: str,
        model: str = "gpt-5.4-mini"
    ) -> int:
        """
        Count tokens for OpenAI models using tiktoken.

        Args:
            text: The text to count tokens for
            model: The OpenAI model name

        Returns:
            Number of tokens
        """
        encoding = self.get_openai_encoding(model)
        if encoding is None:
            return max(1, len(text) // 4) if text else 0

        tokens = encoding.encode(text)
        return len(tokens)

    def count_anthropic_tokens(
        self,
        text: str,
        model: str = "claude-sonnet-4-6"
    ) -> int:
        """
        Count tokens for Anthropic models.

        Anthropic exposes token counting through messages.count_tokens().
        A local character estimate is used when the optional SDK or credentials
        are unavailable.

        Args:
            text: The text to count tokens for
            model: The Anthropic model name

        Returns:
            Number of tokens
        """
        if Anthropic is None:
            return self._estimate_anthropic_tokens(text)

        if self.anthropic_client is None:
            # Initialize only if needed (requires API key)
            try:
                self.anthropic_client = Anthropic()
            except Exception:
                # Fallback to estimation if no API key
                return self._estimate_anthropic_tokens(text)

        try:
            # Anthropic provides a token counting API
            response = self.anthropic_client.messages.count_tokens(
                model=model,
                messages=[{"role": "user", "content": text}],
            )
            return response.input_tokens
        except Exception:
            # Fallback to estimation
            return self._estimate_anthropic_tokens(text)

    def _estimate_anthropic_tokens(self, text: str) -> int:
        """
        Rough estimation for Anthropic tokens.

        This is deliberately labeled an estimate and must not be used to enforce
        a hard production context limit.
        """
        # Rough estimate: ~4 characters per token
        return len(text) // 4

    def count_messages_tokens(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-5.4-mini",
        provider: str = "openai"
    ) -> int:
        """
        Count tokens for a list of messages (chat format).

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name
            provider: "openai" or "anthropic"

        Returns:
            Total token count including message formatting overhead
        """
        if provider == "openai":
            return self._count_openai_messages(messages, model)
        elif provider == "anthropic":
            return self._count_anthropic_messages(messages, model)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _count_openai_messages(
        self,
        messages: List[Dict[str, str]],
        model: str
    ) -> int:
        """
        Count tokens for OpenAI chat messages.

        This is a local estimate for text-only Chat Completions-style messages.
        Exact overhead varies by model and request shape.
        """
        encoding = self.get_openai_encoding(model)
        if encoding is None:
            content_estimate = sum(
                max(1, len(str(value)) // 4)
                for message in messages
                for value in message.values()
            )
            return content_estimate + (3 * len(messages)) + 3

        tokens_per_message = 3  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = 1  # if there's a name, the role is omitted

        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(str(value)))
                if key == "name":
                    num_tokens += tokens_per_name

        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens

    def _count_anthropic_messages(
        self,
        messages: List[Dict[str, str]],
        model: str
    ) -> int:
        """
        Count tokens for Anthropic chat messages.

        Use Anthropic's token-counting API for exact request counts. This method
        remains offline-friendly for the lesson demos.
        """
        # Simple approximation: count all content + small overhead per message
        total_tokens = 0
        for message in messages:
            content = message.get("content", "")
            total_tokens += self.count_anthropic_tokens(content, model)
            total_tokens += 2  # small overhead per message

        return total_tokens

    def count_with_buffer(
        self,
        text: str,
        model: str,
        provider: str = "openai",
        buffer_pct: float = 0.1
    ) -> int:
        """
        Count tokens with a safety buffer.

        Always add a buffer (5-10%) because:
        1. Token counting can have small variations
        2. Better to be conservative than hit the limit

        Args:
            text: Text to count
            model: Model name
            provider: "openai" or "anthropic"
            buffer_pct: Buffer percentage (0.1 = 10% buffer)

        Returns:
            Token count with buffer added
        """
        if provider == "openai":
            base_count = self.count_openai_tokens(text, model)
        else:
            base_count = self.count_anthropic_tokens(text, model)

        buffered_count = int(base_count * (1 + buffer_pct))
        return buffered_count


# Convenience functions
def count_tokens(
    text: str,
    model: str = "gpt-5.4-mini",
    provider: str = "openai"
) -> int:
    """
    Quick token counting function.

    Example:
        tokens = count_tokens("Hello world", model="gpt-5.4-mini")
    """
    counter = TokenCounter()
    if provider == "openai":
        return counter.count_openai_tokens(text, model)
    else:
        return counter.count_anthropic_tokens(text, model)


def estimate_page_tokens(num_pages: int) -> int:
    """
    Estimate tokens for a number of pages.

    Rule of thumb: ~400-500 tokens per page
    """
    return num_pages * 450


# Example usage and testing
if __name__ == "__main__":
    counter = TokenCounter()

    # Test 1: Simple text
    text = "Hello, how are you doing today?"
    print(f"Text: {text}")
    print(f"OpenAI tokens: {counter.count_openai_tokens(text, 'gpt-5.4-mini')}")
    print(f"Anthropic tokens: {counter.count_anthropic_tokens(text)}")
    print()

    # Test 2: Longer text
    long_text = """
    Artificial intelligence and machine learning have revolutionized the way we build software.
    Large language models like GPT-4 and Claude can understand and generate human-like text,
    enabling applications like chatbots, content generation, and code assistance.
    However, these models have limitations, including context windows and token budgets.
    """
    print(f"Long text tokens (OpenAI): {counter.count_openai_tokens(long_text, 'gpt-5.4-mini')}")
    print(f"Long text tokens (Anthropic): {counter.count_anthropic_tokens(long_text)}")
    print()

    # Test 3: Chat messages
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"},
        {"role": "assistant", "content": "The capital of France is Paris."},
        {"role": "user", "content": "What about Germany?"}
    ]
    print(f"Chat messages tokens: {counter.count_messages_tokens(messages, 'gpt-5.4-mini', 'openai')}")
    print()

    # Test 4: Token counting with buffer
    print(f"Tokens with 10% buffer: {counter.count_with_buffer(long_text, 'gpt-5.4-mini', 'openai', 0.1)}")
    print()

    # Test 5: Page estimation
    print(f"Estimated tokens for 100 pages: {estimate_page_tokens(100)}")

    # Test 6: Compare encodings used by two model generations
    sample_text = "The quick brown fox jumps over the lazy dog."
    print(f"\nToken comparison for: {sample_text}")
    print(f"GPT-4o mini: {counter.count_openai_tokens(sample_text, 'gpt-4o-mini')}")
    print(f"GPT-5.4 mini: {counter.count_openai_tokens(sample_text, 'gpt-5.4-mini')}")

    # Test 7: Show character-to-token ratio
    char_count = len(long_text)
    token_count = counter.count_openai_tokens(long_text, 'gpt-5.4-mini')
    ratio = char_count / token_count
    print(f"\nCharacter-to-token ratio: {ratio:.2f} chars/token")
    print(f"This means roughly {1/ratio:.2f} tokens per character")
