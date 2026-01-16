from os import environ
import ssl
from ldap3 import Server, Connection, ALL, SAFE_SYNC, Tls
from sys import argv

LDAP_SERVER = environ.get("LDAP_SERVER", "ldaps://ldap-replica1.chtcdev.chtc.io")
LDAP_CERT = environ.get("LDAP_CERT", "/etc/pki/tls/certs/tiger_dev_ca.crt")
LDAP_USER = environ.get("LDAP_USER", "cn=readonly,ou=system,dc=chtc,dc=wisc,dc=edu")
LDAP_GROUP = environ.get("LDAP_GROUP", "cn=hpclogin1.chtc.wisc.edu,ou=user_tags,dc=chtc,dc=wisc,dc=edu")

LDAP_AUTHTOK = environ["LDAP_AUTHTOK"] # Required

tls_configuration = Tls(ca_certs_file=LDAP_CERT) if LDAP_CERT else None

def check_ldap_user_in_group(user_name: str,  group_filter: str = LDAP_GROUP, ldap_user: str = LDAP_USER, ldap_server: str = LDAP_SERVER, ldap_authtok: str = LDAP_AUTHTOK) -> bool:
    """ Given an LDAP username and group, return whether that user is in that group. """
    server = Server(ldap_server, get_info=ALL, use_ssl=True, tls=tls_configuration)
    connection = Connection(server, ldap_user, ldap_authtok, client_strategy=SAFE_SYNC, auto_bind=True)
    _, _, response, _ = connection.search(f"uid={user_name},ou=people,dc=chtc,dc=wisc,dc=edu", f"(isMemberOf={group_filter})", attributes=["employeeNumber", "isMemberOf"])

    return len(response) > 0

if __name__ == "__main__":
    users = check_ldap_user_in_group(LDAP_SERVER, LDAP_USER, LDAP_AUTHTOK, LDAP_GROUP, argv[1])
    print(users)
