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


class LiveDashboardStatus(BaseModel):
    # Populated by reading pod status from k8s API
    pod_health: str
    pod_health_reason: str


    # Populated by running condor_status against the AP's condor collector
    collector_health: str
    collector_health_reason: str

    # Populated by sending an HTTP request to the AP's dashboard web server
    dashboard_health: str
    dashboard_health_reason: str

class UserInfo(BaseModel):
    user_id: str
    chtc_account: bool
    ldap_authorized: bool
    dashboard_request_status: DashboardRequestStatus
    dashboard_request_info: DashboardRequestInfo | None
    live_dashboard_status: LiveDashboardStatus | None = None
