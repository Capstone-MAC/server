from database.models.user import User, SignUpModel, SignoutModel, LoginModel, ForgotPasswordModel
from fastapi import APIRouter, UploadFile, File
from database.models.purchase import Purchase
from database.models.results import MACResult
from starlette.responses import FileResponse
from routers.env import db_session, session
from fastapi.responses import JSONResponse
from typing import Optional
import logging

user_router = APIRouter(
    prefix="/user",
    tags=["user"]
)

@user_router.put("/signup", 
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {"message": "회원가입에 성공하였습니다!"}
                }
            }
        },
        401: {
            "content": {
                "application/json": {
                    "example": {"message": "회원가입에 실패하였습니다."}
                }
            }
        },
        409: {
            "content": {
                "application/json": {
                    "example": {"message": "이미 등록된 계정 또는 이메일 입니다."}
                }
            }
        }
    },
    name = "회원 가입"
)
async def signup(model: SignUpModel):
    response_dict = {
        MACResult.SUCCESS: "회원가입에 성공하였습니다.",
        MACResult.FAIL: "회원가입에 실패하였습니다.",
        MACResult.CONFLICT: "이미 등록된 계정 또는 이메일 입니다.",
        MACResult.INTERNAL_SERVER_ERROR: "서버 내부 에러가 발생하였습니다."
    }
    result = User.signup(db_session, model.user_id, model.password, model.name, model.email, model.phone, model.idnum)
    
    return JSONResponse({"message": response_dict[result]}, status_code = result.value)


@user_router.delete("/signout", 
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {"message": "회원탈퇴에 성공하였습니다."}
                }
            }
        },
        401: {
            "content": {
                "application/json": {
                    "example": {"message": "회원탈퇴에 실패하였습니다."}
                }
            }
        },
        408: {
            "content": {
                "application/json": {
                    "example": {"message": "세션이 만료되었습니다."}
                }
            }
        }
    },
    name = "회원 탈퇴"
)
async def signout(model: SignoutModel):
    response_dict = {
        MACResult.SUCCESS: "회원탈퇴에 성공하였습니다.",
        MACResult.FAIL: "회원탈퇴에 실패하였습니다.",
        MACResult.TIME_OUT: "세션이 만료되었습니다.",
        MACResult.INTERNAL_SERVER_ERROR: "서버 내부 에러가 발생하였습니다."
    }
    
    result = MACResult.FAIL
    user = User._load_user_info(db_session, user_id = model.user_id)
    if user:
        if User.login(db_session, session, model.user_id, model.password) == MACResult.SUCCESS:
            result = user.signout(db_session, session)
    
    return JSONResponse({"message": response_dict[result]}, status_code = result.value)


@user_router.post("/login",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {"message": "로그인에 성공하였습니다."}
                }
            }
        },
        401: {
            "content": {
                "application/json": {
                    "example": {"message": "아이디 또는 비밀번호가 일치하지 않습니다."}
                }
            }
        }
    },
    name = "로그인"
)
async def login(model: LoginModel):
    response_dict = {
        MACResult.SUCCESS: "로그인에 성공하였습니다.",
        MACResult.FAIL: "아이디 또는 비밀번호가 일치하지 않습니다.",
        MACResult.INTERNAL_SERVER_ERROR: "서버 내부 에러가 발생하였습니다."
    }
    
    result = User.login(db_session, session, model.user_id, model.password)
    
    return JSONResponse({"message": response_dict[result]}, status_code = result.value)


@user_router.post("/logout",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {"message": "성공적으로 로그아웃 하였습니다."}
                }
            }
        },
        401: {
            "content": {
                "application/json": {
                    "example": {"message": "로그아웃에 실패하였습니다."}
                }
            }
        },
        408: {
            "content": {
                "application/json": {
                    "example": {"message": "세션이 만료되었습니다."}
                }
            }
        }
    },
    name = "로그아웃"
)
async def logout(user_id: str):
    response_dict = {
        MACResult.SUCCESS: "성공적으로 로그아웃 하였습니다",
        MACResult.FAIL: "로그아웃에 실패하였습니다.",
    }
    
    user = User._load_user_info(db_session, user_id = user_id)
    if user:
        result = user.logout(db_session, session)
    else:
        result = MACResult.FAIL
    
    return JSONResponse({"message": response_dict[result]}, status_code = result.value)

