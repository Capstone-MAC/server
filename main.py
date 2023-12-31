from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from database.models import *
from fastapi import FastAPI
from routers import *
import uvicorn

def custom_openapi():
    if not app.openapi_schema:
        app.openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            terms_of_service=app.terms_of_service,
            contact=app.contact,
            license_info=app.license_info,
            routes=app.routes,
            tags=app.openapi_tags,
            servers=app.servers,
        )
        for _, method_item in app.openapi_schema.get('paths').items(): #type: ignore
            for _, param in method_item.items():
                responses = param.get('responses')
                
                if '422' in responses:
                    del responses['422']

                responses['500'] = {
                    "description": "Internal Server Error",
                    "content": {
                        "application/json": {
                            "example": {"message": "서버 내부 에러가 발생하였습니다."}
                        }
                    }
                }

    return app.openapi_schema

app = FastAPI(swagger_ui_parameters={"syntaxHighlight.theme": "nord"})
app.openapi = custom_openapi
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user_router)
app.include_router(address_router)
app.include_router(item_router)
app.include_router(item_image_router)

    
if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)