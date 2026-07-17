from session_memory import add_message, build_conversation_window, render_window


history = ()
history = add_message(history, "user", "My name is Mira.")
history = add_message(history, "assistant", "Nice to meet you, Mira.")
history = add_message(history, "user", "I prefer short answers.")
history = add_message(history, "assistant", "I will keep replies concise.")
history = add_message(history, "user", "What did I ask for?")

window = build_conversation_window(history, ("User name: Mira", "Preference: short answers"), max_pairs=2)
print(render_window(window))
