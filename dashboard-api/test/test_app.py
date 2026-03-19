from src.app import app
from fastapi.testclient import TestClient

client = TestClient(app)

class MockLDAPConnection:
    def search(self, search_base, search_filter, **kwargs):
        return None, None, [], None

def test_get_unregistered_user(mocker):
    # Mocks a request for a user that is not registered
     
    # mock auth
    mocker.patch("src.app.verify_auth_headers", return_value={"eppn": "test-user@wisc.edu"})
    
    # Mock an LDAP connection that returns no entries for the user
    mocker.patch("src.ldap_utils.Connection", return_value=MockLDAPConnection())
    response = client.get("/")
    assert response.status_code == 200
