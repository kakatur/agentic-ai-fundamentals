# Agent-to-Agent Protocol (A2A)

## Core Concepts And Mental Model

A2A is about communication between agents that do not share one runtime. It is
not the same as a Python function call, and it is not the same as giving one
agent a tool. The durable idea is interoperability: one agent discovers another
agent's capabilities, sends a task, receives messages or artifacts, and tracks
task state.

The current A2A specification describes concepts such as Agent Cards, skills,
messages, tasks, artifacts, streaming updates, and protocol bindings. See the
official specification for the current schema details:
https://a2a-protocol.org/latest/specification/

## Important Design Implications

- Discovery should be capability-based, not hard-coded to one implementation.
- Agent Cards are contracts. They tell clients what an agent claims to do.
- Task state matters because remote work may be asynchronous.
- Artifacts are outputs with identity, not just chat text.
- Security and authorization belong at the agent boundary.

## Code Map And Implementation Guidance

- `AgentCard` describes a remote agent and its declared skills.
- `AgentRegistry.find()` selects an agent by capability tag and input mode.
- `A2AClient.send_task()` creates a task message for the selected agent.
- `A2AClient.complete_task()` records a completed task with an artifact.

This is not a full A2A implementation. It is a deterministic teaching model
that makes the protocol shape testable without a server.

## Real Production Considerations And Trade-Offs

A2A is useful when agents cross framework, team, vendor, or network boundaries.
It is overkill when all specialists live inside one application and can be
called through typed functions.

The main trade-off is interoperability versus operational surface. Once work
crosses an agent boundary, you need identity, auth, retries, timeouts, version
compatibility, and task lifecycle handling.

## Practical Tips And Common Mistakes

- Treat Agent Cards as external API contracts.
- Validate capabilities before sending work.
- Preserve task IDs and context IDs in logs.
- Do not expose internal scratchpads as artifacts.
- Keep MCP and A2A separate in your mental model: MCP connects agents to tools;
  A2A connects agents to agents.

## Interview Questions

Basic: What problem does A2A solve?

Intermediate: How is A2A different from tool calling?

Advanced: What security and lifecycle concerns appear when tasks cross agent
boundaries?

## Commands

```bash
cd 09_06_agent-to-agent-protocol-a2a
python3 demo.py
python3 -m pytest
```
