from fastapi.security.api_key import APIKeyHeader
from fastapi import Security
from typing import Optional
# from auth.env import API_KEY

API_KEY = "test-key"

api_key_header = APIKeyHeader(name="access_token", auto_error=False)


def get_api_key(api_key_header: APIKeyHeader = Security(api_key_header)) -> Optional[APIKeyHeader]:
    if api_key_header == API_KEY:
        return api_key_header

    else:
        return None
