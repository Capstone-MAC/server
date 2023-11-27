from enum import Enum

class MACResult(Enum):
    SUCCESS = 200
    FAIL = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    TIME_OUT = 408
    CONFLICT = 409
    ENTITY_ERROR = 422
    INTERNAL_SERVER_ERROR = 500
    