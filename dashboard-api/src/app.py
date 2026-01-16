from typing import Union

from fastapi import FastAPI, HTTPException, Request, Depends
from auth_handler import verify_auth_headers
from ldap_utils import check_ldap_user_in_group
from models import UserInfo
import re

app = FastAPI()

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    auth_info = verify_auth_headers(request)
    if auth_info is None:
        return HTTPException(status_code=401, detail="Unauthorized")
    elif "eppn" not in auth_info:
        return HTTPException(status_code=500, detail="Missing claims in token")
    request.state.user_id = re.sub(r'@.*','', auth_info["eppn"])
    response = await call_next(request)
    return response

@app.get("/")
def get_user_info(request: Request) -> UserInfo:
    print(f"User ID: {request.state.user_id}")
    return UserInfo(
        user_id=request.state.user_id,
        ldap_authorized=check_ldap_user_in_group(request.state.user_id)
    )
