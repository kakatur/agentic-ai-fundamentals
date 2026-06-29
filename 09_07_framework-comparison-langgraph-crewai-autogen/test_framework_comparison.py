from framework_comparison import ProjectNeeds, rank_frameworks, recommendation


def test_stateful_workflow_prefers_langgraph():
    ranked = rank_frameworks(ProjectNeeds(control_flow=5, state_resume=5, operational_control=4))
    assert ranked[0][0] == "LangGraph"


def test_role_heavy_project_prefers_crewai():
    ranked = rank_frameworks(ProjectNeeds(role_modeling=5, conversation=2))
    assert ranked[0][0] == "CrewAI"


def test_conversation_heavy_project_prefers_autogen():
    ranked = rank_frameworks(ProjectNeeds(conversation=5, role_modeling=3))
    assert ranked[0][0] == "AutoGen"


def test_recommendation_includes_reason():
    text = recommendation(ProjectNeeds(control_flow=5))
    assert "points" in text
    assert "fit" in text
