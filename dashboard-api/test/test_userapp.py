from src.app import app
from src.api_models import UserInfo
from src.db_models import RequestStatus
from fastapi.testclient import TestClient
from typing import Any
from dataclasses import dataclass
import pytest

client = TestClient(app)


@dataclass
class MockJsonResponse:
    json_data: Any

    def json(self):
        return self.json_data

    def raise_for_status(self):
        pass


# A minimal valid UserAppUser payload with no submit nodes
USER_NO_SUBMIT_NODES = {
    "id": 1,
    "name": "Test User",
    "netid": "test-user",
    "active": True,
    "date": "2024-01-01T00:00:00",
    "submit_nodes": [],
}

# A UserAppUser payload with a submit node that is NOT the spark node
USER_OTHER_SUBMIT_NODE = {
    "id": 1,
    "name": "Test User",
    "netid": "test-user",
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
}

# A UserAppUser payload with the spark submit node
USER_WITH_SPARK_NODE = {
    "id": 1,
    "name": "Test User",
    "netid": "test-user",
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
}

# A UserAppUser payload with multiple submit nodes, including the spark node
USER_WITH_MULTIPLE_SUBMIT_NODES = {
    "id": 1,
    "name": "Test User",
    "netid": "test-user",
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
}


class TestNoExistingUser:

    @pytest.fixture(autouse=True)
    def mock_auth(self, mocker):
        mocker.patch("src.app.verify_auth_headers", return_value={"eppn": "test-user@wisc.edu"})

    def userapp_response(self, mocker, json_data):
        mocker.patch("src.userapp_utils.requests.get", return_value=MockJsonResponse(json_data=json_data))

    def get_user_info(self):
        response = client.get("/")
        assert response.status_code == 200
        return UserInfo.model_validate(response.json())

    def test_get_unregistered_user(self, mocker):
        # Mocks a request for a user that is not registered in the userapp (empty list response)
        self.userapp_response(mocker, [])
        data = self.get_user_info()
        assert data.user_id == "test-user"
        assert data.chtc_account.chtc_account == RequestStatus.NOT_REQUESTED
        assert data.chtc_account.spark_account == RequestStatus.NOT_REQUESTED

    def test_get_registered_user_no_submit_nodes(self, mocker):
        # Mocks a request for a user that exists in the userapp but has no submit nodes
        self.userapp_response(mocker, [USER_NO_SUBMIT_NODES])
        data = self.get_user_info()
        assert data.user_id == "test-user"
        assert data.chtc_account.chtc_account == RequestStatus.COMPLETE
        assert data.chtc_account.spark_account == RequestStatus.NOT_REQUESTED

    def test_get_registered_user_other_submit_node(self, mocker):
        # Mocks a request for a user that exists and has a submit node, but not the spark node
        self.userapp_response(mocker, [USER_OTHER_SUBMIT_NODE])
        data = self.get_user_info()
        assert data.user_id == "test-user"
        assert data.chtc_account.chtc_account == RequestStatus.COMPLETE
        assert data.chtc_account.spark_account == RequestStatus.NOT_REQUESTED

    def test_get_registered_user_with_spark_node(self, mocker):
        # Mocks a request for a user that exists and has access to the spark submit node
        self.userapp_response(mocker, [USER_WITH_SPARK_NODE])
        data = self.get_user_info()
        assert data.user_id == "test-user"
        assert data.chtc_account.chtc_account == RequestStatus.COMPLETE
        assert data.chtc_account.spark_account == RequestStatus.COMPLETE

    def test_get_registered_user_with_multiple_submit_nodes(self, mocker):
        # Mocks a request for a user that has multiple submit nodes, one of which is the spark node
        self.userapp_response(mocker, [USER_WITH_MULTIPLE_SUBMIT_NODES])
        data = self.get_user_info()
        assert data.user_id == "test-user"
        assert data.chtc_account.chtc_account == RequestStatus.COMPLETE
        assert data.chtc_account.spark_account == RequestStatus.COMPLETE