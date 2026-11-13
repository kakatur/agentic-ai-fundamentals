from pydantic import ValidationError
from request_models import PlainRequest, SearchRequest

raw = {"text": "order status", "max_results": "3"}
plain = PlainRequest(**raw)
print("Dataclass max_results:", repr(plain.max_results), type(plain.max_results).__name__)
try:
    SearchRequest.model_validate(raw)
except ValidationError as error:
    issue = error.errors()[0]
    print("Strict validation error:", issue["loc"], issue["type"])
request = SearchRequest.model_validate({"text": "order status", "max_results": 3})
print("Valid request:", request.model_dump())
