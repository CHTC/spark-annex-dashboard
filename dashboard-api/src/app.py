from typing import Union

from fastapi import FastAPI, HTTPException, Request, Depends
from auth_handler import verify_auth_headers
from ldap_utils import check_ldap_user_in_group
from api_models import UserInfo, DashboardRequestInfo, ChtcAccountStatus
import db
from notification_emails import *
from ap_status import get_live_dashboard_status
import re

app = FastAPI()

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    auth_info = verify_auth_headers(request, request.app)
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
    user_status = check_ldap_user_in_group(request.state.user_id)
    user = db.register_user_if_not_exists(request.state.user_id, user_status)
    dashboard_status, dashboard_info = db.get_user_dashboard_status(request.state.user_id)
    running_dashboard_status = get_live_dashboard_status(request.state.user_id) if dashboard_status == db.RequestStatus.COMPLETE else None
    return UserInfo(
        user_id=request.state.user_id,
        chtc_account=ChtcAccountStatus(
            chtc_account=user.chtc_account,
            spark_account=user.spark_account),
        dashboard_request_status=dashboard_status,
        dashboard_request_info=dashboard_info,
        live_dashboard_status=running_dashboard_status
    )

@app.post("/ap-request")
def submit_ap_dashboard_request(dashboard_request: DashboardRequestInfo, request: Request) -> dict[str, str]:
    db.register_user_dashboard_request(request.state.user_id, dashboard_request)
    send_dashboard_request_notification(request.state.user_id, dashboard_request)
    return {"result":"ok"}


@app.delete("/ap-request")
def delete_ap_dashboard_request(request: Request) -> dict[str, str]:
    db.cancel_user_dashboard_request(request.state.user_id)
    send_dashboard_cancellation_notification(request.state.user_id)
    return {"result":"ok"}
