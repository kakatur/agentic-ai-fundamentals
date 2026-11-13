# Python Classes and Pydantic: Validate AI Application Data

Learn how type hints, a dataclass, and a Pydantic model handle incoming search requests. The example compares a string where an integer is expected with a valid request. It runs locally without an AI model.

## Type hints and dataclasses

A type hint communicates the intended type to readers and type-checking tools. Python does not automatically enforce it at runtime. A dataclass generates methods such as an initializer; it does not by itself validate annotated field types.

```python
PlainRequest(text="order status", max_results="3")
```

This dataclass accepts `"3"` and stores a string, despite the `int` annotation. The demo prints `'3' str`. Such a value can cause trouble later when code expects a number.

## Validate the request at the boundary

`SearchRequest` is a Pydantic model. Its strict configuration rejects a string where an integer is required; `extra="forbid"` rejects unexpected fields. `Field(ge=1, le=10)` constrains the result count, and `min_length=1` requires at least one character in `text`. A whitespace-only string still meets that length constraint; add a separate rule if the application must reject it.

```python
SearchRequest.model_validate({"text": "order status", "max_results": 3})
```

The valid input produces a model. `model_dump()` returns a Python dictionary. Passing the string `"3"` instead raises `ValidationError`; the demo displays the field location and `int_type` error code. The code deliberately enables strict mode. Pydantic can coerce some inputs in its default, non-strict mode, so do not assume both modes behave the same.

A validated type and range do not guarantee the search query is accurate or safe to execute in every context. Add rules appropriate to the application and handle validation errors without exposing sensitive input.

## Interview questions

- **Basic:** What is the difference between `==` and `is` in Python? `==` compares values; `is` checks whether two names refer to the same object. Use `is None` to test for `None`.
- **Intermediate:** Do Python type hints automatically validate function or dataclass inputs? No. They describe intended types; a separate runtime check is needed.
- **Advanced:** Why choose strict validation at an external boundary? It rejects unintended coercions such as a numeric string for an integer in this example. Choose strictness deliberately: some input formats may require explicit conversion before validation.

## Run and test

Requires Python 3.10 or newer and Pydantic 2. The commands below create a local environment; activation shown for macOS/Linux.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python demo.py
python -m unittest -v
```

Try changing `max_results` to `0`, `11`, and `"3"`. Compare the validation errors with a valid integer. The code was checked with Pydantic 2.14.3.

References: Python expressions (`==` and `is`) [https://docs.python.org/3/reference/expressions.html]; Python dataclasses [https://docs.python.org/3/library/dataclasses.html]; Pydantic models [https://docs.pydantic.dev/latest/concepts/models/]; Pydantic strict mode [https://docs.pydantic.dev/latest/concepts/strict_mode/].
