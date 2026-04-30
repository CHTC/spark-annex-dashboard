"""
Util script to mark a user's dashboard as provisioned, and send a notification email
to the user
"""
import sys

sys.path.append(".") # Why are relative imports in Python so difficult :(
from src.db import mark_user_dashboard_request_complete
from src.notification_emails import send_ap_provisioning_complete_notification


netid = sys.argv[1]

mark_user_dashboard_request_complete(netid)
send_ap_provisioning_complete_notification(netid)
