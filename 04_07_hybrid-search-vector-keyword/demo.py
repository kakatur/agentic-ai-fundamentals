from hybrid import hybrid_search
dense=["password-guide","account-security","e104-runbook"]
lexical=["e104-runbook","error-catalog","password-guide"]
print(hybrid_search(dense,lexical,{"password-guide","e104-runbook","error-catalog"}))
