from hybrid import hybrid_search


dense = ["password-guide", "account-security", "e104-runbook"]
lexical = ["e104-runbook", "error-catalog", "password-guide"]
eligible = {"password-guide", "e104-runbook", "error-catalog"}
for document_id, score in hybrid_search(dense, lexical, eligible):
    print(f"{score:.5f}  {document_id}")
