from pydantic import BaseModel
from db_models import DashboardRequestStatus, UserDashboardRequestsModel

class DashboardRequestInfo(BaseModel):
    job_input_size: int
    job_output_size: int
    job_count: int
    concurrent_jobs: int
    dagman: bool
    local_universe: bool


    @staticmethod
    def from_db_model(db_model: "UserDashboardRequestsModel") -> "DashboardRequestInfo":
        return DashboardRequestInfo(
            job_input_size = db_model.job_input_size_gb,
            job_output_size = db_model.job_output_size_gb,
            job_count = db_model.job_count,
            concurrent_jobs = db_model.concurrent_jobs,
            dagman = db_model.dagman,
            local_universe = db_model.local_universe,
        )

class UserInfo(BaseModel):
    user_id: str
    ldap_authorized: bool
    dashboard_status: DashboardRequestStatus
    dashboard_info: DashboardRequestInfo | None = None