@user_router.post("/update",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {"message": "성공적으로 정보를 변경하였습니다."}
                }
            }
        },
        401: {
            "content": {
                "application/json": {
                    "example": {"message": "정보 변경에 실패하였습니다."}
                }
            }
        },
        409: {
            "content": {
                "application/json": {
                    "example": {"message": "이미 해당 이메일이 존재합니다."}
                }
            }
        },
    },
    name = "정보 변경하기"
)
async def update_info(user_id: str, name: Optional[str] = None, email: Optional[str] = None, phone: Optional[str] = None):
    response_dict = {
        MACResult.SUCCESS: "성공적으로 정보를 변경하였습니다.",
        MACResult.FAIL: "정보 변경에 실패하였습니다.",
        MACResult.CONFLICT: "이미 해당 이메일이 존재합니다.",
        MACResult.INTERNAL_SERVER_ERROR: "서버 내부 에러가 발생하였습니다."
    }
    
    user = User._load_user_info(db_session, user_id = user_id)
    result = MACResult.FAIL
    if user:
        result = user.update_info(db_session, user_id, name, email, phone)
    
    return JSONResponse({"message": response_dict[result]}, status_code = result.value)
        
@user_router.post("/forgot/id",
   responses={
        200: {
            "content": {
                "application/json": {
                    "example": {"message": "아이디는 'admin' 입니다."}
                }
            }
        },
        401: {
            "content": {
                "application/json": {
                    "example": {"message": "정보 변경에 실패하였습니다."}
                }
            }
        }
    },
   name = "아이디 찾기"               
)
async def forgot_id(email: str):
    try:
        user = User._load_user_info(db_session, email = email)
        if user is None:
            return JSONResponse({"message": "아이디 찾기에 실패하였습니다."}, status_code = MACResult.FAIL.value)

        else:
            return JSONResponse({"message": f"아이디는 {user.user_id} 입니다."}, status_code = MACResult.SUCCESS.value)
    
    except:
        return JSONResponse({"message": "서버 내부 에러가 발생하였습니다."}, status_code = MACResult.INTERNAL_SERVER_ERROR.value)

@user_router.post("/forgot/password",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {"message": "성공적으로 정보를 변경하였습니다."}
                }
            }
        },
        401: {
            "content": {
                "application/json": {
                    "example": {"message": "정보 변경에 실패하였습니다."}
                }
            }
        }
    },
    name = "비밀번호 변경")
async def forgot_password(model: ForgotPasswordModel):
    response_dict = {
        MACResult.SUCCESS: "성공적으로 정보를 변경하였습니다.",
        MACResult.FAIL: "정보 변경에 실패하였습니다.",
        MACResult.INTERNAL_SERVER_ERROR: "서버 내부 에러가 발생하였습니다."
    }
    
    result = User.forgot_password(db_session, session, model.user_id, model.password)
    
    return JSONResponse({"message": response_dict[result]}, status_code = result.value)

@user_router.post("/check/id",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {"message": "아이디가 사용 가능합니다!"}
                }
            }
        },
        409: {
            "content": {
                "application/json": {
                    "example": {"message": "아이디가 이미 사용중입니다."}
                }
            }
        },
        422: {
            "content": {
                "application/json": {
                    "example": {"message": "아이디와 이메일중 하나만 입력하세요."}
                }
            }
        }
    },
    name = "아이디 중복 체크"
)
async def check_duplicate_id(id: str):
    response_dict = {
        MACResult.SUCCESS: "아이디가 사용 가능합니다!",
        MACResult.CONFLICT: "아이디가 이미 사용중입니다.",
        MACResult.ENTITY_ERROR: "아이디와 이메일중 하나만 입력하세요.",
        MACResult.INTERNAL_SERVER_ERROR: "서버 내부 에러가 발생하였습니다."
    }
    result = User.check_duplicate(db_session, user_id = id)
    return JSONResponse({"message": response_dict[result]}, status_code = result.value)


@user_router.post("/check/email",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {"message": "이메일이 사용 가능합니다!"}
                }
            }
        },
        409: {
            "content": {
                "application/json": {
                    "example": {"message": "이메일이 이미 사용중입니다."}
                }
            }
        },
        422: {
            "content": {
                "application/json": {
                    "example": {"message": "아이디와 이메일중 하나만 입력하세요."}
                }
            }
        }
    },
    name = "이메일 중복 체크"
)
async def check_duplicate_email(email: str):
    response_dict = {
        MACResult.SUCCESS: "이메일이 사용 가능합니다!",
        MACResult.CONFLICT: "이메일이 이미 사용중입니다.",
        MACResult.ENTITY_ERROR: "아이디와 이메일중 하나만 입력하세요.",
        MACResult.INTERNAL_SERVER_ERROR: "서버 내부 에러가 발생하였습니다."
    }
    result = User.check_duplicate(db_session, email = email)
    return JSONResponse({"message": response_dict[result]}, status_code = result.value)


