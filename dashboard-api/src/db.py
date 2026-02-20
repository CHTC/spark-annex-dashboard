from sqlalchemy import create_engine, select, delete
from sqlalchemy.orm import sessionmaker, Session, joinedload
from os import environ
from typing import Optional
import urllib.parse
from db_models import *
from api_models import DashboardRequestInfo
from ldap_utils import UserLDAPStatus

from fastapi import HTTPException

db_path = environ.get("DASHBOARD_DB_PATH", "sqlite:///tmp/dashboard.db")


engine = create_engine(db_path)

Base.metadata.create_all(engine)

DbSession = sessionmaker(bind=engine)


def register_user_if_not_exists(netid: str):
    """ Given a user ID, create a user entry in the database """
    with DbSession() as session:
        user = session.scalar(select(UserModel).where(UserModel.netid == netid))

        if user is None:
            user = UserModel(netid = netid)
            session.add(user)
            session.commit()

def get_user_dashboard_status(netid: str) -> tuple[DashboardRequestStatus, DashboardRequestInfo | None]:
    """ Given a user ID, return the status of that user's dashboard request."""
    with DbSession() as session:
        user = session.scalar(select(UserModel).where(UserModel.netid == netid))
        active_request = session.scalar(select(UserDashboardRequestsModel)
            .where(UserDashboardRequestsModel.user_id == user.id)
            .where(UserDashboardRequestsModel.request_status != DashboardRequestStatus.DELETED)
        )
        if not active_request:
            return DashboardRequestStatus.NOT_REQUESTED, None

        return active_request.request_status, DashboardRequestInfo.from_db_model(active_request)



def register_user_dashboard_request(netid: str, dashboard_request: DashboardRequestInfo):
    with DbSession() as session:
        user = session.scalar(select(UserModel).where(UserModel.netid == netid))
        if not user:
            raise HTTPException(400, "User not registered")

        if any(r.request_status != DashboardRequestStatus.DELETED for r in user.dashboard_requests):
            raise HTTPException(400, "User has already requested a dashboard")

        request = UserDashboardRequestsModel(
            user_id = user.id,
            request_status = DashboardRequestStatus.REQUEST_RECEIVED,
            dashboard_name = user.netid,

            job_input_size_gb = dashboard_request.job_input_size,
            job_output_size_gb = dashboard_request.job_output_size,

            job_count = dashboard_request.job_count,
            concurrent_jobs = dashboard_request.concurrent_jobs,

            dagman = dashboard_request.dagman,
            local_universe = dashboard_request.local_universe,
        )

        session.add(request)
        session.commit()


def cancel_user_dashboard_request(netid: str):
    """ Given a user ID, return the status of that user's dashboard request."""
    with DbSession() as session:
        user = session.scalar(select(UserModel).where(UserModel.netid == netid))
        active_request = session.scalar(select(UserDashboardRequestsModel)
            .where(UserDashboardRequestsModel.user_id == user.id)
            .where(UserDashboardRequestsModel.request_status != DashboardRequestStatus.DELETED)
        )
        if not active_request:
            raise HTTPException(400, "User has no active dashboard request")

        active_request.request_status = DashboardRequestStatus.DELETED
        session.add(active_request)
        session.commit()

def get_not_fully_registered_users() -> list[UserModel]:
    """Get list of users whose LDAP status in the database does not match their actual LDAP status."""
    with DbSession() as session:
        users = session.scalars(select(UserModel)
            .where((UserModel.chtc_account == False) | (UserModel.spark_account == False))
        ).all()
        return users

def update_user_chtc_account_status(netid: str, account_status: UserLDAPStatus):
    with DbSession() as session:
        user = session.scalar(select(UserModel).where(UserModel.netid == netid))
        if user is not None:
            user.chtc_account = account_status.chtc_account
            user.spark_account = account_status.spark_account
            session.add(user)
            session.commit()
