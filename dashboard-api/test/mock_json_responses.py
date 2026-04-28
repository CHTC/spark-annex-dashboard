"""
Shared mock JSON response payloads for userapp API tests.

All USER_* constants are single-object dicts representing one userapp user record.
Wrap them in a list when passing as an API response, e.g. [USER_ACTIVE_NO_SUBMIT_NODES].
Use USER_NOT_IN_USERAPP directly (it is already an empty list).
"""

from dataclasses import dataclass
from typing import Any


TEST_NETID = "test-user"


@dataclass
class MockJsonResponse:
    """Minimal stand-in for a requests.Response object."""

    json_data: Any

    def json(self):
        return self.json_data

    def raise_for_status(self):
        pass


# ---------------------------------------------------------------------------
# Empty response (user not found in userapp)
# ---------------------------------------------------------------------------

USER_NOT_IN_USERAPP = []

# ---------------------------------------------------------------------------
# Active users
# ---------------------------------------------------------------------------

# Active user with no submit nodes → chtc=COMPLETE, spark=NOT_REQUESTED
USER_ACTIVE_NO_SUBMIT_NODES = {
    "id": 1,
    "name": "Test User",
    "netid": TEST_NETID,
    "active": True,
    "date": "2024-01-01T00:00:00",
    "submit_nodes": [],
    "user_forms": [],
}

# Active user with a submit node that is NOT the spark node → chtc=COMPLETE, spark=NOT_REQUESTED
USER_ACTIVE_OTHER_SUBMIT_NODE = {
    "id": 1,
    "name": "Test User",
    "netid": TEST_NETID,
    "active": True,
    "date": "2024-01-01T00:00:00",
    "submit_nodes": [
        {
            "id": 10,
            "submit_node_id": 2,
            "submit_node_name": "other-login.chtc.wisc.edu",
            "user_id": 1,
        }
    ],
    "user_forms": [],
}

# Active user on the spark (HPC) submit node → chtc=COMPLETE, spark=COMPLETE
USER_ACTIVE_WITH_SPARK_NODE = {
    "id": 1,
    "name": "Test User",
    "netid": TEST_NETID,
    "active": True,
    "date": "2024-01-01T00:00:00",
    "submit_nodes": [
        {
            "id": 10,
            "submit_node_id": 1,
            "submit_node_name": "hpclogin1.chtc.wisc.edu",
            "user_id": 1,
        }
    ],
    "user_forms": [],
}

# Active user with multiple submit nodes, including the spark node → chtc=COMPLETE, spark=COMPLETE
USER_WITH_MULTIPLE_SUBMIT_NODES = {
    "id": 1,
    "name": "Test User",
    "netid": TEST_NETID,
    "active": True,
    "date": "2024-01-01T00:00:00",
    "submit_nodes": [
        {
            "id": 10,
            "submit_node_id": 2,
            "submit_node_name": "other-login.chtc.wisc.edu",
            "user_id": 1,
        },
        {
            "id": 11,
            "submit_node_id": 1,
            "submit_node_name": "hpclogin1.chtc.wisc.edu",
            "user_id": 1,
        },
    ],
    "user_forms": [],
}

# ---------------------------------------------------------------------------
# Inactive users
# ---------------------------------------------------------------------------

# Inactive user with no user_forms → chtc=NOT_REQUESTED, spark=NOT_REQUESTED
USER_INACTIVE_NO_FORMS = {
    "id": 1,
    "name": "Test User",
    "netid": TEST_NETID,
    "active": False,
    "date": "2024-01-01T00:00:00",
    "submit_nodes": [],
    "user_forms": [],
}

# Inactive user with a form that does NOT request HPC → chtc=REQUEST_RECEIVED, spark=NOT_REQUESTED
USER_INACTIVE_NON_HPC_FORM = {
    "id": 1,
    "name": "Test User",
    "netid": TEST_NETID,
    "active": False,
    "date": "2024-01-01T00:00:00",
    "submit_nodes": [],
    "user_forms": [
        {
            "id": 1,
            "form_type": "user_application",
            "status": "pending",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
            "content": {"computing_type": "HTC"},
        }
    ],
}

# Inactive user with a form requesting HPC access → chtc=REQUEST_RECEIVED, spark=REQUEST_RECEIVED
USER_INACTIVE_HPC_FORM = {
    "id": 1,
    "name": "Test User",
    "netid": TEST_NETID,
    "active": False,
    "date": "2024-01-01T00:00:00",
    "submit_nodes": [],
    "user_forms": [
        {
            "id": 1,
            "form_type": "user_application",
            "status": "pending",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
            "content": {"computing_type": "HPC"},
        }
    ],
}