"""Run the lesson graphs and print state updates."""

from parallel_workflow import build_parallel_graph
from support_workflow import build_support_graph, initial_state


def show_support_run(request: str) -> None:
    graph = build_support_graph()
    print(f"\nRequest: {request}")
    for update in graph.stream(initial_state(request), stream_mode="updates"):
        print(update)


def show_parallel_run() -> None:
    graph = build_parallel_graph()
    result = graph.invoke(
        {
            "topic": "agent deployment",
            "notes": [],
            "summary": "",
        }
    )
    print("\nParallel result:")
    print(result)


if __name__ == "__main__":
    show_support_run("How do I reset my password?")
    show_support_run("I need a payment refund")
    show_parallel_run()
