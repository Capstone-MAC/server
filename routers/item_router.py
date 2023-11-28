from database.models.item import Item, Category
from database.models.results import MACResult
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Query
from routers.env import db_session
from typing import Optional

item_router = APIRouter(
    prefix = "/item",
    tags = ["item"]
)

@item_router.get("",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "seq": -1,
                        "name": "test",
                        "category": "디지털 기기",
                        "cnt": "1",
                        "price": "10,000",
                        "description": "테스트 기기입니다.",
                        "views": -1,
                        "created_at": "2023/11/28 04:19:53",
                        "images": [
                            {
                            "path": "./images/3942b44c-5e53-48ea-ad4a-3af2a7ba7030.jpg",
                            "index": 0
                            },
                            {
                            "path": "./images/2ed9af27-bc08-4e1f-afc6-25015b1b130a.jpg",
                            "index": 1
                            },
                            {
                            "path": "./images/ca0261af-119f-42dc-9b9b-0bdb53d2cdb8.jpg",
                            "index": 2
                            }
                        ]
                    }
                }
            }
        },
        401: {
            "content": {
                "application/json": {
                    "example": {"message": "아이템이 존재하지 않습니다."}
                }
            }
        }
    },
    name = "물품 자세히 조회하기"
)
# 
async def get_item(item_seq: int):
    item = Item.get_item_by_item_seq(db_session, item_seq)
    if item is None:
        return JSONResponse({"message": "아이템이 존재하지 않습니다."}, status_code = MACResult.FAIL.value)
    
    return JSONResponse(item.info(db_session), status_code = MACResult.SUCCESS.value)

@item_router.get("/search/{search_value}",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": [
                    {
                        "seq": 7,
                        "name": "test",
                    },
                    {
                        "seq": 8,
                        "name": "test2",
                    }
                ]}
            }
        },
        401: {
            "content": {
                "application/json": {
                    "example": []
                }
            }
        }
    },
    name = "아이템 검색하기",
    description = "검색 창에 뜨는 목록"
)
async def search_item(search_value: str, start: int = 0, count: int = 10):
    result = Item.search_items(db_session, search_value, start, count)
    if result is None or len(result) == 0:
        return JSONResponse([], status_code = MACResult.FAIL.value)

    else:
        return JSONResponse(result, status_code = MACResult.SUCCESS.value)

@item_router.get("/search_detail/{search_value}",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example":[
                        {
                            "seq": -1,
                            "name": "test",
                            "created_at": "15시간 전",
                            "price": 10000,
                            "saved_cnt": 0,
                            "image_path": "./images/3942b44c-5e53-48ea-ad4a-3af2a7ba7030.jpg"
                        },
                        {
                            "seq": -2,
                            "name": "test3",
                            "created_at": "12분 전",
                            "price": 10000,
                            "saved_cnt": 0,
                            "image_path": None
                        }
                    ]
                }
            }
        },
        401: {
            "content": {
                "application/json": {
                    "example": []
                }
            }
        }
    },
    name = "아이템 자세히 검색하기",
    description = "검색 탭에 뜨는 목록"
)
async def search_detail_item(search_value: str, start: int = 0, count: int = 10):
    result = Item.search_detail_items(db_session, search_value, start, count)
    if result is None or len(result) == 0:
        return JSONResponse([], status_code = MACResult.FAIL.value)

    else:
        return JSONResponse(result, status_code = MACResult.SUCCESS.value)

