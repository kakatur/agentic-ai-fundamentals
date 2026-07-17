from context_compression import compress_context, render_compressed_context


lines = [
    "The user is planning a migration.",
    "The answer must avoid downtime.",
    "We decided to migrate accounts in batches.",
    "Next: confirm rollback owner.",
    "The old system uses nightly exports.",
]

compressed = compress_context(lines)
print(render_compressed_context(compressed))
