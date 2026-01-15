from typing import Union

from fastapi import FastAPI, Request, Depends
from auth_handler import read_cilogon_headers
import jwt

app = FastAPI(
#    dependencies=[Depends(read_cilogon_headers)]
)

JWKS_URL = "https://cilogon.org/oauth2/certs"
AUDIENCE = "cilogon:/client_id/534864d355885529ea6033daa9bdf0ec"

def verify_auth_headers(request: Request) -> Union[dict, None]:
    auth_header = request.headers.get("Authorization")
    if auth_header:
        token = auth_header.split(" ")[1]
        jwks_client = jwt.PyJWKClient(JWKS_URL)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        decoded_token = jwt.decode(token, signing_key, audience=AUDIENCE, algorithms=["RS256"])
        return decoded_token
    return "No token provided"


@app.get("/")
def read_root(request: Request) -> dict[str, str]:
    print(verify_auth_headers(request))
    return {
        "message": "Hello, world!",
    }
