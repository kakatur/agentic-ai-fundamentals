from evaluation import Result, Workload, evaluate, growth_scenario


workload = Workload(1_000_000, 768, 100, 10, 0.7, 50, 5)
results = [
    Result("candidate-a", 0.96, 80, 2, 900),
    Result("candidate-b", 0.98, 120, 1, 700),
]
for result in results:
    print(result.name, evaluate(result, workload, min_recall=0.95, max_p95_ms=100, max_cost=1000))
print("growth vectors:", growth_scenario(workload).vectors)
