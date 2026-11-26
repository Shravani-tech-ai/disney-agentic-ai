"""HTTP client used by ADK tools to call the local mock provider API."""
import os
import httpx
from typing import Any

DEFAULT_BASE_URL = os.getenv("MOCK_PROVIDER_API_URL", "http://127.0.0.1:8001")
TIMEOUT = float(os.getenv("MOCK_PROVIDER_API_TIMEOUT", "10"))

def _request(method: str, path: str, **kwargs: Any) -> dict[str, Any]:
    url = DEFAULT_BASE_URL.rstrip("/") + path
    try:
        response = httpx.request(method, url, timeout=TIMEOUT, **kwargs)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict): return {"success":False,"mock":True,"error":"Unexpected API response format."}
        return payload
    except httpx.HTTPStatusError as exc:
        try: detail = exc.response.json().get("detail", exc.response.text)
        except Exception: detail = exc.response.text
        return {"success":False,"mock":True,"http_status":exc.response.status_code,"error":str(detail)}
    except httpx.HTTPError as exc:
        return {"success":False,"mock":True,"error":f"Mock provider API is unreachable at {url}: {exc}. Start mock_api_server on port 8001."}

def get(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]: return _request("GET",path,params=params)
def post(path: str, body: dict[str, Any]) -> dict[str, Any]: return _request("POST",path,json=body)
