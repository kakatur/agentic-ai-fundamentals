from chunking import window_chunks


text = "Reset a password from settings. Keep the recovery code private. Contact support if the account is locked."
for chunk in window_chunks(text, size=6, overlap=2, document_id="help"):
    print(chunk)
