"""Send an HTTP JSON request through a Requests-compatible session."""
import requests


def fetch_order(base_url: str, order_id: str, session=None) -> dict:
    """Fetch an order; propagate HTTP, timeout, and decoding errors."""
    client = session if session is not None else requests
    response = client.get(f'{base_url}/orders', params={'id': order_id}, timeout=5)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict) or not isinstance(data.get('status'), str):
        raise ValueError('Response must contain a string status')
    return data
