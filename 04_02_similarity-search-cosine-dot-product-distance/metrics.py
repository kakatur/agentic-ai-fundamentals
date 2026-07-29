from __future__ import annotations
import math

def _check(a, b):
    if len(a) != len(b) or not a: raise ValueError("vectors need equal nonzero dimension")

def dot_product(a, b):
    _check(a, b)
    return sum(x*y for x, y in zip(a, b))

def cosine_similarity(a, b):
    product = dot_product(a, b)
    norms = math.sqrt(sum(x*x for x in a)) * math.sqrt(sum(y*y for y in b))
    return 0.0 if norms == 0 else product / norms

def euclidean_distance(a, b):
    _check(a, b)
    return math.sqrt(sum((x-y)**2 for x, y in zip(a, b)))

def rank(query, items, metric):
    reverse = metric != "euclidean"
    fn = {"cosine": cosine_similarity, "dot": dot_product, "euclidean": euclidean_distance}[metric]
    return sorted(((name, fn(query, vector)) for name, vector in items.items()), key=lambda x:x[1], reverse=reverse)
