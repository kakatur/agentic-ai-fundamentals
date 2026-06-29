"""Run the common multi-agent patterns from the lesson."""

from patterns import (
    Task,
    VerifierAgent,
    default_coordinator,
    default_specialists,
    run_producer_verifier_pattern,
)


def print_result(label: str, result) -> None:
    print(f"\n{label}")
    print(f"  route: {result.route}")
    print(f"  confidence: {result.confidence}")
    print(f"  verified: {result.verified}")
    print(f"  answer: {result.answer}")
    for handoff in result.handoffs:
        print(f"  handoff: {handoff.sender} -> {handoff.receiver}: {handoff.reason}")


def main() -> None:
    coordinator = default_coordinator()

    print_result(
        "Coordinator-router",
        coordinator.run_router_pattern(
            Task(customer_id="cus_101", request="I was charged twice")
        ),
    )
    print_result(
        "Parallel specialists",
        coordinator.run_parallel_pattern(
            Task(
                customer_id="cus_202",
                request="Login fails after payment API timeout",
            )
        ),
    )
    print_result(
        "Producer-verifier",
        run_producer_verifier_pattern(
            Task(customer_id="cus_303", request="Need refund for invoice"),
            producer=default_specialists()[0],
            verifier=VerifierAgent(),
        ),
    )
    print_result(
        "Escalation",
        coordinator.run_router_pattern(
            Task(customer_id="cus_404", request="Something is wrong", priority=5)
        ),
    )


if __name__ == "__main__":
    main()
