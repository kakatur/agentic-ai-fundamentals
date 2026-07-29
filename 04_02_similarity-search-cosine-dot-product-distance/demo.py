from metrics import rank
query=[1.0,0.0]
items={"same direction, large":[4.0,0.0],"nearby":[0.8,0.2],"opposite":[-1.0,0.0]}
for metric in ("cosine","dot","euclidean"):
    print(metric, rank(query,items,metric))
