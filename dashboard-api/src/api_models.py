from pydantic import BaseModel
from db_models import DashboardRequestStatus

class UserInfo(BaseModel):
    user_id: str
    ldap_authorized: bool
    dashboard_status: DashboardRequestStatus


class DashboardRequestInfo(BaseModel):
    job_input_size: int
    job_output_size: int
    job_count: int
    concurrent_jobs: int
    dagman: bool
    local_universe: bool
