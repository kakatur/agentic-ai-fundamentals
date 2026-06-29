from agent_as_tool import ToolCoordinator, ToolRequest, make_support_tools


def test_single_specialist_tool_handles_narrow_request():
    coordinator = ToolCoordinator(make_support_tools())
    result = coordinator.answer(ToolRequest("cust-1", "Please refund this charge"))
    assert result.tool_name == "billing_tool"
    assert result.confidence > 0.8
    assert coordinator.audit_log[0].reason == "matched: refund, charge"


def test_tool_budget_limits_fan_out():
    coordinator = ToolCoordinator(make_support_tools(), max_tool_calls=2)
    result = coordinator.answer(ToolRequest("cust-2", "payment login timeout error"))
    assert result.tool_name == "coordinator_merge"
    assert len(coordinator.audit_log) == 2


def test_no_match_stays_with_coordinator():
    coordinator = ToolCoordinator(make_support_tools())
    result = coordinator.answer(ToolRequest("cust-3", "change my display color"))
    assert result.tool_name == "coordinator"
    assert result.confidence == 0.0