@user_router.get("/items", 
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": [
                        {
                            "seq": -1,
                            "name": "test2",
                            "created_at": "2023년 11월 28일",
                            "price": 10000,
                            "saved_cnt": 2,
                            "image_path": "./images/1687e0e2-45bc-4a31-b506-db3edb933772.jpg"
                        },
                        {
                            "seq": -2,
                            "name": "test3",
                            "created_at": "2023년 11월 28일",
                            "price": 10000,
                            "saved_cnt": 1,
                            "image_path": None
                        }
                    ]
                }
            }
        },
        401: {
            "content": {
                "application/json": {
                    "example": {"message": "유저 아이디가 잘못 입력되었습니다."}
                }
            }
        },
    },
    name = "상품 목록 조회하기"
)
async def load_save_items(user_id: str):
    user = User._load_user_info(db_session, user_id = user_id)
    if user:
        items = user.load_saved_items(db_session)
        if items:
            return JSONResponse(list(map(lambda x: x.recommend(db_session), items)), status_code = MACResult.SUCCESS.value)
        
    return JSONResponse({"message": "유저 아이디가 잘못 입력되었습니다."}, status_code=MACResult.FAIL.value) 
    

@user_router.post("/items/update", 
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {"message": "성공적으로 변경하였습니다."}
                }
            }
        },
        401: {
            "content": {
                "application/json": {
                    "example": {"message": "변경에 실패하였습니다."}
                }
            }
        },
        409: {
            "content": {
                "application/json": {
                    "example": {"message": "데이터 충돌이 일어났습니다."}
                }
            }
        }
    },
    name = "상품 목록 업데이트 하기"
)
async def update_saved_items(user_id: str, item_seq: int):
    response_dict = {
        MACResult.SUCCESS: "성공적으로 변경하였습니다.",
        MACResult.FAIL: "변경에 실패하였습니다.",
        MACResult.INTERNAL_SERVER_ERROR: "서버 내부 에러가 발생하였습니다.",
    }
    
    user = User._load_user_info(db_session, user_id = user_id)
    if user:
        result = user.update_saved_items(db_session, item_seq)
        
    else:
        logging.error("유저가 존재하지 않습니다.")
        result = MACResult.INTERNAL_SERVER_ERROR
    
    return JSONResponse({"message": response_dict[result]}, status_code = result.value)

@user_router.get("/profile",
    responses={
        200: {
            "description": f"<img src='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRWnq7jeLUzceGdpxcXuVvh0_f0hiRz4ZiJmVPncOI&s' /> ",
            "content": None
        },
        408: {
            "content": {
                "application/json": {
                    "example": {"message": "세션이 만료되었습니다."}
                }
            }
        }
    },
    name = "프로필 이미지 불러오기"
)
async def profile(path: str):
    return FileResponse(path, media_type="image/png")

@user_router.post("/profile/update",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {"message": "이미지를 성공적으로 변경하였습니다!"}
                }
            }
        },
        401: {
            "content": {
                "application/json": {
                    "example": {"message": "이미지 변경에 실패하였습니다."}
                }
            }
        },
        408: {
            "content": {
                "application/json": {
                    "example": {"message": "세션이 만료되었습니다."}
                }
            }
        }
    },
    name = "프로필 이미지 업데이트"
)
async def update_profile(user_id: str, file: UploadFile = File(None)):
    response_dict = {
        MACResult.SUCCESS: "이미지를 성공적으로 변경하였습니다!",
        MACResult.FAIL: "이미지 변경에 실패하였습니다.",
        MACResult.TIME_OUT: "세션이 만료되었습니다.",
        MACResult.INTERNAL_SERVER_ERROR: "서버 내부 에러가 발생하였습니다."
    }
    user = User._load_user_info(db_session, user_id = user_id)
    if user:
        result = user.update_profile_image(db_session, session, None if file is None else await file.read())
    
    else:
        logging.error("유저가 존재하지 않습니다.")
        result = MACResult.INTERNAL_SERVER_ERROR
                
    return JSONResponse({"message": response_dict[result]}, status_code = result.value)

@user_router.post("/email/send",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {"message": "메일을 성공적으로 전송하였습니다!"}
                }
            }
        },
        401: {
            "content": {
                "application/json": {
                    "example": {"message": "메일 전송에 실패하였습니다."}
                }
            }
        }
    },
    name = "이메일 전송하기"
)
async def send_email(email: str):
    response_dict = {
        MACResult.SUCCESS: "메일을 성공적으로 전송하였습니다!",
        MACResult.FAIL: "메일 전송에 실패하였습니다.",
        MACResult.INTERNAL_SERVER_ERROR: "서버 내부 에러가 발생하였습니다."
    }
    
    result = User.send_email(session, email)
    return JSONResponse({"message": response_dict[result]}, status_code = result.value)

