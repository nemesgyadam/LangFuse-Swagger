import os

from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

API_KEY = os.getenv("API_KEY", "42")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)


async def get_api_key(api_key: str = Security(api_key_header)) -> str:
    """Validate API key."""
    if api_key == API_KEY:
        return api_key
    raise HTTPException(status_code=403, detail="Invalid API key")
