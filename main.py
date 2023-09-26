from fastapi.responses import JSONResponse
from database.settings import DBSettings
from database.conn import DBConnector
from database.models.user import *
from fastapi import FastAPI
import uvicorn

app = FastAPI()
conn = DBConnector.connection()

@app.get("/")
async def index():
    return {
        "hello": "World"
    }
    
@app.put("/signup")
async def signup(model: SignUpModel):
    result = User.signup(conn, model.user_id, model.password, model.name, model.email, model.phone, model.idnum, model.address_seq)
    
    if result == UserResult.SUCCESS:
        return JSONResponse({"message": "성공"}, status_code = 200)
    
    if result == UserResult.FAIL:
        return JSONResponse({"message": "실패"}, status_code = 401)

    if result == UserResult.INTERNAL_SERVER_ERROR:
        return JSONResponse({"message": "서버 에러"}, status_code=500)

@app.post("/check/id",
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
        500: {
            "content": {
                "application/json": {
                    "example": {"message": "서버 내부 에러가 발생하였습니다."}
                }
            }
        }
    },
)
async def check_duplicate_id(id: str):
    response_dict = {
        UserResult.SUCCESS: "아이디가 사용 가능합니다!",
        UserResult.CONFLICT: "아이디가 이미 사용중입니다.",
        UserResult.INTERNAL_SERVER_ERROR: "서버 내부 에러가 발생하였습니다."
    }
    result = User.check_duplicate(conn, id)
    return JSONResponse({"message": response_dict[result]}, status_code = result.value)

@app.post("/check/email",
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
        500: {
            "content": {
                "application/json": {
                    "example": {"message": "서버 내부 에러가 발생하였습니다."}
                }
            }
        }
    },
)
async def check_duplicate_email(email: str):
    response_dict = {
        UserResult.SUCCESS: "아이디가 사용 가능합니다!",
        UserResult.CONFLICT: "아이디가 이미 사용중입니다.",
        UserResult.INTERNAL_SERVER_ERROR: "서버 내부 에러가 발생하였습니다."
    }
    result = User.check_duplicate(conn, email)
    return JSONResponse({"message": response_dict[result]}, status_code = result.value)

    
    
if __name__ == "__main__":
    if not DBSettings.check_exist_table(conn, "user"):
        DBSettings.create_user_table(conn)
    uvicorn.run("main:app", host="localhost", port=8080, reload=True)