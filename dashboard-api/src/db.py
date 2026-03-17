from sqlalchemy import create_engine, select, delete
from sqlalchemy.orm import sessionmaker, Session, joinedload
from os import environ
from typing import Optional
import urllib.parse
import db_models as dm
from api_models import DashboardRequestInfo
from ldap_utils import UserLDAPStatus

from fastapi import HTTPException

db_path = environ.get("DASHBOARD_DB_PATH", "sqlite:///tmp/dashboard.db")


engine = create_engine(db_path)

dm.Base.metadata.create_all(engine)

DbSession = sessionmaker(bind=engine, expire_on_commit=False)


def get_or_update_user(netid: str, user_status: UserLDAPStatus | None = None):
    """ Given a user ID, create a user entry in the database """
    with DbSession() as session:
        user = session.scalar(select(dm.UserModel).where(dm.UserModel.netid == netid))

        if user is None:
            user = dm.UserModel(netid = netid)
            user.chtc_account = dm.RequestStatus.NOT_REQUESTED
            user.spark_account = dm.RequestStatus.NOT_REQUESTED
            user.assistance_requested = False
            session.add(user)
            session.commit()
        elif user_status:
            user.chtc_account = user_status.chtc_account
            user.spark_account = user_status.spark_account
            session.add(user)
            session.commit()
        return user

def get_user_dashboard_status(netid: str) -> tuple[dm.RequestStatus, DashboardRequestInfo | None]:
    """ Given a user ID, return the status of that user's dashboard request."""
    with DbSession() as session:
        user = session.scalar(select(dm.UserModel).where(dm.UserModel.netid == netid))
        active_request = session.scalar(select(dm.UserDashboardRequestsModel)
            .where(dm.UserDashboardRequestsModel.user_id == user.id)
            .where(dm.UserDashboardRequestsModel.request_status != dm.RequestStatus.DELETED)
        )
        if not active_request:
            return dm.RequestStatus.NOT_REQUESTED, None

        return active_request.request_status, DashboardRequestInfo.from_db_model(active_request)



def register_user_dashboard_request(netid: str, dashboard_request: DashboardRequestInfo):
    with DbSession() as session:
        user = session.scalar(select(dm.UserModel).where(dm.UserModel.netid == netid))
        if not user:
            raise HTTPException(400, "User not registered")

        if any(r.request_status != dm.RequestStatus.DELETED for r in user.dashboard_requests):
            raise HTTPException(400, "User has already requested a dashboard")

        request = dm.UserDashboardRequestsModel(
            user_id = user.id,
            request_status = dm.RequestStatus.REQUEST_RECEIVED,
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
        user = session.scalar(select(dm.UserModel).where(dm.UserModel.netid == netid))
        active_request = session.scalar(select(dm.UserDashboardRequestsModel)
            .where(dm.UserDashboardRequestsModel.user_id == user.id)
            .where(dm.UserDashboardRequestsModel.request_status != dm.RequestStatus.DELETED)
        )
        if not active_request:
            raise HTTPException(400, "User has no active dashboard request")

        active_request.request_status = dm.RequestStatus.DELETED
        session.add(active_request)
        session.commit()

def get_not_fully_registered_users() -> list[dm.UserModel]:
    """Get list of users whose LDAP status in the database does not match their actual LDAP status."""
    with DbSession() as session:
        users = session.scalars(select(dm.UserModel)
            .where((dm.UserModel.chtc_account != dm.RequestStatus.COMPLETE) | (dm.UserModel.spark_account != dm.RequestStatus.COMPLETE))
        ).all()
        return list(users)

def update_user_chtc_account_status_from_ldap(netid: str, account_status: UserLDAPStatus):
    with DbSession() as session:
        user = session.scalar(select(dm.UserModel).where(dm.UserModel.netid == netid))
        if user is None:
            return
        user.chtc_account = dm.RequestStatus.COMPLETE if account_status.chtc_account else user.chtc_account
        user.spark_account = dm.RequestStatus.COMPLETE if account_status.spark_account else user.spark_account
        session.add(user)
        session.commit()


def mark_user_assistance_requested(netid: str):
    with DbSession() as session:
        user = session.scalar(select(dm.UserModel).where(dm.UserModel.netid == netid))
        if user is None:
            return
        user.assistance_requested = True
        session.add(user)
        session.commit()
