"""
Util script to mark a user's dashboard repair request as serviced, and 
send a notification email to the user
"""
import sys

sys.path.append(".") # Why are relative imports in Python so difficult :(
from src.db import mark_user_assistance_completed
from src.notification_emails import send_ap_repair_complete_notification


netid = sys.argv[1]

mark_user_assistance_completed(netid)
send_ap_repair_complete_notification(netid)
