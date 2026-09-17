from collections import defaultdict
from collections.abc import Sequence


def reciprocal_rank_fusion(rankings: Sequence[Sequence[str]], *, k: int = 60, weights: Sequence[float] | None = None):
    if k <= 0:
        raise ValueError("k must be positive")
    branch_weights = list(weights) if weights is not None else [1.0] * len(rankings)
    if len(branch_weights) != len(rankings) or any(weight < 0 for weight in branch_weights):
        raise ValueError("weights must align with rankings and be nonnegative")

    scores = defaultdict(float)
    for ranking, weight in zip(rankings, branch_weights):
        for rank, document_id in enumerate(ranking, start=1):
            scores[document_id] += weight / (k + rank)
    return sorted(scores.items(), key=lambda item: (-item[1], item[0]))


def hybrid_search(dense_ids, lexical_ids, eligible_ids, *, weights=(1.0, 1.0), k=60):
    eligible = set(eligible_ids)
    branches = [[document_id for document_id in ranking if document_id in eligible] for ranking in (dense_ids, lexical_ids)]
    return reciprocal_rank_fusion(branches, k=k, weights=weights)