@item_router.get("/recommend",
    responses = {
        200: {
            "content": {
                "application/json": {
                    "example": [
                        {
                            "seq": -1,
                            "name": "test",
                            "created_at": "15시간 전",
                            "price": 10000,
                            "saved_cnt": 0,
                            "image_path": "./images/3942b44c-5e53-48ea-ad4a-3af2a7ba7030.jpg"
                        },
                        {
                            "seq": -2,
                            "name": "test3",
                            "created_at": "12분 전",
                            "price": 10000,
                            "saved_cnt": 0,
                            "image_path": None
                        }
                    ]
                }
            }
        }
    },
    name = "아이템 추천",
    description = "홈화면에서 나오는 아이템 추천"
)
async def recommend_item(start: int = 0, count: int = 10,):
    result = Item.get_recommended_item(db_session, start, count)
    if result is None or len(result) == 0:
        return JSONResponse([], status_code = MACResult.FAIL.value)
    
    else:
        return JSONResponse(result, status_code = MACResult.SUCCESS.value)


@item_router.put("/insert", 
    responses = {
        200: {
            "content": {
                "application/json": {
                    "example": {"message": "상품정보가 등록되었습니다."}
                }
            }
        },
        401: {
            "content": {
                "application/json": {
                    "example": {"message": "상품정보 입력에 실패하였습니다."}
                }
            }
        },
        422: {
            "content": {
                "application/json": {
                    "example": {"message": "유효한 카테고리가 아닙니다."}
                }
            }
        }
    },
    name = "상품 등록하기"
)
async def insert_item(name: str, cnt: int, price: int, description: str, category: str = Query(enum = Category.get_all_category_name(db_session))):
    response_dict = {
        MACResult.SUCCESS: "상품정보가 등록되었습니다.",
        MACResult.FAIL: "상품정보 입력에 실패하였습니다.",
        MACResult.ENTITY_ERROR: "유효한 카테고리가 아닙니다.",
        MACResult.INTERNAL_SERVER_ERROR: "서버 내부 에러가 발생하였습니다."
    }
    result = Item.insert_item_info(db_session, name, category, cnt, price, description)
    
    return JSONResponse({"message": response_dict[result]}, status_code = result.value)

@item_router.post("/update", 
    responses = {
        200: {
            "content": {
                "application/json": {
                    "example": {"message": "성공적으로 상품정보를 업데이트 하였습니다."}
                }
            }
        },
        401: {
            "content": {
                "application/json": {
                    "example": {"message": "상품 정보를 찾을 수 없습니다."}
                }
            }
        }
    },
    name = "상품 정보 업데이트 하기"
)
async def update_item(item_seq: int, name: Optional[str] = None, cnt: Optional[int] = None, price: Optional[int] = None, description: Optional[str] = None, views: Optional[int] = None):
    response_dict = {
        MACResult.SUCCESS: "성공적으로 상품정보를 업데이트 하였습니다.",
        MACResult.FAIL: "상품 정보를 찾을 수 없습니다.",
        MACResult.INTERNAL_SERVER_ERROR: "서버 내부 에러가 발생하였습니다."
    }
    item = Item.get_item_by_item_seq(db_session, seq = item_seq)
    if item is None:
        result = MACResult.FAIL
    
    else:
        result = item.update_item_info(db_session, name, cnt, price, description, views)
    
    return JSONResponse({"message": response_dict[result]}, status_code = result.value)

@item_router.delete("/delete", 
    responses = {
        200: {
            "content": {
                "application/json": {
                    "example": {"message": "상품이 성공적으로 제거되었습니다."}
                }
            }
        },
        401: {
            "content": {
                "application/json": {
                    "example": {"message": "상품 제거에 실패하였습니다."}
                }
            }
        }
    },
    name = "상품 삭제하기"
)
async def delete_item(item_seq: int):
    response_dict = {
        MACResult.SUCCESS: "상품이 성공적으로 제거되었습니다.",
        MACResult.FAIL: "상품 제거에 실패하였습니다.",
        MACResult.INTERNAL_SERVER_ERROR: "서버 내부 에러가 발생하였습니다."
    }
    
    item = Item.get_item_by_item_seq(db_session, item_seq)
    if item is None:
        result = MACResult.FAIL
    else:
        result = item.delete_item(db_session)
        
    return JSONResponse({"message": response_dict[result]}, status_code = result.value)

