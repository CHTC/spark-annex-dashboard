import enum
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship, Mapped
from typing import List
from uuid import uuid4
from datetime import datetime

class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    netid: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    chtc_account: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    spark_account: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    dashboard_requests: Mapped[List["UserDashboardRequestsModel"]] = relationship(back_populates="user")

class DashboardRequestStatus(enum.Enum):
    NOT_REQUESTED = "Not requested"
    REQUEST_RECEIVED = "Request received"
    IN_PROGRESS = "In progress"
    COMPLETE = "Active"
    DELETION_REQUESTED = "Deletion Requested"
    DELETED = "Deleted"


class UserDashboardRequestsModel(Base):
    __tablename__ = "user_dashboard_requests"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # ID of the user that requested the dashboard
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped["UserModel"] = relationship(back_populates="dashboard_requests")

    # Time that the user submitted the request
    request_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Status of the request as noted by the infrastructure services team
    request_status: Mapped[DashboardRequestStatus] = mapped_column(Enum(DashboardRequestStatus), nullable=False)

    # User-set parameters for dashboard creation
    dashboard_name: Mapped[str] = mapped_column(String, nullable=False)

    job_input_size_gb: Mapped[int] = mapped_column(Integer, nullable=False)
    job_output_size_gb: Mapped[int] = mapped_column(Integer, nullable=False)

    job_count: Mapped[int] = mapped_column(Integer, nullable=False)
    concurrent_jobs: Mapped[int] = mapped_column(Integer, nullable=False)

    dagman: Mapped[bool] = mapped_column(Boolean, nullable=False)
    local_universe: Mapped[bool] = mapped_column(Boolean, nullable=False)
