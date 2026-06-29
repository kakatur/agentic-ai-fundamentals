from state_management import Checkpointer, StatePatch, WorkflowState, merge_state, run_workflow


def test_merge_appends_unique_facts_and_risks():
    state = WorkflowState("t1", "refund")
    merged = merge_state(
        state,
        StatePatch(facts=("billing intent",), risks=("money movement",)),
        StatePatch(facts=("billing intent",), risks=("money movement", "urgent")),
    )
    assert merged.facts == ("billing intent",)
    assert merged.risks == ("money movement", "urgent")
    assert merged.version == 1


def test_checkpointer_keeps_resume_history():
    checkpoint = Checkpointer()
    final = run_workflow(WorkflowState("t2", "urgent refund"), checkpoint)
    assert final.decision == "review"
    assert len(checkpoint.history("t2")) == 4
    assert checkpoint.latest("t2") == final


def test_low_risk_request_answers_directly():
    final = run_workflow(WorkflowState("t3", "login question"), Checkpointer())
    assert final.route == "security"
    assert final.decision == "answer"
