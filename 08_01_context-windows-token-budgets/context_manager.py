"""
Context Manager - Smart context window management with sliding windows

This module handles conversation history truncation, sliding windows,
and intelligent context preservation to stay within token limits.
"""

import json
from typing import List, Dict, Any, Optional
from token_counter import TokenCounter


class ContextManager:
    """
    Manages context windows and ensures total tokens stay within limits.

    Features:
    - Sliding window for conversation history
    - Prioritized message retention
    - Smart truncation
    - Token budget enforcement
    """

    def __init__(
        self,
        model: str = "gpt-5.4-mini",
        provider: str = "openai",
        context_limit: int = 400_000
    ):
        self.model = model
        self.provider = provider
        self.context_limit = context_limit
        self.counter = TokenCounter()

    def count_tokens(self, text: str) -> int:
        """Count tokens for the configured model."""
        if self.provider == "openai":
            return self.counter.count_openai_tokens(text, self.model)
        elif self.provider == "anthropic":
            return self.counter.count_anthropic_tokens(text, self.model)
        raise ValueError(f"Unsupported provider: {self.provider}")

    def count_message_tokens(self, message: Dict[str, str]) -> int:
        """Count tokens for a single message."""
        content = message.get("content", "")
        # Add overhead for role and formatting
        return self.count_tokens(content) + 4

    def count_messages_tokens(self, messages: List[Dict[str, str]]) -> int:
        """Count tokens for a list of messages."""
        return self.counter.count_messages_tokens(
            messages,
            self.model,
            self.provider
        )

    def truncate_history_simple(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int
    ) -> List[Dict[str, str]]:
        """
        Simple sliding window: keep most recent messages that fit.

        Args:
            messages: Full conversation history
            max_tokens: Maximum tokens allowed for history

        Returns:
            Truncated message list
        """
        if not messages:
            return []

        # Always keep the first message (often important context)
        first_message = messages[0]
        remaining_messages = messages[1:]

        # Start from the end and work backwards
        truncated = []
        current_tokens = self.count_message_tokens(first_message)
        if current_tokens > max_tokens:
            return []

        for message in reversed(remaining_messages):
            message_tokens = self.count_message_tokens(message)
            if current_tokens + message_tokens <= max_tokens:
                truncated.insert(0, message)
                current_tokens += message_tokens
            else:
                break

        # Add back the first message
        return [first_message] + truncated

    def truncate_history_preserve_pairs(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int
    ) -> List[Dict[str, str]]:
        """
        Preserve user-assistant message pairs.

        Important: Don't break conversation turns - always keep Q&A together.

        Args:
            messages: Full conversation history
            max_tokens: Maximum tokens allowed for history

        Returns:
            Truncated message list with preserved pairs
        """
        if not messages:
            return []

        # Separate system messages from conversation
        system_messages = [m for m in messages if m["role"] == "system"]
        conversation = [m for m in messages if m["role"] != "system"]

        # Count system tokens
        system_tokens = sum(self.count_message_tokens(m) for m in system_messages)
        available_tokens = max_tokens - system_tokens

        if available_tokens <= 0:
            # If system messages exceed budget, return only system
            return system_messages

        # Group into pairs (user + assistant)
        pairs = []
        i = 0
        while i < len(conversation):
            if i + 1 < len(conversation):
                # We have a pair
                pair = [conversation[i], conversation[i + 1]]
                pair_tokens = sum(self.count_message_tokens(m) for m in pair)
                pairs.append((pair, pair_tokens))
                i += 2
            else:
                # Odd message at the end (usually the current user message)
                pair = [conversation[i]]
                pair_tokens = self.count_message_tokens(conversation[i])
                pairs.append((pair, pair_tokens))
                i += 1

        # Keep most recent pairs that fit
        selected_pairs = []
        current_tokens = 0

        for pair, pair_tokens in reversed(pairs):
            if current_tokens + pair_tokens <= available_tokens:
                selected_pairs.insert(0, pair)
                current_tokens += pair_tokens
            else:
                break

        # Flatten pairs
        conversation_history = [msg for pair in selected_pairs for msg in pair]

        return system_messages + conversation_history

    def truncate_history_selective(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        keep_first_n: int = 2,
        keep_last_n: int = 4
    ) -> List[Dict[str, str]]:
        """
        Selective retention: keep first N and last N messages, drop middle.

        This is useful when:
        - First messages contain important context (user goal, constraints)
        - Recent messages are most relevant
        - Middle messages are less critical

        Args:
            messages: Full conversation history
            max_tokens: Maximum tokens allowed
            keep_first_n: Number of messages to keep from start
            keep_last_n: Number of messages to keep from end

        Returns:
            Truncated message list
        """
        if not messages:
            return []

        if len(messages) <= keep_first_n + keep_last_n:
            # If total messages fit within keep limits, check if they fit token budget
            total_tokens = self.count_messages_tokens(messages)
            if total_tokens <= max_tokens:
                return messages
            else:
                # Use simple truncation
                return self.truncate_history_simple(messages, max_tokens)

        # Split into first, middle, last
        first_messages = messages[:keep_first_n]
        last_messages = messages[-keep_last_n:]

        # Count tokens
        first_tokens = self.count_messages_tokens(first_messages)
        last_tokens = self.count_messages_tokens(last_messages)
        total_tokens = first_tokens + last_tokens

        if total_tokens <= max_tokens:
            return first_messages + last_messages
        else:
            # Even first+last exceed budget, truncate last only
            available_for_last = max_tokens - first_tokens
            truncated_last = self.truncate_history_simple(
                last_messages,
                available_for_last
            )
            return first_messages + truncated_last

    def calculate_available_history_budget(
        self,
        system_prompt: str,
        tools: List[Dict[str, Any]],
        retrieval_docs: List[str],
        current_message: str = "",
        response_budget: int = 2000
    ) -> int:
        """
        Calculate how many tokens are available for conversation history.

        Args:
            system_prompt: The system prompt text
            tools: Tool/function definitions
            retrieval_docs: Retrieved documents
            current_message: Current user input, which must always fit
            response_budget: Tokens reserved for the model's response

        Returns:
            Available token budget for history
        """
        system_tokens = self.count_tokens(system_prompt)

        # Count tool tokens (rough estimate)
        tools_text = json.dumps(tools, sort_keys=True, separators=(",", ":"))
        tools_tokens = self.count_tokens(tools_text)

        # Count retrieval tokens
        retrieval_text = self._format_retrieval_context(retrieval_docs) if retrieval_docs else ""
        retrieval_tokens = self.count_tokens(retrieval_text)
        current_message_tokens = self.count_message_tokens(
            {"role": "user", "content": current_message}
        )

        used_tokens = (
            system_tokens +
            tools_tokens +
            retrieval_tokens +
            current_message_tokens +
            response_budget
        )

        available = self.context_limit - used_tokens

        # Always leave a buffer
        buffer = int(self.context_limit * 0.05)  # 5% buffer
        available = max(0, available - buffer)

        return available

    def build_request(
        self,
        system_prompt: str,
        conversation_history: List[Dict[str, str]],
        current_message: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        retrieval_docs: Optional[List[str]] = None,
        response_budget: int = 2000
    ) -> Dict[str, Any]:
        """
        Build a complete API request that fits within context limits.

        This is the main method - it orchestrates all truncation logic.

        Args:
            system_prompt: System prompt
            conversation_history: Full conversation history
            current_message: Current user message
            tools: Optional tool definitions
            retrieval_docs: Optional retrieved documents
            response_budget: Tokens reserved for response

        Returns:
            Dict with 'messages' and 'metadata' about token usage
        """
        tools = tools or []
        retrieval_docs = retrieval_docs or []

        # Calculate available budget for history
        history_budget = self.calculate_available_history_budget(
            system_prompt,
            tools,
            retrieval_docs,
            current_message,
            response_budget
        )

        # Truncate history to fit budget
        history_without_system_messages = [
            message for message in conversation_history
            if message.get("role") != "system"
        ]
        truncated_history = self.truncate_history_preserve_pairs(
            history_without_system_messages,
            history_budget
        )

        # Build messages list
        messages = []

        # Add system prompt
        messages.append({"role": "system", "content": system_prompt})

        # Add retrieval context (if any)
        if retrieval_docs:
            retrieval_context = self._format_retrieval_context(retrieval_docs)
            messages.append({"role": "system", "content": retrieval_context})

        # Add conversation history
        messages.extend(truncated_history)

        # Add current user message
        messages.append({"role": "user", "content": current_message})

        # Calculate actual token usage
        actual_tokens = self.count_messages_tokens(messages)
        tools_tokens = self.count_tokens(
            json.dumps(tools, sort_keys=True, separators=(",", ":"))
        ) if tools else 0
        total_input_tokens = actual_tokens + tools_tokens
        reserved_total = total_input_tokens + response_budget
        if reserved_total > self.context_limit:
            raise ValueError(
                "Request plus reserved response exceeds context limit: "
                f"{reserved_total:,} > {self.context_limit:,}"
            )

        metadata = {
            "total_input_tokens": total_input_tokens,
            "history_tokens": self.count_messages_tokens(truncated_history),
            "system_tokens": self.count_tokens(system_prompt),
            "retrieval_tokens": self.count_tokens(
                self._format_retrieval_context(retrieval_docs)
            ) if retrieval_docs else 0,
            "current_message_tokens": self.count_message_tokens(
                {"role": "user", "content": current_message}
            ),
            "tools_tokens": tools_tokens,
            "response_budget": response_budget,
            "context_limit": self.context_limit,
            "reserved_total_tokens": reserved_total,
            "utilization_pct": (reserved_total / self.context_limit) * 100,
            "messages_kept": len(truncated_history),
            "messages_dropped": len(history_without_system_messages) - len(truncated_history)
        }

        return {
            "messages": messages,
            "tools": tools,
            "metadata": metadata
        }

    def _format_retrieval_context(self, docs: List[str]) -> str:
        """Format retrieved documents for injection into context."""
        formatted = "# Retrieved Context\n\n"
        for i, doc in enumerate(docs, 1):
            formatted += f"## Document {i}\n{doc}\n\n"
        return formatted


