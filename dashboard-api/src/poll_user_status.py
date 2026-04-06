"""
Util script to poll the LDAP status of users in the database and sync changes to the local SQLite database.
Also, send notification emails to users when their account status updates.
"""

from celery import Celery
from celery.schedules import crontab
from datetime import timedelta
from os import environ
import pytz

from . import db
from .userapp_utils import get_userapp_user_status
from .notification_emails import send_chtc_account_provisioned_notification, send_slurm_account_provisioned_notification
from .icinga_utils import check_icinga_puppet_update_time
from .db_models import RequestStatus

app = Celery()

PUPPET_WAIT_TIME = timedelta(hours=int(environ.get('PUPPET_WAIT_HOURS', 2)))

@app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    # Calls poll_user_ldap_status every minute
    sender.add_periodic_task(crontab(minute='*', hour='*'), poll_userapp_user_status.s())

@app.task
def poll_userapp_user_status():
    """Poll the LDAP status of all users in the database and update the database if there are any changes. Also send notification emails if there are any changes."""
    last_puppet_run = check_icinga_puppet_update_time()

    # Convert naive puppet timestamp (Central Time) to UTC-aware datetime
    central = pytz.timezone('US/Central')
    last_puppet_run_utc = central.localize(last_puppet_run).astimezone(pytz.UTC)

    print(f"Polling LDAP status of users based on last puppet run: {last_puppet_run_utc}...")
    users = db.get_not_fully_registered_users()
    for user in users:
        userapp_status = get_userapp_user_status(user.netid)
        if (
            (userapp_status.chtc_account == RequestStatus.COMPLETE and user.chtc_account != RequestStatus.COMPLETE)
            or 
            (userapp_status.spark_account == RequestStatus.COMPLETE and user.spark_account != RequestStatus.COMPLETE)
        ):
            if userapp_status.modify_timestamp and last_puppet_run_utc - userapp_status.modify_timestamp < PUPPET_WAIT_TIME:
                print(f"User {user.netid} has LDAP modification more recent than last puppet run. Skipping.")
                continue

            db.update_user_chtc_account_status_from_ldap(user.netid, userapp_status)
            if userapp_status.chtc_account == RequestStatus.COMPLETE and userapp_status.spark_account == RequestStatus.COMPLETE:
                print(f"User {user.netid} has newly-detected LDAP access. Notifying.")
                send_slurm_account_provisioned_notification(user.netid)
            elif userapp_status.chtc_account == RequestStatus.COMPLETE:
                print(f"User {user.netid} has newly detected CHTC access, but not LDAP access. Notifying")
                send_chtc_account_provisioned_notification(user.netid)