@user_router.post("/email/verify", 
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {"message": "성공적으로 인증되었습니다!"}
                }
            }
        },
        401: {
            "content": {
                "application/json": {
                    "example": {"message": "인증에 실패하였습니다."}
                }
            }
        },
        408: {
            "content": {
                "application/json": {
                    "example": {"message": "세션이 만료되었습니다."}
                }
            }
        }
    },
    name = "이메일 인증"
)
async def verify_email(email: str, verify_code: str):
    response_dict = {
        MACResult.SUCCESS: "성공적으로 인증되었습니다!",
        MACResult.FAIL: "인증에 실패하였습니다.",
        MACResult.TIME_OUT: "세션이 만료되었습니다.",
        MACResult.INTERNAL_SERVER_ERROR: "서버 내부 에러가 발생하였습니다."
    }
    
    result = User.verify_email_code(session, email, verify_code)
    return JSONResponse({"message": response_dict[result]}, status_code = result.value)

@user_router.get("/{user_id}", 
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "seq": -1,
                        "user_id": "admin",
                        "name": "admin",
                        "email": "admin@admin.com",
                        "phone": "01000000000",
                        "idnum": "0001013000000",
                        "profile": "./images/ec12de1a-64e0-11ee-b17f-eb74bf123164.jpg",
                        "address_seq": "-1",
                        "signup_date": "2023-10-06T00:09:25",
                        "password_update_date": "2023-10-06T00:09:25",
                        "last_login": "2023-10-06T01:30:36",
                        "saved_items": "[3, 5]",
                        "saved_categories": "[1, 2]"
                    }
                }
            }
        },
        403: {
            "content": {
                "application/json": {
                    "example": {"message": "접근 권한이 없습니다."}
                }
            }
        },
        404: {
            "content": {
                "application/json": {
                    "example": {"message": "조건을 만족하는 유저가 없습니다."}
                }
            }
        }
    },
    name = "유저 정보 조회하기",
    description = "API KEY 필요"
)
async def info(user_id: str):
    user = User._load_user_info(db_session, user_id = user_id)
    if user:
        return user.info
    
    else:
        return JSONResponse({"message": "조건을 만족하는 유저가 없습니다."}, status_code = MACResult.NOT_FOUND.value)

@user_router.post("/purchase",
    responses = {
        200: {
            "content": {
                "application/json": {
                    "example": {"message": "성공적으로 구매 신청하였습니다."}
                }
            }
        },
        404: {
            "content": {
                "aplication/json": {
                    "example": {"message": "사용자를 찾을 수 없습니다."}
                }
            }
        },
        409: {
            "content": {
                "application/json": {
                    "example": {"message": "이미 구매중인 상품입니다."}
                }
            }
        }
    },
    name = "상품 구매 요청하기"
)
async def purchase(user_id: str, item_seq: int):
    response_dict = {
        MACResult.SUCCESS: "성공적으로 구매 신청하였습니다.",
        MACResult.NOT_FOUND: "사용자를 찾을 수 없습니다.",
        MACResult.CONFLICT: "이미 구매중인 상품입니다.",
        MACResult.INTERNAL_SERVER_ERROR: "서버 내부 에러가 발생하였습니다."
    }
    user = User._load_user_info(db_session, user_id = user_id)
    result = MACResult.NOT_FOUND
    if user:
        result = user.purchase(db_session, item_seq)
    
    return JSONResponse({"message": response_dict[result]}, status_code = result.value)

@user_router.get("/purchase/list",
    responses = {
        200: {
            "content": {
                "application/json": {
                    "example": [
                        {
                            "seq": -1,
                            "name": "test_product",
                            "created_at": "51분 전",
                            "price": 10000,
                            "saved_cnt": 0,
                            "image_path": None
                        }
                    ]
                }
            }
        },
        404: {
            "content": {
                "application/json": {
                    "example": {"message": "사용자를 찾을 수 없습니다."}
                }
            }
        }
    },
    name = "구매중인 상품 목록 불러오기"
)
async def get_purchase_list(user_id: str):
    user = User._load_user_info(db_session, user_id = user_id)
    if user:
        result = Purchase.get_purchase_item_list(db_session, user.seq) # type: ignore
        return JSONResponse(result, status_code = MACResult.SUCCESS.value)
    
    else:
        return JSONResponse({"message": "사용자를 찾을 수 없습니다."}, status_code = MACResult.NOT_FOUND.value)
    