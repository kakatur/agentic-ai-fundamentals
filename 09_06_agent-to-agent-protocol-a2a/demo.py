from a2a_protocol import A2AClient, sample_registry


def main() -> None:
    client = A2AClient(sample_registry())
    task = client.send_task("task-42", "refund", "Review refund eligibility")
    print(task)
    print(client.complete_task("task-42", "refund-summary", "Eligible after invoice review"))


if __name__ == "__main__":
    main()
