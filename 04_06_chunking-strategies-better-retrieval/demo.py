from chunking import window_chunks
text="Reset a password from settings. Keep the recovery code private. Contact support if the account is locked."
for chunk in window_chunks(text,6,2,"help"): print(chunk)
