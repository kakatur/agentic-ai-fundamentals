from message_collections import count_by_role, make_history, sources_in_order

messages = [
    {"role": "user", "content": "Where is my order?"},
    {"role": "assistant", "content": "What is your order number?"},
    {"role": "user", "content": "A17"},
    {"role": "assistant", "content": "It shipped today."},
]
sources = ["shipping", "returns", "shipping", "orders"]
print("Recent messages:", make_history(messages))
print("Role counts:", count_by_role(messages))
print("Unique sources:", sources_in_order(sources))
