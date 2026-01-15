from typing import Union

from fastapi import FastAPI, HTTPException, Request, Depends
from auth_handler import verify_auth_headers
import jwt

app = FastAPI()

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    auth_info = verify_auth_headers(request)
    request.state.auth_info = auth_info
    if auth_info is None:
        return HTTPException(status_code=401, detail="Unauthorized")
    response = await call_next(request)
    return response

@app.get("/")
def read_root(request: Request) -> dict[str, str]:
    print(f"Auth info: {request.state.auth_info}")
    return {
        "message": "Hello, world!",
    }
