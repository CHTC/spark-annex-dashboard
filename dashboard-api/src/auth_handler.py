from fastapi import Request
import jwt
from os import environ
from typing import Union

JWKS_URL = "https://cilogon.org/oauth2/certs"
AUDIENCE = environ.get("JWT_AUDIENCE", "cilogon:/client_id/534864d355885529ea6033daa9bdf0ec")

def verify_auth_headers(request: Request) -> Union[dict, None]:
    auth_header = request.headers.get("Authorization")
    if auth_header:
        try:
            token = auth_header.split(" ")[1]
            jwks_client = jwt.PyJWKClient(JWKS_URL)
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            decoded_token = jwt.decode(token, signing_key, audience=AUDIENCE, algorithms=["RS256"])
            print(f"decoded auth token successfully: {decoded_token}")
            return decoded_token
        except Exception as e:
            print(f"Error verifying token: {e}")
            return None
    return None
