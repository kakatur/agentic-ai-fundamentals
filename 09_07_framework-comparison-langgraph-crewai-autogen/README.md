# Framework Comparison: LangGraph vs CrewAI vs AutoGen

## Core Concepts And Mental Model

Choose a framework by control model, not by popularity. The question is not
"Which framework is best?" The question is "What shape does this workflow
need?"

Useful comparison dimensions:

- explicit control flow
- role and crew modeling
- conversational agent interaction
- state, checkpoint, and resume support
- operational control and testability

The right answer can also be no framework. Typed functions, queues, and tool
wrappers are often enough.

## Important Design Implications

- LangGraph is strongest when explicit state and graph control matter.
- CrewAI is strongest when the mental model is role-oriented delegation.
- AutoGen is strongest when agent conversation is the center of the design.
- No framework is valid when the workflow is small and deterministic.
- A matrix beats vibes. Score the project needs first.

## Code Map And Implementation Guidance

- `FrameworkProfile` stores a framework's relative strengths.
- `ProjectNeeds` stores project weights.
- `score()` multiplies strengths by weights.
- `rank_frameworks()` returns the ordered decision matrix.
- `demo.py` shows a stateful workflow that prefers LangGraph.

The scores are teaching heuristics, not universal truth. Adjust them for your
team, hosting environment, compliance requirements, and framework versions.

## Real Production Considerations And Trade-Offs

Frameworks buy structure and ecosystem. They also add version churn, runtime
constraints, debugging surfaces, and migration cost.

Choose a framework when it removes more complexity than it introduces. If your
only need is calling two specialist functions and merging results, a framework
may be heavier than the problem.

## Practical Tips And Common Mistakes

- Write down the workflow shape before choosing a tool.
- Score the top two options against the same requirements.
- Prototype the hardest failure mode, not the happiest demo.
- Include operations: tracing, retries, deployment, and tests.
- Revisit the decision after the first working version.

## Interview Questions

Basic: When would LangGraph be a better fit than a role-based framework?

Intermediate: How would you compare CrewAI and AutoGen for a support workflow?

Advanced: What evidence would convince you not to use a multi-agent framework?

## Commands

```bash
cd 09_07_framework-comparison-langgraph-crewai-autogen
python3 demo.py
python3 -m pytest
```
