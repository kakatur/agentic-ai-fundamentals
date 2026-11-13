"""Prepare support requests for a prompt; no model or API is called."""


def clean_text(text: str) -> str:
    """Collapse whitespace and reject input that contains no words."""
    cleaned = " ".join(text.split())
    if not cleaned:
        raise ValueError("ERR-001: User text must not be empty")
    return cleaned


def prepare_request(text: str, max_words: int = 12) -> dict:
    """Clean a request and include up to max_words in a prompt.

    We use a small word limit for our convenience. In a real-world
    application, the model can usually handle more words than this
    demo allows.
    """
    if isinstance(max_words, bool) or not isinstance(max_words, int) or max_words < 1:
        raise ValueError("max_words must be a positive integer")

    cleaned = clean_text(text)
    words = cleaned.split()
    selected = []
    for word in words:
        if len(selected) == max_words:
            break
        selected.append(word)

    selected_text = " ".join(selected)
    prompt = "Investigate this issue: " + selected_text
    return {
        "cleaned_text": cleaned,
        "word_count": len(words),
        "prompt": prompt,
    }


def build_prompt(text: str, max_words: int = 12) -> str:
    """Return only the prompt from prepare_request."""
    return prepare_request(text, max_words)["prompt"]


def build_openai_prompt_fields(text: str) -> dict:
    """Build instruction and input fields for an OpenAI Responses API call."""
    cleaned = clean_text(text)
    return {
        "instructions": "Investigate this issue",
        "input": [{"role": "user", "content": cleaned}],
    }


def prepare_batch(requests: list[str], max_words: int = 12) -> list[dict]:
    """Prepare each request, keeping a clear error for empty entries."""
    if isinstance(max_words, bool) or not isinstance(max_words, int) or max_words < 1:
        raise ValueError("max_words must be a positive integer")
    results = []
    for position, text in enumerate(requests, start=1):
        try:
            result = prepare_request(text, max_words)
        except ValueError as error:
            results.append({"position": position, "error": str(error)})
        else:
            results.append({"position": position, "request": result})
    return results
