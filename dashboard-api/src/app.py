from typing import Union

from fastapi import FastAPI, HTTPException, Request, Depends
from auth_handler import verify_auth_headers
from ldap_utils import check_ldap_user_in_group
from api_models import UserInfo, DashboardRequestInfo
from db import *
from notification_emails import send_dashboard_request_notification
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
    register_user_if_not_exists(request.state.user_id)
    dashboard_status, dashboard_info = get_dashboard_status_for_netid(request.state.user_id)
    return UserInfo(
        user_id=request.state.user_id,
        ldap_authorized=check_ldap_user_in_group(request.state.user_id),
        dashboard_status=dashboard_status,
        dashboard_info=dashboard_info,
    )

@app.post("/ap-request")
def submit_ap_dashboard_request(dashboard_request: DashboardRequestInfo, request: Request) -> dict[str, str]:
    register_user_dashboard_request(request.state.user_id, dashboard_request)
    send_dashboard_request_notification(request.state.user_id, dashboard_request)
    return {"result":"ok"}

