from ai_text_pipeline import classify_requests

items = [
    "Summarize this design doc",
    "translate hello to Spanish",
    "   ",
    "Extract invoice total",
]
for result in classify_requests(items):
    print(result)
