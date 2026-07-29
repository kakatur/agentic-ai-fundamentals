from evaluation import Workload, Result, evaluate
w=Workload(1_000_000,768,100,10,0.7,50,5)
for r in [Result("candidate-a",.96,80,2,900),Result("candidate-b",.98,120,1,700)]: print(r.name,evaluate(w,r,min_recall=.95,max_p95_ms=100,max_cost=1000))
