import sqlite3
from conversation_store import add_messages, create_schema, get_messages

connection = sqlite3.connect(':memory:')
try:
    create_schema(connection)
    add_messages(connection, 'order-A17', [('user', 'Where is my order?'), ('assistant', 'It shipped today.')])
    print('Conversation order-A17:', get_messages(connection, 'order-A17'))
    print('Other conversation:', get_messages(connection, 'other'))
finally:
    connection.close()
