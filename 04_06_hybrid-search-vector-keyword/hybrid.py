"""Rank fusion for already-filtered retrieval result lists."""


def reciprocal_rank_fusion(rankings, *, rank_constant=10, weights=None):
    """Fuse ordered document-ID lists using reciprocal rank fusion.

    Ranks are one-based. Repeated IDs within one list contribute only their
    first rank. If weights are omitted, each ranking has weight 1.
    """
    if rank_constant < 0:
        raise ValueError("rank_constant must be nonnegative")
    if weights is None:
        weights = [1.0] * len(rankings)
    if len(weights) != len(rankings):
        raise ValueError("provide exactly one weight per ranking")
    if any(weight <= 0 for weight in weights):
        raise ValueError("weights must be positive")

    scores = {}
    for ranking, weight in zip(rankings, weights):
        seen = set()
        for rank, document_id in enumerate(ranking, start=1):
            if document_id in seen:
                continue
            seen.add(document_id)
            scores[document_id] = scores.get(document_id, 0.0) + weight / (rank_constant + rank)
    return sorted(scores.items(), key=lambda item: (-item[1], item[0]))
