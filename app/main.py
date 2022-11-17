from typing import List
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi import Depends,status
from fastapi.responses import RedirectResponse,HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from hashlib import sha256
from os import path

app = FastAPI()

html = ""

SECRET = "secret-key"

manager = LoginManager(SECRET,token_url="/auth/login",use_cookie=True)
manager.cookie_name = "some-name"

DB = {"u":{"password":"a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"}} # hashed

@manager.user_loader
def load_user(username:str):
    
    user = DB.get(username)
    return user

@app.post("/auth/login")
def login(data: OAuth2PasswordRequestForm = Depends()):
    #hashed_username = hashlib.sha256(username.encode('utf-8')).hexdigest()
    username = data.username
    password =  sha256(data.password.encode('utf-8')).hexdigest()
    user = load_user(username)
    # user = load_user(username)
    if not user:
        raise Exception
    elif password != user["password"]:
        raise InvalidCredentialsException
    access_token = manager.create_access_token(
        data={"sub":username}
    )
    resp = RedirectResponse(url="/chat",status_code=status.HTTP_302_FOUND)
    manager.set_cookie(resp,access_token)
    return resp

@app.get("/chat")
def getPrivateendpoint(_=Depends(manager)):
    with open('index.html', 'r') as f:
        return HTMLResponse(f.read())


pth = path.dirname(__file__)

@app.get("/",response_class=HTMLResponse)
def loginwithCreds(request:Request):
    with open(path.join(pth, "login.html")) as f:
        return HTMLResponse(content=f.read())


@app.get("/")
async def get():
    return HTMLResponse(html)

class ConnectionManager:
    def __init__(self):
        self.connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    async def broadcast(self, data: str):
        for connection in self.connections:
            await connection.send_text(data)

    def disconnect(self, websocket: WebSocket):
        self.connections.remove(websocket)


manager2 = ConnectionManager()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager2.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager2.broadcast(f"Client {client_id}: {data}")
    except WebSocketDisconnect:
        manager2.disconnect(websocket)
        await manager2.broadcast(f"Client #{client_id} left the chat")
