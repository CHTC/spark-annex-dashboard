"""
Utility functions for interacting with the Userapp API.
Used to check if a user exists in the userapp system and whether they have
access to a submit node (for Spark/HPC access).
"""

from datetime import datetime, timezone
from os import environ
from typing import Optional, Any
from dataclasses import dataclass

import requests
from pydantic import BaseModel

from .db_models import RequestStatus

USERAPP_BASE_URL = environ.get("USERAPP_BASE_URL", "http://localhost:8000")
USERAPP_TOKEN = environ.get("USERAPP_TOKEN", "")

# The submit node name that indicates Spark/HPC access
SPARK_SUBMIT_NODE = environ.get("SPARK_SUBMIT_NODE", "hpclogin1.chtc.wisc.edu")


@dataclass
class UserAppUserStatus:
    """Dataclass to represent the LDAP status of a user."""

    chtc_account: RequestStatus
    spark_account: RequestStatus
    modify_timestamp: datetime | None = None


class UserAppSubmitNode(BaseModel):
    """Model for a user's submit node association from the userapp API (UserSubmitGet schema)."""

    id: Optional[int] = None
    submit_node_id: int
    submit_node_name: str
    user_id: int


class UserAppUserForm(BaseModel):
    """Model for a user's form entry from the userapp API (UserApplicationView schema)."""

    id: int
    form_type: str
    status: str
    created_at: datetime
    updated_at: datetime
    content: Optional[dict[str, Any]] = None


class UserAppUser(BaseModel):
    """Model for a user record returned from the userapp API (UserGetFull schema)."""

    id: int
    name: str
    netid: str
    active: Optional[bool] = None
    date: Optional[datetime] = None
    submit_nodes: list[UserAppSubmitNode] = []
    user_forms: list[UserAppUserForm] = []


def get_users_by_netid(
    user_id: str,
    base_url: str = USERAPP_BASE_URL,
    token: str = USERAPP_TOKEN,
) -> list[UserAppUser]:
    """
    Query the userapp /users endpoint filtering by netid.

    Uses the PostgREST-style filter query parameter: ?netid=eq.<user_id>

    Args:
        user_id: The netid of the user to look up.
        base_url: Base URL of the userapp API.
        token: Bearer token for authentication.

    Returns:
        A list of UserAppUser objects matching the given netid.

    Raises:
        requests.exceptions.RequestException: If the API request fails.
    """
    url = f"{base_url}/users"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"netid": f"eq.{user_id}"}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    data = response.json()
    return [UserAppUser.model_validate(user) for user in data]


def get_userapp_user_status(
    user_id: str,
    spark_submit_node: str = SPARK_SUBMIT_NODE,
    base_url: str = USERAPP_BASE_URL,
    token: str = USERAPP_TOKEN,
) -> UserAppUserStatus:
    """
    Query the userapp API for the given netid and return a UserAppUserStatus.

    Status logic:
    - chtc_account:
        - COMPLETE if the user is active.
        - REQUEST_RECEIVED if the user is not active but has a populated user_forms entry.
        - NOT_REQUESTED otherwise.
    - spark_account:
        - COMPLETE if the user is active and has access to the submit node named
          spark_submit_node (default: hpclogin1.chtc.wisc.edu).
        - REQUEST_RECEIVED if any user_forms entry has a computing_type containing "HPC".
        - NOT_REQUESTED otherwise.
    - modify_timestamp: set to the user's account creation time (date field) since
      there is no account modification time in the userapp API.

    Args:
        user_id: The netid of the user to look up.
        spark_submit_node: The name of the submit node that indicates Spark/HPC access.
        base_url: Base URL of the userapp API.
        token: Bearer token for authentication.

    Returns:
        A UserAppUserStatus reflecting the user's account state in the userapp system.

    Raises:
        requests.exceptions.RequestException: If the API request fails.
    """
    users = get_users_by_netid(user_id, base_url=base_url, token=token)

    if not users:
        return UserAppUserStatus(
            chtc_account=RequestStatus.NOT_REQUESTED,
            spark_account=RequestStatus.NOT_REQUESTED,
            modify_timestamp=None,
        )

    # Use the first matching user (netid should be unique)
    user = users[0]

    # Determine chtc_account status
    if user.active:
        chtc_account = RequestStatus.COMPLETE
    elif user.user_forms:
        chtc_account = RequestStatus.REQUEST_RECEIVED
    else:
        chtc_account = RequestStatus.NOT_REQUESTED

    # Determine spark_account status
    has_spark_access = any(
        sn.submit_node_name == spark_submit_node
        for sn in user.submit_nodes
    )
    has_hpc_form = any(
        form.content is not None and "HPC" in str(form.content.get("computing_type", ""))
        for form in user.user_forms
    )

    if user.active and has_spark_access:
        spark_account = RequestStatus.COMPLETE
    elif has_hpc_form:
        spark_account = RequestStatus.REQUEST_RECEIVED
    else:
        spark_account = RequestStatus.NOT_REQUESTED

    modify_timestamp = user.date.replace(tzinfo=timezone.utc) if user.date else None

    return UserAppUserStatus(
        chtc_account=chtc_account,
        spark_account=spark_account,
        modify_timestamp=modify_timestamp,
    )


def update_user_state_from_userapp(user_name: str, current_status: UserAppUserStatus) -> UserAppUserStatus:
    userapp_status = get_userapp_user_status(user_name)
    return UserAppUserStatus(
        chtc_account = userapp_status.chtc_account if userapp_status.chtc_account > current_status.chtc_account else current_status.chtc_account,
        spark_account = userapp_status.spark_account if userapp_status.spark_account > current_status.spark_account else current_status.spark_account,
        modify_timestamp = userapp_status.modify_timestamp if userapp_status.modify_timestamp else current_status.modify_timestamp,
    )
