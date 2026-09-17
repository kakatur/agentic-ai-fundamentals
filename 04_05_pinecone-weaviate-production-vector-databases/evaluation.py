from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Workload:
    vectors: int
    dimension: int
    queries_per_second: float
    writes_per_second: float
    filtered_fraction: float
    tenants: int
    freshness_seconds: float


@dataclass(frozen=True)
class Result:
    name: str
    recall_at_k: float
    p95_ms: float
    freshness_seconds: float
    monthly_cost: float


def evaluate(result: Result, workload: Workload, *, min_recall: float, max_p95_ms: float, max_cost: float):
    checks = {
        "recall": result.recall_at_k >= min_recall,
        "latency": result.p95_ms <= max_p95_ms,
        "freshness": result.freshness_seconds <= workload.freshness_seconds,
        "cost": result.monthly_cost <= max_cost,
    }
    return checks, all(checks.values())


def growth_scenario(workload: Workload, factor: int = 3) -> Workload:
    if factor <= 0:
        raise ValueError("factor must be positive")
    return replace(
        workload,
        vectors=workload.vectors * factor,
        queries_per_second=workload.queries_per_second * factor,
        writes_per_second=workload.writes_per_second * factor,
    )
