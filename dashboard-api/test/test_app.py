from src.app import app
from src.api_models import UserInfo
from src.db_models import RequestStatus
from fastapi.testclient import TestClient

client = TestClient(app)

class MockLDAPConnection:
    def search(self, search_base, search_filter, **kwargs):
        return None, None, [], None

class MockJsonResponse:
    def json(self):
        return {}
    
    def raise_for_status(self):
        pass

def test_get_unregistered_user(mocker):
    # Mocks a request for a user that is not registered
     
    # mock auth
    mocker.patch("src.app.verify_auth_headers", return_value={"eppn": "test-user@wisc.edu"})
    
    # Mock an LDAP connection that returns no entries for the user
    mocker.patch("src.userapp_utils.requests.get", return_value=MockJsonResponse())
    response = client.get("/")
    assert response.status_code == 200
    
    data = UserInfo.model_validate(response.json())
    assert data.user_id == "test-user"
    assert data.chtc_account.chtc_account == RequestStatus.NOT_REQUESTED
    assert data.chtc_account.spark_account == RequestStatus.NOT_REQUESTED
