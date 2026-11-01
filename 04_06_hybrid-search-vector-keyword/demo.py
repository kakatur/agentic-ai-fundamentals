from hybrid import reciprocal_rank_fusion


dense = ["general-access", "FAQ-reset"] + [f"dense-{n}" for n in range(3, 6)] + ["E104-runbook", "dense-7", "dense-8"]
lexical = ["E104-runbook"] + [f"lexical-{n}" for n in range(2, 5)] + ["FAQ-reset", "lexical-6", "lexical-7", "general-access"]
focus = {"FAQ-reset", "E104-runbook", "general-access"}

for document_id, score in reciprocal_rank_fusion([dense, lexical], rank_constant=10):
    if document_id in focus:
        print(f"{document_id}: {score:.4f}")
