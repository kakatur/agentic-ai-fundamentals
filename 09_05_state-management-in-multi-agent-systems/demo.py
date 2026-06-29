from state_management import Checkpointer, WorkflowState, run_workflow


def main() -> None:
    checkpoint = Checkpointer()
    final = run_workflow(
        WorkflowState("task-9", "urgent refund request for wrong invoice"),
        checkpoint,
    )
    print(final)
    print("history versions:", [state.version for state in checkpoint.history("task-9")])


if __name__ == "__main__":
    main()
