"""
Retrieval Truncation - Smart document truncation strategies

This module implements intelligent strategies for truncating retrieved documents
to fit within token budgets while preserving the most relevant information.
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass
from token_counter import TokenCounter


@dataclass
class RetrievalResult:
    """Represents a retrieved document with metadata."""
    content: str
    score: float  # Relevance score (0-1)
    source: str
    tokens: int


class RetrievalTruncator:
    """
    Handles intelligent truncation of retrieved documents.

    Strategies:
    1. Top-N selection (keep most relevant)
    2. Proportional truncation (trim all proportionally)
    3. Greedy selection (pack highest value documents)
    4. Position-aware (avoid lost-in-middle problem)
    """

    def __init__(self, model: str = "gpt-5.4-mini", provider: str = "openai"):
        self.model = model
        self.provider = provider
        self.counter = TokenCounter()

    def count_tokens(self, text: str) -> int:
        """Count tokens for text."""
        if self.provider == "openai":
            return self.counter.count_openai_tokens(text, self.model)
        elif self.provider == "anthropic":
            return self.counter.count_anthropic_tokens(text, self.model)
        raise ValueError(f"Unsupported provider: {self.provider}")

    def prepare_retrieval_results(
        self,
        documents: List[Dict[str, any]]
    ) -> List[RetrievalResult]:
        """
        Convert raw documents to RetrievalResult objects.

        Args:
            documents: List of dicts with 'content', 'score', 'source'

        Returns:
            List of RetrievalResult objects
        """
        results = []
        for doc in documents:
            content = doc["content"]
            tokens = self.count_tokens(content)
            results.append(RetrievalResult(
                content=content,
                score=doc.get("score", 1.0),
                source=doc.get("source", "unknown"),
                tokens=tokens
            ))
        return results

    def truncate_top_n(
        self,
        results: List[RetrievalResult],
        max_tokens: int
    ) -> Tuple[List[RetrievalResult], int]:
        """
        Keep top N most relevant documents that fit within budget.

        Strategy: Greedy selection by relevance score.
        Best when: You want only the highest quality documents.

        Args:
            results: List of retrieval results
            max_tokens: Maximum tokens allowed

        Returns:
            Tuple of (selected results, total tokens used)
        """
        # Sort by score descending
        sorted_results = sorted(results, key=lambda x: x.score, reverse=True)

        selected = []
        total_tokens = 0

        for result in sorted_results:
            if total_tokens + result.tokens <= max_tokens:
                selected.append(result)
                total_tokens += result.tokens
            else:
                continue

        return selected, total_tokens

    def truncate_proportional(
        self,
        results: List[RetrievalResult],
        max_tokens: int
    ) -> Tuple[List[RetrievalResult], int]:
        """
        Truncate all documents proportionally to fit budget.

        Strategy: Keep all documents but trim each to fit budget.
        Best when: You want representation from all retrieved docs.

        Args:
            results: List of retrieval results
            max_tokens: Maximum tokens allowed

        Returns:
            Tuple of (truncated results, total tokens used)
        """
        if not results:
            return [], 0

        # Calculate total tokens needed
        total_tokens_needed = sum(r.tokens for r in results)

        if total_tokens_needed <= max_tokens:
            # All docs fit, no truncation needed
            return results, total_tokens_needed

        # Calculate proportional allocation
        allocation_ratio = max_tokens / total_tokens_needed

        truncated = []
        total_tokens = 0

        for result in results:
            # Allocate tokens proportionally
            allocated_tokens = int(result.tokens * allocation_ratio)

            # Truncate content
            truncated_content = self._truncate_text_to_tokens(
                result.content,
                allocated_tokens
            )

            actual_tokens = self.count_tokens(truncated_content)
            truncated_result = RetrievalResult(
                content=truncated_content,
                score=result.score,
                source=result.source,
                tokens=actual_tokens
            )

            truncated.append(truncated_result)
            total_tokens += actual_tokens

        return truncated, total_tokens

    def truncate_position_aware(
        self,
        results: List[RetrievalResult],
        max_tokens: int
    ) -> Tuple[List[RetrievalResult], int]:
        """
        Position-aware truncation to avoid "lost in the middle" problem.

        Strategy:
        - Place most relevant docs at the END (nearest to query)
        - Place medium relevant docs at the START
        - Skip or truncate least relevant docs

        Best when: Context size is large and you want to maximize utilization.

        Args:
            results: List of retrieval results
            max_tokens: Maximum tokens allowed

        Returns:
            Tuple of (positioned results, total tokens used)
        """
        selected, total_tokens = self.truncate_top_n(results, max_tokens)

        # Highest-relevance item is nearest the user query when the caller
        # inserts this list immediately before that query.
        positioned = sorted(selected, key=lambda item: item.score)
        return positioned, total_tokens

    def truncate_diverse(
        self,
        results: List[RetrievalResult],
        max_tokens: int,
        diversity_threshold: float = 0.3
    ) -> Tuple[List[RetrievalResult], int]:
        """
        Select diverse documents to avoid redundancy.

        Strategy: Use Maximal Marginal Relevance (MMR) approach.
        Best when: Retrieved docs have high overlap/redundancy.

        Note: This is a simplified version. Production systems would
        use actual embeddings and cosine similarity for diversity calculation.

        Args:
            results: List of retrieval results
            max_tokens: Maximum tokens allowed
            diversity_threshold: Minimum diversity score required

        Returns:
            Tuple of (diverse results, total tokens used)
        """
        if not results:
            return [], 0

        # Start with the most relevant document
        sorted_results = sorted(results, key=lambda x: x.score, reverse=True)
        selected = []
        total_tokens = 0
        if sorted_results[0].tokens <= max_tokens:
            selected.append(sorted_results[0])
            total_tokens = sorted_results[0].tokens
        remaining = sorted_results[1:]

        while remaining and total_tokens < max_tokens:
            # Find the document that is both relevant and diverse
            best_doc = None
            best_score = -1

            for candidate in remaining:
                if total_tokens + candidate.tokens > max_tokens:
                    continue

                # Simplified diversity: character-level overlap
                diversity_score = self._calculate_diversity(
                    candidate,
                    selected
                )

                # Combine relevance and diversity
                # MMR formula: λ * relevance - (1-λ) * similarity
                lambda_param = 0.7  # Weight for relevance vs diversity
                mmr_score = (
                    lambda_param * candidate.score -
                    (1 - lambda_param) * (1 - diversity_score)
                )

                if mmr_score > best_score:
                    best_score = mmr_score
                    best_doc = candidate

            if best_doc is None:
                break

            selected.append(best_doc)
            total_tokens += best_doc.tokens
            remaining.remove(best_doc)

        return selected, total_tokens

    def _calculate_diversity(
        self,
        candidate: RetrievalResult,
        selected: List[RetrievalResult]
    ) -> float:
        """
        Calculate diversity score (simplified).

        In production, use actual embeddings and cosine distance.
        Here we use character-level Jaccard similarity as proxy.

        Args:
            candidate: Candidate document
            selected: Already selected documents

        Returns:
            Diversity score (0-1, higher is more diverse)
        """
        if not selected:
            return 1.0

        # Calculate average similarity to selected docs
        similarities = []
        candidate_chars = set(candidate.content.lower())

        for doc in selected:
            doc_chars = set(doc.content.lower())
            intersection = len(candidate_chars & doc_chars)
            union = len(candidate_chars | doc_chars)
            jaccard = intersection / union if union > 0 else 0
            similarities.append(jaccard)

        avg_similarity = sum(similarities) / len(similarities)
        diversity = 1 - avg_similarity

        return diversity

    def _truncate_text_to_tokens(
        self,
        text: str,
        max_tokens: int
    ) -> str:
        """
        Truncate text to fit within token limit.

        Strategy: Take the first max_tokens worth of content.
        Could be improved by taking first + last, or most relevant sentences.

        Args:
            text: Text to truncate
            max_tokens: Maximum tokens allowed

        Returns:
            Truncated text
        """
        if max_tokens <= 0:
            return ""

        if self.provider == "openai":
            encoding = self.counter.get_openai_encoding(self.model)
            if encoding is not None:
                tokens = encoding.encode(text)
                if len(tokens) <= max_tokens:
                    return text
                return encoding.decode(tokens[:max_tokens])

            current_tokens = self.count_tokens(text)
            if current_tokens <= max_tokens:
                return text
            char_pos = int(len(text) * (max_tokens / current_tokens))
            return text[:char_pos]
        else:
            # Similar logic for Anthropic
            current_tokens = self.count_tokens(text)
            if current_tokens <= max_tokens:
                return text

            char_ratio = max_tokens / current_tokens
            char_pos = int(len(text) * char_ratio)
            truncated = text[:char_pos] + "..."

            return truncated

    def format_for_context(
        self,
        results: List[RetrievalResult],
        include_scores: bool = False,
        include_sources: bool = True
    ) -> str:
        """
        Format retrieval results for injection into LLM context.

        Args:
            results: List of retrieval results
            include_scores: Whether to include relevance scores
            include_sources: Whether to include source attribution

        Returns:
            Formatted string ready for context injection
        """
        if not results:
            return ""

        formatted_parts = ["# Retrieved Context\n"]

        for i, result in enumerate(results, 1):
            formatted_parts.append(f"\n## Document {i}")

            if include_sources:
                formatted_parts.append(f"**Source:** {result.source}")

            if include_scores:
                formatted_parts.append(f"**Relevance:** {result.score:.2f}")

            formatted_parts.append(f"\n{result.content}\n")

        return "\n".join(formatted_parts)


# Example usage
if __name__ == "__main__":
    print("Retrieval Truncation Demo")
    print("=" * 70)

    # Create sample documents
    sample_docs = [
        {
            "content": "Python is a high-level, interpreted programming language. " * 20,
            "score": 0.95,
            "source": "python_intro.md"
        },
        {
            "content": "JavaScript is a scripting language used for web development. " * 15,
            "score": 0.85,
            "source": "javascript_basics.md"
        },
        {
            "content": "TypeScript is a superset of JavaScript with static typing. " * 18,
            "score": 0.80,
            "source": "typescript_guide.md"
        },
        {
            "content": "Java is a statically-typed, object-oriented programming language. " * 25,
            "score": 0.70,
            "source": "java_overview.md"
        },
        {
            "content": "C++ is a powerful systems programming language. " * 22,
            "score": 0.65,
            "source": "cpp_reference.md"
        },
        {
            "content": "Go is a compiled language designed for concurrency. " * 12,
            "score": 0.60,
            "source": "go_tutorial.md"
        }
    ]

    # Initialize truncator
    truncator = RetrievalTruncator(model="gpt-5.4-mini", provider="openai")

    # Prepare results
    results = truncator.prepare_retrieval_results(sample_docs)

    # Calculate total tokens
    total_tokens = sum(r.tokens for r in results)
    print(f"Total documents: {len(results)}")
    print(f"Total tokens: {total_tokens:,}\n")

    # Token budget
    max_tokens = 1500

    print(f"Token Budget: {max_tokens:,} tokens")
    print("=" * 70)

    # Strategy 1: Top-N
    print("\n1. TOP-N STRATEGY")
    print("-" * 70)
    top_n_results, top_n_tokens = truncator.truncate_top_n(results, max_tokens)
    print(f"Documents selected: {len(top_n_results)}")
    print(f"Tokens used: {top_n_tokens:,} ({(top_n_tokens/max_tokens)*100:.1f}%)")
    print("Selected documents:")
    for r in top_n_results:
        print(f"  - {r.source} (score: {r.score:.2f}, {r.tokens} tokens)")

    # Strategy 2: Proportional
    print("\n2. PROPORTIONAL STRATEGY")
    print("-" * 70)
    prop_results, prop_tokens = truncator.truncate_proportional(results, max_tokens)
    print(f"Documents included: {len(prop_results)}")
    print(f"Tokens used: {prop_tokens:,} ({(prop_tokens/max_tokens)*100:.1f}%)")
    print("All documents (truncated):")
    for r in prop_results:
        print(f"  - {r.source} (score: {r.score:.2f}, {r.tokens} tokens)")

    # Strategy 3: Position-aware
    print("\n3. POSITION-AWARE STRATEGY")
    print("-" * 70)
    pos_results, pos_tokens = truncator.truncate_position_aware(results, max_tokens)
    print(f"Documents selected: {len(pos_results)}")
    print(f"Tokens used: {pos_tokens:,} ({(pos_tokens/max_tokens)*100:.1f}%)")
    print("Positioned documents:")
    for i, r in enumerate(pos_results, 1):
        position = "START" if i <= len(pos_results)//2 else "END"
        print(f"  {i}. {r.source} (score: {r.score:.2f}, {r.tokens} tokens) -> {position}")

    # Strategy 4: Diverse
    print("\n4. DIVERSE STRATEGY")
    print("-" * 70)
    diverse_results, diverse_tokens = truncator.truncate_diverse(results, max_tokens)
    print(f"Documents selected: {len(diverse_results)}")
    print(f"Tokens used: {diverse_tokens:,} ({(diverse_tokens/max_tokens)*100:.1f}%)")
    print("Diverse documents:")
    for r in diverse_results:
        print(f"  - {r.source} (score: {r.score:.2f}, {r.tokens} tokens)")

    # Format for context
    print("\n" + "=" * 70)
    print("FORMATTED CONTEXT (Position-Aware Strategy):")
    print("=" * 70)
    formatted = truncator.format_for_context(
        pos_results,
        include_scores=True,
        include_sources=True
    )
    print(formatted[:500] + "...\n")  # Show first 500 chars

    # Strategy comparison
    print("\n" + "=" * 70)
    print("STRATEGY COMPARISON")
    print("=" * 70)
    print(f"{'Strategy':<20} {'Docs':<8} {'Tokens':<12} {'Utilization':<12}")
    print("-" * 70)
    print(f"{'Top-N':<20} {len(top_n_results):<8} {top_n_tokens:<12} {(top_n_tokens/max_tokens)*100:.1f}%")
    print(f"{'Proportional':<20} {len(prop_results):<8} {prop_tokens:<12} {(prop_tokens/max_tokens)*100:.1f}%")
    print(f"{'Position-Aware':<20} {len(pos_results):<8} {pos_tokens:<12} {(pos_tokens/max_tokens)*100:.1f}%")
    print(f"{'Diverse':<20} {len(diverse_results):<8} {diverse_tokens:<12} {(diverse_tokens/max_tokens)*100:.1f}%")

    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)
    print("• Use TOP-N when: You want only the highest quality documents")
    print("• Use PROPORTIONAL when: You want all documents represented")
    print("• Use POSITION-AWARE when: Context size is large (>10K tokens)")
    print("• Use DIVERSE when: Retrieved docs have high redundancy")
