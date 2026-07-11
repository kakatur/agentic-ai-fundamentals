from context_budget import ContextItem, build_context, edge_load_context, reserve_response_budget


items = [
    ContextItem("policy", "Refunds over 500 dollars require manager approval.", priority=5, pinned=True),
    ContextItem("profile", "The customer prefers concise answers.", priority=3, pinned=True),
    ContextItem("old_ticket", "Two years ago the customer asked about shipping labels.", priority=1),
    ContextItem("recent_ticket", "Yesterday the customer reported a duplicate invoice.", priority=4),
]

available = reserve_response_budget(context_window=120, response_tokens=35, safety_margin=10)
report = build_context(items, max_tokens=available)

print(f"Selected: {[item.label for item in report.selected]}")
print(f"Dropped: {[item.label for item in report.dropped]}")
print()
print(edge_load_context("Answer using only the supplied context.", report.selected, "Can I refund this invoice?"))
