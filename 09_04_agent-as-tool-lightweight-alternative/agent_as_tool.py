from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable


@dataclass(frozen=True)
class ToolRequest:
    customer_id: str
    text: str
    priority: int = 1


@dataclass(frozen=True)
class ToolResult:
    tool_name: str
    answer: str
    confidence: float
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class ToolCall:
    tool_name: str
    reason: str
    result: ToolResult


@dataclass(frozen=True)
class AgentTool:
    name: str
    description: str
    keywords: tuple[str, ...]
    handler: Callable[[ToolRequest], ToolResult]

    def matches(self, request: ToolRequest) -> tuple[str, ...]:
        text = request.text.lower()
        return tuple(keyword for keyword in self.keywords if keyword in text)

    def run(self, request: ToolRequest) -> ToolResult:
        return self.handler(request)


@dataclass
class ToolCoordinator:
    tools: list[AgentTool]
    max_tool_calls: int = 2
    audit_log: list[ToolCall] = field(default_factory=list)

    def choose_tools(self, request: ToolRequest) -> list[tuple[AgentTool, tuple[str, ...]]]:
        ranked = [
            (tool, matches)
            for tool in self.tools
            if (matches := tool.matches(request))
        ]
        ranked.sort(key=lambda item: (-len(item[1]), item[0].name))
        return ranked[: self.max_tool_calls]

    def answer(self, request: ToolRequest) -> ToolResult:
        selected = self.choose_tools(request)
        if not selected:
            return ToolResult(
                tool_name="coordinator",
                answer="No specialist tool matched the request.",
                confidence=0.0,
                evidence=("no matching tool keywords",),
            )

        results: list[ToolResult] = []
        for tool, matches in selected:
            result = tool.run(request)
            self.audit_log.append(
                ToolCall(
                    tool_name=tool.name,
                    reason=f"matched: {', '.join(matches)}",
                    result=result,
                )
            )
            results.append(result)

        if len(results) == 1:
            return results[0]

        confidence = sum(result.confidence for result in results) / len(results)
        answer = " | ".join(result.answer for result in results)
        evidence = tuple(item for result in results for item in result.evidence)
        return ToolResult("coordinator_merge", answer, confidence, evidence)


def make_support_tools() -> list[AgentTool]:
    def billing(request: ToolRequest) -> ToolResult:
        return ToolResult(
            "billing_tool",
            f"Check invoice and payment history for {request.customer_id}.",
            0.88,
            ("billing scope matched",),
        )

    def security(request: ToolRequest) -> ToolResult:
        return ToolResult(
            "security_tool",
            f"Review login risk and active sessions for {request.customer_id}.",
            0.84,
            ("security scope matched",),
        )

    def technical(request: ToolRequest) -> ToolResult:
        return ToolResult(
            "technical_tool",
            f"Collect logs and reproduction details for {request.customer_id}.",
            0.8,
            ("technical scope matched",),
        )

    return [
        AgentTool("billing_tool", "Handles payments and invoices", ("invoice", "payment", "refund", "charge"), billing),
        AgentTool("security_tool", "Handles login and account risk", ("login", "mfa", "password", "risk"), security),
        AgentTool("technical_tool", "Handles errors and product failures", ("error", "bug", "timeout", "crash"), technical),
    ]
