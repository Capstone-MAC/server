from fastapi.responses import JSONResponse, FileResponse
from database.models.item_images import ItemImages
from fastapi import APIRouter, UploadFile, File
from database.models.results import MACResult
from routers.env import db_session
from typing import Optional

item_image_router = APIRouter(
    prefix = "/item/images",
    tags = ["item"]
)

@item_image_router.get("/",
    responses={
        200: {
            "description": f"<img src='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRWnq7jeLUzceGdpxcXuVvh0_f0hiRz4ZiJmVPncOI&s' /> ",
            "content": None
        },
    },
    name = "상품 이미지 불러오기"
)
async def get_image(path: str):
    return FileResponse(path, media_type="image/png")

@item_image_router.get("/{item_seq}",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": [{
                        "path": "./images/41085b40-46fc-49ba-b93c-8101ca63ce6d.jpg",
                        "index": 0
                    }]
                }
            }
        }
    },
    name="상품 모든 이미지 경로 조회",
)
async def get_all_item_image_path(item_seq: int):
    paths = ItemImages.get_all_image_path(db_session, item_seq)
    return JSONResponse(paths, status_code = MACResult.SUCCESS.value)

@item_image_router.get("/{item_seq}/{index}",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "path": "./images/41085b40-46fc-49ba-b93c-8101ca63ce6d.jpg",
                    }
                }
            }
        }
    },
    name="상품 이미지 경로 조회",
)
async def get_item_image_path(item_seq: int, index: int = 0):
    path = ItemImages.get_image_path(db_session, item_seq, index)
    return JSONResponse({"path": path}, status_code = MACResult.SUCCESS.value)

@item_image_router.put("/{item_seq}/{index}",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {"message": "이미지를 성공적으로 업로드 하였습니다."}
                }
            }
        },
        409: {
            "content": {
                "application/json": {
                    "example": {"message": "해당 인덱스에 이미지가 존재합니다."}
                }
            }
        }
    },
    name = "이미지 업로드"
)
async def insert_item_image(item_seq: int, image: UploadFile = File(None, max_length=5*1024*1024), index: int = 0):
    response_dict = {
        MACResult.SUCCESS: "이미지를 성공적으로 업로드 하였습니다.",
        MACResult.CONFLICT: "해당 인덱스에 이미지가 존재합니다.",
        MACResult.INTERNAL_SERVER_ERROR: "서버 내부 에러가 발생하였습니다."
    }
    result = ItemImages.insert_image(db_session, item_seq, index, await image.read())
    
    return JSONResponse({"message": response_dict[result]}, status_code = result.value)

@item_image_router.delete("/{item_seq}/{index}",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {"message": "이미지를 성공적으로 제거하였습니다."}
                }
            }
        }
    },
    name="이미지 제거"
)
async def delete_item_image(item_seq: int, index:Optional[int] = None):
    objs = db_session.query(ItemImages).filter_by(item_seq = item_seq).all()
    result = None
    for obj in objs:
        if index and index == obj.index:
           result = obj.delete_image(db_session, item_seq, obj.path) # type: ignore
        
        else:
            result = obj.delete_image(db_session, item_seq, obj.path) # type: ignore
            if result == MACResult.INTERNAL_SERVER_ERROR:
                break
    
    if result is not None and result == MACResult.SUCCESS:
        db_session.commit()
        return JSONResponse({"message": "이미지를 성공적으로 제거하였습니다."})
           
    else:
        return JSONResponse({"message": "서버 내부 에러가 발생하였습니다."})
    