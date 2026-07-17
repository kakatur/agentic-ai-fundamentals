from long_term_memory import LongTermMemory


memory = LongTermMemory()
memory.remember("u1", "preferred_tone", "concise", "conversation:42", confidence=0.9)
memory.remember("u1", "project", "billing migration", "ticket:77", confidence=0.8)

print(memory.profile("u1", min_confidence=0.85))
for record in memory.retrieve("u1", "billing project"):
    print(memory.provenance(record))
