from conversation_store import ConversationStore

store = ConversationStore(':memory:')
store.add_message('c1', 'user', 'hello')
store.add_message('c1', 'assistant', 'hi')
print(store.list_messages('c1'))
