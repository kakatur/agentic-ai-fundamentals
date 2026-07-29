from collections import defaultdict

def reciprocal_rank_fusion(rankings, *, k=60, weights=None):
    if k<=0: raise ValueError("k must be positive")
    weights=weights or [1.0]*len(rankings)
    if len(weights)!=len(rankings) or any(w<0 for w in weights): raise ValueError("weights must align and be nonnegative")
    scores=defaultdict(float)
    for ranking,weight in zip(rankings,weights):
        for rank,doc_id in enumerate(ranking,start=1): scores[doc_id]+=weight/(k+rank)
    return sorted(scores.items(),key=lambda item:(-item[1],item[0]))

def hybrid_search(dense_ids, lexical_ids, eligible_ids, *, weights=(1.0,1.0), k=60):
    eligible=set(eligible_ids)
    branches=[[doc for doc in ranking if doc in eligible] for ranking in (dense_ids,lexical_ids)]
    return reciprocal_rank_fusion(branches,k=k,weights=list(weights))
