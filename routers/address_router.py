from database.models.address import Address, AddressBody
from database.models.results import MACResult
from fastapi.responses import JSONResponse
from database.models.user import User
from routers.env import db_session
from fastapi import APIRouter
from typing import Optional

address_router = APIRouter(
    prefix = "/user/address",
    tags = ["user"]
)

@address_router.get("/{user_id}",
    responses = {
        200: {
            "content": {
                "application/json": {
                    "example": [
                        {
                            "user_seq": -1,
                            "eng_addr": "string",
                            "addr_detail": "string",
                            "rn_mgt_sn": "string",
                            "si_nm": "string",
                            "emd_nm": "string",
                            "is_default": True,
                            "road_full_addr": "string",
                            "zip_no": "string",
                            "adm_cd": "string",
                            "bg_mgt_sn": "string",
                            "sgg_nm": "string",
                            "rn": "string"
                        }
                    ]
                }
            }
        },
        401: {
            "content": {
                "application/json": {
                    "example": {"message": "주소 조회에 실패하였습니다."}
                }
            }
        }
    },
    name = "주소 조회하기"
)
async def get_address_with_user_id(user_id: str, default: bool = False):
    user = User._load_user_info(db_session, user_id = user_id)
    if user:
        if default:
            result = Address.get_default_address(db_session, user.seq)  # type: ignore
            return JSONResponse(result, status_code = MACResult.SUCCESS.value)
        
        else:
            result = Address.get_address(db_session, user.seq) #type: ignore
            return JSONResponse(result, status_code = MACResult.SUCCESS.value)
        
    return JSONResponse({"message": "주소 조회에 실패하였습니다."}, status_code = MACResult.FAIL.value)
    
@address_router.put("/{user_id}",
    responses = {
        200: {
            "content": {
                "application/json": {
                    "example": {"message": "주소가 성공적으로 등록되었습니다."}
                }
            }
        },
        409: {
            "content": {
                "application/json": {
                    "example": {"message": "주소가 이미 등록되었습니다."}
                }
            }
        }
    },
    name = "주소 등록하기"
)
async def insert_address(user_id: str, data: AddressBody):
    response_dict = {
        MACResult.SUCCESS: "주소가 성공적으로 등록되었습니다.",
        MACResult.CONFLICT: "주소가 이미 등록되었습니다.",
        MACResult.INTERNAL_SERVER_ERROR: "서버 내부에러가 발생하였습니다."
    }
    
    user = User._load_user_info(db_session, user_id = user_id) #type: ignore
    if user:
        result = Address.insert_address(db_session, user.seq, data.road_full_addr, data.eng_addr, data.zip_no, data.adm_cd, data.rn_mgt_sn, data.bg_mgt_sn, data.si_nm, data.sgg_nm, data.emd_nm, data.rn, data.addr_detail) #type: ignore
        return JSONResponse({"message": response_dict[result]}, status_code = result.value)
        
    return JSONResponse({"message": "실패하였습니다"}, status_code = MACResult.FAIL.value)

@address_router.delete("/{user_id}",
    responses = {
        200: {
            "content": {
                "application/json": {
                    "example": {"message": "주소가 성공적으로 삭제되었습니다."}
                }
            }
        },
        401: {
            "content": {
                "application/json": {
                    "example": {"message": "주소 제거에 실패하였습니다."}
                }
            }
        }
    }
)
async def delete_address(user_id: str, road_full_addr: str):
    response_dict = {
        MACResult.SUCCESS: "주소가 성공적으로 삭제되었습니다.",
        MACResult.FAIL: "주소 제거에 실패하였습니다.",
        MACResult.INTERNAL_SERVER_ERROR: "서버 내부에러가 발생하였습니다."
    }
    
    user = User._load_user_info(db_session, user_id = user_id) # type: ignore
    if user:
        result = Address.delete_address(db_session, user.seq, road_full_addr) # type: ignore
        return JSONResponse({"message": response_dict[result]}, status_code = result.value)
        
    return JSONResponse({"message": response_dict[MACResult.FAIL]}, status_code = MACResult.FAIL.value)

@address_router.post("/{user_id}",
    responses = {
        200: {
            "content": {
                "application/json": {
                    "example": {"message": "기본 배송지가 변경되었습니다."}
                }
            }
        },
        401: {
            "content": {
                "application/json": {
                    "example": {"message": "기본 배송지 변경에 실패하였습니다."}
                }
            }
        },
    }                     
)
async def set_default_address(user_id: str, road_full_addr: str):
    response_dict = {
        MACResult.SUCCESS: "기본 배송지가 변경되었습니다.",
        MACResult.FAIL: "기본 배송지 변경에 실패하였습니다.",
        MACResult.INTERNAL_SERVER_ERROR: "서버 내부에러가 발생하였습니다."
    }
    
    user = User._load_user_info(db_session, user_id = user_id)
    if user:
        result = Address.set_default_address(db_session, user.seq, road_full_addr) # type: ignore
        return JSONResponse({"message": response_dict[result]}, status_code = result.value)
    
    return JSONResponse({"message": response_dict[MACResult.FAIL]}, status_code = MACResult.FAIL.value)
