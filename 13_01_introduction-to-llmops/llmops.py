from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from time import perf_counter
from typing import Callable, Iterable, Literal
from uuid import uuid4


Intent = Literal["billing", "technical_support", "account_access"]
Severity = Literal["low", "normal", "high"]
ModelFn = Callable[[str], str]


@dataclass(frozen=True)
class EvalExample:
    id: str
    ticket: str
    expected_intent: Intent
    expected_severity: Severity
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class Prediction:
    intent: Intent
    severity: Severity
    answer: str


@dataclass(frozen=True)
class TraceRecord:
    trace_id: str
    example_id: str
    model_version: str
    prompt_version: str
    latency_ms: float
    prompt_tokens: int
    completion_tokens: int
    expected_intent: Intent
    actual_intent: Intent
    expected_severity: Severity
    actual_severity: Severity
    passed: bool
    tags: tuple[str, ...]


@dataclass(frozen=True)
class RiskCheck:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class ReleaseReport:
    model_version: str
    prompt_version: str
    accuracy: float
    high_severity_recall: float
    average_latency_ms: float
    average_tokens: float
    traces: tuple[TraceRecord, ...]
    risk_checks: tuple[RiskCheck, ...]
    promoted: bool


def golden_examples() -> tuple[EvalExample, ...]:
    return (
        EvalExample(
            id="billing-refund",
            ticket="I was charged twice and need a refund.",
            expected_intent="billing",
            expected_severity="high",
            tags=("money", "customer-impact"),
        ),
        EvalExample(
            id="login-reset",
            ticket="I forgot my password and cannot sign in.",
            expected_intent="account_access",
            expected_severity="normal",
            tags=("authentication",),
        ),
        EvalExample(
            id="outage",
            ticket="The production dashboard is down for every user.",
            expected_intent="technical_support",
            expected_severity="high",
            tags=("incident", "customer-impact"),
        ),
        EvalExample(
            id="how-to-export",
            ticket="How do I export last month's usage report?",
            expected_intent="technical_support",
            expected_severity="low",
            tags=("how-to",),
        ),
        EvalExample(
            id="email-change",
            ticket="Please change the email address on my account.",
            expected_intent="account_access",
            expected_severity="normal",
            tags=("profile",),
        ),
    )


def classify_baseline(ticket: str) -> str:
    text = ticket.lower()
    if any(term in text for term in ("refund", "charged", "invoice", "billing")):
        intent = "billing"
    elif any(term in text for term in ("password", "sign in", "login", "email")):
        intent = "account_access"
    else:
        intent = "technical_support"

    if any(term in text for term in ("down", "every user", "charged twice", "refund")):
        severity = "high"
    elif any(term in text for term in ("forgot", "cannot", "change")):
        severity = "normal"
    else:
        severity = "low"

    return f"{intent}|{severity}|Route to {intent} queue with {severity} urgency."


def classify_candidate(ticket: str) -> str:
    text = ticket.lower()
    if any(term in text for term in ("refund", "charged", "invoice", "billing")):
        intent = "billing"
    elif any(term in text for term in ("password", "sign in", "login", "email")):
        intent = "account_access"
    else:
        intent = "technical_support"

    # Candidate improves wording but regresses refund severity.
    if any(term in text for term in ("down", "every user")):
        severity = "high"
    elif any(term in text for term in ("forgot", "cannot", "change", "refund")):
        severity = "normal"
    else:
        severity = "low"

    return f"{intent}|{severity}|Thanks. I routed this to {intent} at {severity} urgency."


def parse_prediction(raw_output: str) -> Prediction:
    parts = raw_output.split("|", maxsplit=2)
    if len(parts) != 3:
        raise ValueError("Model output must use intent|severity|answer format.")

    intent, severity, answer = (part.strip() for part in parts)
    if intent not in {"billing", "technical_support", "account_access"}:
        raise ValueError(f"Unknown intent: {intent}")
    if severity not in {"low", "normal", "high"}:
        raise ValueError(f"Unknown severity: {severity}")

    return Prediction(intent=intent, severity=severity, answer=answer)


def token_estimate(text: str) -> int:
    return max(1, round(len(text.split()) * 1.3))


def run_eval(
    *,
    examples: Iterable[EvalExample],
    model: ModelFn,
    model_version: str,
    prompt_version: str,
) -> tuple[TraceRecord, ...]:
    traces: list[TraceRecord] = []

    for example in examples:
        started = perf_counter()
        raw_output = model(example.ticket)
        latency_ms = (perf_counter() - started) * 1000
        prediction = parse_prediction(raw_output)
        passed = (
            prediction.intent == example.expected_intent
            and prediction.severity == example.expected_severity
        )

        traces.append(
            TraceRecord(
                trace_id=str(uuid4()),
                example_id=example.id,
                model_version=model_version,
                prompt_version=prompt_version,
                latency_ms=latency_ms,
                prompt_tokens=token_estimate(example.ticket),
                completion_tokens=token_estimate(prediction.answer),
                expected_intent=example.expected_intent,
                actual_intent=prediction.intent,
                expected_severity=example.expected_severity,
                actual_severity=prediction.severity,
                passed=passed,
                tags=example.tags,
            )
        )

    return tuple(traces)


def accuracy(traces: Iterable[TraceRecord]) -> float:
    records = tuple(traces)
    if not records:
        return 0.0
    return sum(record.passed for record in records) / len(records)


def recall_for_high_severity(traces: Iterable[TraceRecord]) -> float:
    high_records = [
        record for record in traces if record.expected_severity == "high"
    ]
    if not high_records:
        return 1.0
    return sum(
        record.actual_severity == "high" for record in high_records
    ) / len(high_records)


def evaluate_release(
    *,
    traces: tuple[TraceRecord, ...],
    minimum_accuracy: float = 0.90,
    minimum_high_severity_recall: float = 1.0,
    maximum_average_latency_ms: float = 50.0,
    maximum_average_tokens: float = 40.0,
) -> ReleaseReport:
    score = accuracy(traces)
    high_recall = recall_for_high_severity(traces)
    avg_latency = mean(record.latency_ms for record in traces)
    avg_tokens = mean(
        record.prompt_tokens + record.completion_tokens for record in traces
    )

    risk_checks = (
        RiskCheck(
            name="overall_accuracy",
            passed=score >= minimum_accuracy,
            detail=f"{score:.0%} >= {minimum_accuracy:.0%}",
        ),
        RiskCheck(
            name="high_severity_recall",
            passed=high_recall >= minimum_high_severity_recall,
            detail=f"{high_recall:.0%} >= {minimum_high_severity_recall:.0%}",
        ),
        RiskCheck(
            name="latency_budget",
            passed=avg_latency <= maximum_average_latency_ms,
            detail=f"{avg_latency:.2f}ms <= {maximum_average_latency_ms:.2f}ms",
        ),
        RiskCheck(
            name="token_budget",
            passed=avg_tokens <= maximum_average_tokens,
            detail=f"{avg_tokens:.1f} <= {maximum_average_tokens:.1f}",
        ),
    )

    return ReleaseReport(
        model_version=traces[0].model_version,
        prompt_version=traces[0].prompt_version,
        accuracy=score,
        high_severity_recall=high_recall,
        average_latency_ms=avg_latency,
        average_tokens=avg_tokens,
        traces=traces,
        risk_checks=risk_checks,
        promoted=all(check.passed for check in risk_checks),
    )
