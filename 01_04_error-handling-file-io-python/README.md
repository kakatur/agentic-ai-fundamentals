# Parse JSON in Python: Turn AI Responses Into Usable Data

Parse a simulated response, validate its fields, handle two different failures, and save the result as JSON. The example uses local sample text and does not call an AI model. It applies the Pydantic validation introduced in Lesson 1.3.

## Decode a response

```python
raw = '{"category":"shipping","summary":"Order arrives tomorrow."}'
data = json.loads(raw)
```

`json.loads` converts JSON text into Python data. Here, `data` is a dictionary with two string values. Valid JSON can also decode to a list, number, string, Boolean, or `None`; successful decoding alone does not establish that the result has the fields your program needs.

## Validate the expected shape

`Response.model_validate(data)` checks the decoded value against the model. `category` must be `shipping`, `returns`, or `other`, and `summary` must be a nonempty string. Strict mode and forbidden extra fields make the boundary explicit. Like Lesson 1.3, this length check permits a whitespace-only summary; add another rule if needed.

The valid response produces `response.category == "shipping"` and `response.summary == "Order arrives tomorrow."`. These checks establish the shape and allowed values, not whether an AI-generated summary is factually correct.

## Distinguish failures

- Malformed JSON such as `{"category":` causes `json.JSONDecodeError`. The text cannot be decoded.
- Valid JSON with the wrong structure or values, such as `{"category":"billing","summary":"Hi"}`, causes Pydantic `ValidationError`. The decoder succeeded, but the data did not meet the model.

The demo catches each separately and prints a clear message. Decide how to report or recover from errors in your application; do not silently treat malformed input as a valid response. Limit untrusted input size before parsing when appropriate.

## Save the result

`save_response` converts the validated model to a Python dictionary with `model_dump()`, then uses `json.dumps(..., indent=2)` to create JSON text and `Path.write_text` to save it. The demo uses a temporary directory and reads the file back, leaving no permanent result file. The function overwrites an existing destination; choose a different write strategy if that matters.

## Interview questions

- **Basic:** What is the difference between `json.loads` and `json.dumps`? `loads` decodes JSON text into Python data; `dumps` encodes Python data into JSON text.
- **Intermediate:** Does successful JSON parsing guarantee the fields are suitable for the application? No. Parsing checks JSON syntax, while a model can check the required shape and values.
- **Advanced:** Why distinguish a `JSONDecodeError` from a validation error? The first indicates malformed JSON; the second indicates data that parsed but did not satisfy the model. They can require different handling.

## Run and test

Requires Python 3.10 or newer and Pydantic 2. The demo uses only local data.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python demo.py
python -m unittest -v
```

Try an unsupported category, missing summary, and malformed JSON. Compare the errors. Verified with Pydantic 2.14.3.

References: Python JSON [https://docs.python.org/3/library/json.html]; Pydantic models [https://docs.pydantic.dev/latest/concepts/models/].
