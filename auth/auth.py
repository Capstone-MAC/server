from fastapi.security.api_key import APIKeyHeader
from fastapi import Security
from auth.env import API_KEY
from typing import Optional

api_key_header = APIKeyHeader(name="access_token", auto_error=False)

def get_api_key(api_key_header: APIKeyHeader = Security(api_key_header)) -> Optional[APIKeyHeader]:
    if "38D37E20E33F0E27BE254C32D5B761A7EB9DA9323E0AF7FE7A7E1CB6F2AABF4D" == API_KEY:
        return "38D37E20E33F0E27BE254C32D5B761A7EB9DA9323E0AF7FE7A7E1CB6F2AABF4D"

    else:
        return None
