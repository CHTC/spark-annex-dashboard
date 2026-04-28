"""
Util script to poll the LDAP status of users in the database and sync changes to the local SQLite database.
Also, send notification emails to users when their account status updates.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import timedelta
from os import environ
import pytz

from . import db
from .userapp_utils import get_userapp_user_status
from .notification_emails import send_chtc_account_provisioned_notification, send_slurm_account_provisioned_notification
from .icinga_utils import check_icinga_puppet_update_time
from .db_models import RequestStatus

PUPPET_WAIT_TIME = timedelta(hours=int(environ.get('PUPPET_WAIT_HOURS', 2)))


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
        # We need to ensure that enough time has passed between the user being marked for spark login node acesss
        # in the userapp, and puppet reconciling the user's account onto the login node. We don't get the user's last
        # update time from the userapp directly, just the creation time, so we need to proxy the update time with the
        # "last observed change" stored directly in the dashboard DB
        can_mark_complete = user.updated_at and last_puppet_run_utc - user.updated_at > PUPPET_WAIT_TIME
        userapp_status.spark_account = userapp_status.spark_account if can_mark_complete else RequestStatus.NOT_REQUESTED
        if (
            (userapp_status.chtc_account == RequestStatus.COMPLETE and user.chtc_account != RequestStatus.COMPLETE)
            or
            (userapp_status.spark_account == RequestStatus.COMPLETE and user.spark_account != RequestStatus.COMPLETE)
        ):

            db.update_user_chtc_account_status_from_userapp(user.netid, userapp_status)
            if userapp_status.chtc_account == RequestStatus.COMPLETE and userapp_status.spark_account == RequestStatus.COMPLETE:
                print(f"User {user.netid} has newly-detected LDAP access. Notifying.")
                send_slurm_account_provisioned_notification(user.netid)
            elif userapp_status.chtc_account == RequestStatus.COMPLETE:
                print(f"User {user.netid} has newly detected CHTC access, but not LDAP access. Notifying")
                send_chtc_account_provisioned_notification(user.netid)


scheduler = BackgroundScheduler()
scheduler.add_job(poll_userapp_user_status, 'cron', minute='*', hour='*')


def start():
    """Start the APScheduler background scheduler."""
    scheduler.start()


def stop():
    """Stop the APScheduler background scheduler."""
    scheduler.shutdown()
