from pathlib import Path
from safe_file_pipeline import write_json, read_json

path = Path('demo-request.json')
write_json(path, {'message': 'hello'})
print(read_json(path))
path.unlink()
