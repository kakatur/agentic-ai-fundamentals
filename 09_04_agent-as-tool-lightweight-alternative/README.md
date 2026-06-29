# Agent-as-Tool: The Lightweight Alternative

## Core Concepts And Mental Model

Agent-as-tool means a coordinator calls a specialist through the same kind of
contract it would use for any other tool. The specialist can still contain an
LLM, retrieval, validation, or its own private workflow. The coordinator does
not need to know that. It sees a name, input schema, output schema, and a
bounded result.

Use this shape when the work is mostly request-response:

- one coordinator owns the user interaction
- specialists do not need to talk to each other
- tool calls can be bounded and audited
- the result can be merged with simple policy

Do not reach for a graph runtime just because the implementation contains more
than one agent. Start with the smallest control surface that gives you routing,
budgets, testability, and observability.

## Important Design Implications

- A specialist tool needs a narrow description. If every tool says it handles
  "customer issues," the coordinator cannot route safely.
- Tool outputs should include confidence and evidence, not only prose.
- The coordinator should own call budgets. A tool wrapper without a budget is
  just hidden fan-out.
- Audit records should include the tool name, reason, and returned result.
- Graduate to graph orchestration when specialists need long-running state,
  retries, human approval, loops, or explicit branch joins.

## Code Map And Implementation Guidance

- `AgentTool` defines the stable wrapper around a specialist.
- `ToolCoordinator.choose_tools()` ranks matching tools by keyword evidence.
- `ToolCoordinator.answer()` executes within `max_tool_calls` and records
  every call.
- `ToolResult` carries answer text, confidence, and evidence.
- `demo.py` shows a request that calls two tools and merges the result.

The implementation uses keyword matching so tests are deterministic. Replace
the matcher with an LLM router only after the contract, budget, and audit
behavior are already tested.

## Real Production Considerations And Trade-Offs

Agent-as-tool keeps the system simple, but it can hide complex behavior behind
one call. Make that safe by requiring structured outputs, timeouts, retries,
and redaction at the wrapper boundary.

This pattern is weak when the workflow needs shared state across many steps.
If a billing agent must wait for security, then technical support must retry
after billing, you have a workflow, not just a tool call. Use a graph, queue,
or state machine instead.

## Practical Tips And Common Mistakes

- Keep tool names action-oriented and domain-specific.
- Treat a tool description as routing policy, not marketing copy.
- Fail closed when no tool matches.
- Log why a tool was selected.
- Do not let tools call each other unless that recursion is explicitly part of
  the design.

## Interview Questions

Basic: What is the difference between an agent-as-tool and a multi-agent graph?

Intermediate: How would you keep an agent tool from making unbounded calls?

Advanced: When would you refactor an agent-as-tool design into a graph-based
workflow?

## Commands

```bash
cd 09_04_agent-as-tool-lightweight-alternative
python3 demo.py
python3 -m pytest
```
