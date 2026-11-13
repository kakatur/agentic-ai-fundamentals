import json
from pathlib import Path
from tempfile import TemporaryDirectory
from pydantic import ValidationError
from parse_response import parse_response, save_response

raw = '{"category":"shipping","summary":"Order arrives tomorrow."}'
response = parse_response(raw)
print('Category:', response.category)
print('Summary:', response.summary)
with TemporaryDirectory() as directory:
    path = Path(directory) / 'result.json'
    save_response(response, path)
    print('Saved JSON:', json.loads(path.read_text(encoding='utf-8')))
for bad in ('{"category":', '{"category":"billing","summary":"Hi"}'):
    try:
        parse_response(bad)
    except json.JSONDecodeError:
        print('Error: invalid JSON')
    except ValidationError:
        print('Error: response does not match schema')
