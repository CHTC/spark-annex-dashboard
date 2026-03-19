"""
Utility functions for interacting with the LDAP directory. Used to check
if a user is registered with a CHTC account, and if they are marked for
Slurm login access.
"""
from dataclasses import dataclass
from os import environ
from sys import argv
from datetime import datetime
from ldap3 import ALL, SAFE_SYNC, Connection, Server, Tls

from .db_models import RequestStatus

LDAP_SERVER = environ.get("LDAP_SERVER", "ldaps://ldap-replica1.chtcdev.chtc.io")
LDAP_CERT = environ.get("LDAP_CERT", "/etc/pki/tls/certs/tiger_dev_ca.crt")
LDAP_USER = environ.get("LDAP_USER", "cn=readonly,ou=system,dc=chtc,dc=wisc,dc=edu")
LDAP_GROUP = environ.get(
    "LDAP_GROUP", "cn=hpclogin1.chtc.wisc.edu,ou=user_tags,dc=chtc,dc=wisc,dc=edu"
)

LDAP_AUTHTOK = environ.get("LDAP_AUTHTOK", "")  # Required

tls_configuration = Tls(ca_certs_file=LDAP_CERT) if LDAP_CERT else None


@dataclass
class UserLDAPStatus:
    """Dataclass to represent the LDAP status of a user."""

    chtc_account: RequestStatus
    spark_account: RequestStatus
    modify_timestamp: datetime | None = None


def check_ldap_user_in_group(
    user_name: str,
    group_filter: str = LDAP_GROUP,
    ldap_user: str = LDAP_USER,
    ldap_server: str = LDAP_SERVER,
    ldap_authtok: str = LDAP_AUTHTOK,
) -> UserLDAPStatus:
    """Given an LDAP username and group, return whether that user is in that group."""
    server = Server(ldap_server, get_info=ALL, use_ssl=True, tls=tls_configuration)
    connection = Connection(server, ldap_user, ldap_authtok, client_strategy=SAFE_SYNC, auto_bind=True)
    # TODO we probably don't need to query LDAP twice here
    _, _, exists_response, _ = connection.search(
        f"uid={user_name},ou=people,dc=chtc,dc=wisc,dc=edu",
        f"(uid={user_name})",
        attributes=["employeeNumber", "isMemberOf", "modifyTimestamp"],
    )
    _, _, group_response, _ = connection.search(
        f"uid={user_name},ou=people,dc=chtc,dc=wisc,dc=edu",
        f"(isMemberOf={group_filter})",
        attributes=["employeeNumber", "isMemberOf", "modifyTimestamp"],
    )

    modify_timestamp : datetime | None = None
    if len(exists_response) > 0 and "modifyTimestamp" in exists_response[0]["attributes"]:
        modify_timestamp = exists_response[0]["attributes"]["modifyTimestamp"]
    return UserLDAPStatus(
        chtc_account = RequestStatus.COMPLETE if len(exists_response) > 0 else RequestStatus.NOT_REQUESTED,
        spark_account = RequestStatus.COMPLETE if len(group_response) > 0 else RequestStatus.NOT_REQUESTED,
        modify_timestamp = modify_timestamp,
    )
    
    
def update_user_state_from_ldap(user_name: str, current_status: UserLDAPStatus) -> UserLDAPStatus:
    ldap_status = check_ldap_user_in_group(user_name)
    return UserLDAPStatus(
        chtc_account = ldap_status.chtc_account if ldap_status.chtc_account > current_status.chtc_account else current_status.chtc_account,
        spark_account = ldap_status.spark_account if ldap_status.spark_account > current_status.spark_account else current_status.spark_account,
        modify_timestamp = ldap_status.modify_timestamp if ldap_status.modify_timestamp else current_status.modify_timestamp,
    )

if __name__ == "__main__":
    users = check_ldap_user_in_group(
        LDAP_SERVER, LDAP_USER, LDAP_AUTHTOK, LDAP_GROUP, argv[1]
    )
    print(users)
