from memory_privacy import PrivateMemory, PrivacyAwareMemoryStore


store = PrivacyAwareMemoryStore()
store.remember(PrivateMemory("m1", "u1", "preference", "prefers concise answers", consent=True))
store.remember(PrivateMemory("m2", "u1", "project", "billing migration", consent=True))

print(store.export_user("u1"))
print(f"Deleted: {store.delete_user('u1')}")
print(store.audit_log("u1"))
