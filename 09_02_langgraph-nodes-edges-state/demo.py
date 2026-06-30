"""Run the lesson graph with a few support requests."""

from graph_workflow import SupportState, build_support_graph


def print_run(label: str, state: SupportState) -> None:
    graph = build_support_graph()
    run = graph.invoke(state)

    print(f"\n== {label} ==")
    print(f"visited: {' -> '.join(run.visited)}")
    print(f"route:   {run.state.route}")
    print(f"risk:    {run.state.risk}")
    print(f"facts:   {', '.join(run.state.facts)}")
    print(f"answer:  {run.state.final_answer}")


def main() -> None:
    print_run(
        "billing path",
        SupportState(request="I was charged twice and need a refund."),
    )
    print_run(
        "security path",
        SupportState(request="I lost MFA access and cannot log in."),
    )
    print_run(
        "escalation path",
        SupportState(
            request="Urgent: enterprise customer says this looks like fraud.",
            customer_tier="enterprise",
        ),
    )


if __name__ == "__main__":
    main()
