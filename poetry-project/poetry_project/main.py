from fastapi import Depends, FastAPI, Request, UploadFile, File
from fastapi.responses import JSONResponse
import os
from fastapi.staticfiles import StaticFiles
import shutil
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

staticDirectory = "./static"
uploadsDirectory = os.path.join(staticDirectory,"uploads")
app = FastAPI()

try:
    from .config import env
except ModuleNotFoundError as e:
    shutil.copyfile("./poetry_project/config.py.sample", "./poetry_project/config.py")
    from .config import env

if not os.path.exists(staticDirectory):
    os.mkdir(staticDirectory)
    
if not os.path.exists(uploadsDirectory):
    os.mkdir(uploadsDirectory)
    
if env["baseURL"] != "":
    myHostName = env["baseURL"]
else:
    myHostName = None

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http") # 認証に関する処理
async def auth(request: Request, call_next):
    if(not request.method in ["GET", "OPTIONS"]):
        if "authorization" in request.headers.keys():
                if request.headers["authorization"] == env["ils_auth"]:
                    return await call_next(request)
                else:
                    content = {"info":"discord"}
        else:
            content = {"info":"The request header does not contain the credentials. 'authorization=token' like"}
        return JSONResponse(status_code=401, content=content)
    else:
        return await call_next(request)
    
@app.middleware("http")
async def getMyHostName(request : Request, call_next):
    global myHostName
    if myHostName == None:
        myHostName = request.base_url
    return await call_next(request)

@app.get("/")
def read_root():
    status_code = 404;
    body =  {"message": "Specify the resource."}
    return JSONResponse(status_code=status_code, content=body)

@app.post("/image")
async def post_image(file: UploadFile):
    # ファイル名の決定
    fileName = f"{int(datetime.now().timestamp()*1e+6)}_{file.filename}"
    with open(f"./static/uploads/{fileName}", "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"message": "success.","url":f"{myHostName}static/uploads/{fileName}"}

@app.put("/image/{fileName}")
def put_image(fileName : str, file: UploadFile):
    with open(f"./static/uploads/{fileName}", "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"message": "success.","url":f"{myHostName}static/uploads/{fileName}"}

@app.delete("/image/{fileName}")
def delete_image(fileName : str):
    os.remove(f"./static/uploads/{fileName}")
    return {"message": "success."}