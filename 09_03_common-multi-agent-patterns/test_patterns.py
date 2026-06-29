from patterns import (
    Route,
    SpecialistAgent,
    Task,
    VerifierAgent,
    default_coordinator,
    default_specialists,
    run_producer_verifier_pattern,
)


def test_coordinator_router_selects_billing_specialist():
    result = default_coordinator().run_router_pattern(
        Task(customer_id="cus_1", request="refund my duplicate charge")
    )

    assert result.route == Route.BILLING
    assert result.replies[0].agent == "billing_agent"
    assert result.handoffs[0].sender == "coordinator"
    assert result.handoffs[0].receiver == "billing_agent"


def test_parallel_pattern_fans_out_to_multiple_relevant_specialists():
    result = default_coordinator().run_parallel_pattern(
        Task(customer_id="cus_2", request="login error after payment timeout")
    )

    agents = {reply.agent for reply in result.replies}
    assert agents == {"billing_agent", "security_agent", "technical_agent"}
    assert len(result.handoffs) == 3
    assert " | " in result.answer


def test_low_confidence_or_critical_priority_escalates():
    result = default_coordinator().run_router_pattern(
        Task(customer_id="cus_3", request="unclear problem", priority=5)
    )

    assert result.route == Route.HUMAN_REVIEW
    assert result.answer == "Escalated for human review."
    assert result.handoffs[-1].receiver == "human_review"


def test_producer_verifier_accepts_supported_answer():
    result = run_producer_verifier_pattern(
        Task(customer_id="cus_4", request="refund invoice question"),
        producer=default_specialists()[0],
        verifier=VerifierAgent(),
    )

    assert result.verified is True
    assert result.route == Route.BILLING


def test_producer_verifier_rejects_unsupported_answer():
    producer = SpecialistAgent(
        name="vague_agent",
        route=Route.TECHNICAL,
        keywords=("outage",),
        response_template="General response without customer support.",
    )

    result = run_producer_verifier_pattern(
        Task(customer_id="cus_5", request="outage"),
        producer=producer,
        verifier=VerifierAgent(),
    )

    assert result.verified is False
    assert result.route == Route.HUMAN_REVIEW
    assert result.handoffs[-1].sender == "verifier"
