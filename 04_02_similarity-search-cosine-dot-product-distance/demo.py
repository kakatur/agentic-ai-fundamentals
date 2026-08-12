from metrics import rank


query = [1.0, 0.0]
candidates = {
    "same direction, longer": [4.0, 0.0],
    "nearby endpoint": [0.8, 0.2],
    "opposite direction": [-1.0, 0.0],
}

for metric_name in ("cosine", "dot", "euclidean"):
    print(f"\n{metric_name}")
    for name, score in rank(query, candidates, metric_name):
        print(f"  {score:+.3f}  {name}")
