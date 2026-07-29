from dataclasses import dataclass

@dataclass(frozen=True)
class Workload:
    vectors:int; dimension:int; queries_per_second:float; writes_per_second:float
    filtered_fraction:float; tenants:int; freshness_seconds:float

@dataclass(frozen=True)
class Result:
    name:str; recall:float; p95_ms:float; freshness_seconds:float; monthly_cost:float

def evaluate(workload, result, *, min_recall, max_p95_ms, max_cost):
    checks={"recall":result.recall>=min_recall,"latency":result.p95_ms<=max_p95_ms,"freshness":result.freshness_seconds<=workload.freshness_seconds,"cost":result.monthly_cost<=max_cost}
    return checks, all(checks.values())

def comparable_scenarios(base):
    return {"expected":base,"growth_3x":Workload(base.vectors*3,base.dimension,base.queries_per_second*3,base.writes_per_second*3,base.filtered_fraction,base.tenants*2,base.freshness_seconds)}