# Example usage
if __name__ == "__main__":
    # Initialize manager
    manager = ContextManager(
        model="gpt-5.4-mini",
        provider="openai",
        context_limit=16_384
    )

    # Simulate a long conversation
    conversation_history = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is Python?"},
        {"role": "assistant", "content": "Python is a high-level programming language..."},
        {"role": "user", "content": "What about JavaScript?"},
        {"role": "assistant", "content": "JavaScript is a scripting language..."},
        {"role": "user", "content": "Which one should I learn first?"},
        {"role": "assistant", "content": "It depends on your goals..."},
        {"role": "user", "content": "I want to build web applications."},
        {"role": "assistant", "content": "For web applications, I'd recommend..."},
    ]

    # Add more messages to exceed context
    for i in range(10):
        conversation_history.append({
            "role": "user",
            "content": f"Question {i}: Tell me more about topic {i}?"
        })
        conversation_history.append({
            "role": "assistant",
            "content": f"Answer {i}: Here is detailed information about topic {i}..." * 50
        })

    system_prompt = "You are a helpful coding assistant."
    current_message = "What's the best way to learn programming?"
    retrieval_docs = [
        "Programming requires practice and patience...",
        "Start with fundamentals before advanced topics...",
        "Build projects to reinforce learning..."
    ]

    # Build request that fits context
    result = manager.build_request(
        system_prompt=system_prompt,
        conversation_history=conversation_history,
        current_message=current_message,
        retrieval_docs=retrieval_docs,
        response_budget=2000
    )

    print("Context Management Results:")
    print("-" * 50)
    print(f"Total input tokens: {result['metadata']['total_input_tokens']}")
    print(f"Context limit: {result['metadata']['context_limit']}")
    print(f"Utilization: {result['metadata']['utilization_pct']:.1f}%")
    print(f"Messages kept: {result['metadata']['messages_kept']}")
    print(f"Messages dropped: {result['metadata']['messages_dropped']}")
    print()
    print("Token breakdown:")
    print(f"  System: {result['metadata']['system_tokens']}")
    print(f"  History: {result['metadata']['history_tokens']}")
    print(f"  Retrieval: {result['metadata']['retrieval_tokens']}")
    print(f"  Tools: {result['metadata']['tools_tokens']}")
    print(f"  Response budget: {result['metadata']['response_budget']}")

    # Test different truncation strategies
    print("\n" + "=" * 50)
    print("Comparing Truncation Strategies")
    print("=" * 50)

    # Strategy 1: Simple sliding window
    truncated_simple = manager.truncate_history_simple(conversation_history, 2000)
    print(f"\nSimple sliding window: {len(truncated_simple)} messages kept")

    # Strategy 2: Preserve pairs
    truncated_pairs = manager.truncate_history_preserve_pairs(conversation_history, 2000)
    print(f"Preserve pairs: {len(truncated_pairs)} messages kept")

    # Strategy 3: Selective (keep first and last)
    truncated_selective = manager.truncate_history_selective(
        conversation_history,
        2000,
        keep_first_n=2,
        keep_last_n=4
    )
    print(f"Selective (first 2 + last 4): {len(truncated_selective)} messages kept")
