from agent_as_tool import ToolCoordinator, ToolRequest, make_support_tools


def main() -> None:
    coordinator = ToolCoordinator(make_support_tools(), max_tool_calls=2)
    request = ToolRequest("cust-184", "Payment succeeded but login still times out")
    result = coordinator.answer(request)

    print(result.tool_name)
    print(result.answer)
    print("audit:")
    for call in coordinator.audit_log:
        print(f"- {call.tool_name}: {call.reason}")


if __name__ == "__main__":
    main()
