from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
import re
from .auth_handler import verify_auth_headers
from .userapp_utils import update_user_state_from_userapp, UserAppUserStatus
from .api_models import UserInfo, DashboardRequestInfo, ChtcAccountStatus
from . import db as db
from .db_models import RequestStatus
from . import notification_emails as ne
from .ap_status import get_live_dashboard_status
from .poll_user_status import start as start_scheduler, stop as stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    auth_info = verify_auth_headers(request, request.app)
    if auth_info is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    elif "eppn" not in auth_info:
        raise HTTPException(status_code=500, detail="Missing claims in token")
    request.state.user_id = re.sub(r'@.*','', auth_info["eppn"])
    response = await call_next(request)
    return response

@app.get("/")
def get_user_info(request: Request) -> UserInfo:
    print(f"User ID: {request.state.user_id}")

    print("Getting user info")
    # First, check the last-observed state of the user in the local DB
    user = db.get_or_register_user(request.state.user_id)
    
    # If the user is not fully registered yet, check LDAP to see if their account is fully registered
    if user.chtc_account != RequestStatus.COMPLETE or user.spark_account != RequestStatus.COMPLETE:
        print(f"User state is chtc: {user.chtc_account} spark: {user.spark_account}. Checking the UserApp for updates")
        # Check LDAP to see if either phase of account registration has progressed from the state in the local DB
        user_status = update_user_state_from_userapp(request.state.user_id, UserAppUserStatus(user.chtc_account, user.spark_account))
        
        # Update the user's state in the local DB
        if user_status.chtc_account != user.chtc_account or user_status.spark_account != user.spark_account:
            user = db.update_user(request.state.user_id, user_status)
    
    print("Checking for pending dashboard requests from user.")
    # Then, check if the user is far along enough in the enrollment process to have requested
    # a dashboard
    dashboard_status, dashboard_info = db.get_user_dashboard_status(request.state.user_id)
    
    print("Checking live dashboard status.")
    # If so, query the k8s API for the running dashboard's status
    running_dashboard_status = get_live_dashboard_status(request.state.user_id) if dashboard_status == RequestStatus.COMPLETE else None
    if running_dashboard_status and user.assistance_requested:
        running_dashboard_status.assistance_requested = True
    
    # Return all known information about the user's state for display on the frontend
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
    ne.send_dashboard_request_notification(request.state.user_id, dashboard_request)
    return {"result":"ok"}


@app.delete("/ap-request")
def delete_ap_dashboard_request(request: Request) -> dict[str, str]:
    db.cancel_user_dashboard_request(request.state.user_id)
    ne.send_dashboard_cancellation_notification(request.state.user_id)
    return {"result":"ok"}


@app.post("/ap-repair-request")
def submit_ap_repair_request(request: Request) -> dict[str, str]:
    db.mark_user_assistance_requested(request.state.user_id)
    current_status = get_live_dashboard_status(request.state.user_id)
    ne.send_ap_repair_requested_notification(request.state.user_id, current_status)
    return {"result":"ok"}


@app.post("/slurm-request")
def submit_slurm_account_request(request: Request) -> dict[str, str]:
    db.request_slurm_account(request.state.user_id)
    ne.send_slurm_account_requested_notification(request.state.user_id)
    return {"result":"ok"}
