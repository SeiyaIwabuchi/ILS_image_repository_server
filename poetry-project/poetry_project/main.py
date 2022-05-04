from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
import os
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI()

security = HTTPBasic()

@app.middleware("http")
async def auth(request: Request, call_next):
    print(request.headers.keys())
    if "authorization" in request.headers.keys():
        if "ils_auth" in os.environ.keys():
            if request.headers["authorization"] == os.environ["ils_auth"]:
                return await call_next(request)
            else:
                content = {"info":"discord"}
        else:
            content = {"info":"The authentication information is not registered in the server."}
    else:
        content = {"info":"The request header does not contain the credentials."}
    return JSONResponse(status_code=401, content=content)
    

@app.get("/")
def read_root():
    status_code = 404;
    body =  {"message": "Specify the resource."}
    return JSONResponse(status_code=status_code, content=body)


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}