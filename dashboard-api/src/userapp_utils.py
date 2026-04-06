"""
Utility functions for interacting with the Userapp API.
Used to check if a user exists in the userapp system and whether they have
access to a submit node (for Spark/HPC access).
"""

from datetime import datetime,timezone
from os import environ
from typing import Optional
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
    """Model for a user's submit node association from the userapp API."""

    id: Optional[int] = None
    submit_node_id: int
    submit_node_name: str
    user_id: int


class UserAppUser(BaseModel):
    """Model for a user record returned from the userapp API (UserGetFull schema)."""

    id: int
    name: str
    netid: str
    active: bool
    date: datetime
    submit_nodes: list[UserAppSubmitNode] = []


def get_users_by_netid(
    user_id: str,
    base_url: str = USERAPP_BASE_URL,
    token: str = USERAPP_TOKEN,
) -> list[UserAppUser]:
    """
    Query the userapp /users endpoint filtering by netid.

    Uses the PostgREST-style filter query parameter: ?netid=eq.<user_id>&active=eq.true

    Args:
        user_id: The netid of the user to look up.
        base_url: Base URL of the userapp API.
        token: Bearer token for authentication.

    Returns:
        A list of UserapUserGet objects matching the given netid.

    Raises:
        requests.exceptions.RequestException: If the API request fails.
    """
    url = f"{base_url}/users"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"netid": f"eq.{user_id}","active":"eq.true"}

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
    Query the userapp API for the given netid and return a UserLDAPStatus.

    - chtc_account: COMPLETE if the user exists in the userapp, NOT_REQUESTED otherwise.
    - spark_account: COMPLETE if the user has access to the submit node named
      spark_submit_node (default: hpclogin1.chtc.wisc.edu), NOT_REQUESTED otherwise.
    - modify_timestamp: set to the user's account creation time (date field) since
      there is no account modification time in the userapp API.

    Args:
        user_id: The netid of the user to look up.
        spark_submit_node: The name of the submit node that indicates Spark/HPC access.
        base_url: Base URL of the userapp API.
        token: Bearer token for authentication.

    Returns:
        A UserLDAPStatus reflecting the user's account state in the userapp system.

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
    has_spark_access = any(
        sn.submit_node_name == spark_submit_node
        for sn in user.submit_nodes
    )

    return UserAppUserStatus(
        chtc_account=RequestStatus.COMPLETE,
        spark_account=RequestStatus.COMPLETE if has_spark_access else RequestStatus.NOT_REQUESTED,
        modify_timestamp=user.date.replace(tzinfo=timezone.utc),
    )

def update_user_state_from_userapp(user_name: str, current_status: UserAppUserStatus) -> UserAppUserStatus:
    userapp_status = get_userapp_user_status(user_name)
    return UserAppUserStatus(
        chtc_account = userapp_status.chtc_account if userapp_status.chtc_account > current_status.chtc_account else current_status.chtc_account,
        spark_account = userapp_status.spark_account if userapp_status.spark_account > current_status.spark_account else current_status.spark_account,
        modify_timestamp = userapp_status.modify_timestamp if userapp_status.modify_timestamp else current_status.modify_timestamp,
    )
