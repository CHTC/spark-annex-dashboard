"""
Util script to poll the LDAP status of users in the database and sync changes to the local SQLite database.
Also, send notification emails to users when their account status updates.
"""

import db
from celery import Celery
from celery.schedules import crontab
from ldap_utils import check_ldap_user_in_group
from notification_emails import send_chtc_account_provisioned_notification, send_slurm_account_provisioned_notification
from icinga_utils import check_icinga_puppet_update_time
from datetime import timedelta

app = Celery()

PUPPET_WAIT_TIME = timedelta(hours=2)

@app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    # Calls poll_user_ldap_status every minute
    sender.add_periodic_task(crontab(minute='*/10', hour='*'), poll_user_ldap_status.s())

@app.task
def poll_user_ldap_status():
    """Poll the LDAP status of all users in the database and update the database if there are any changes. Also send notification emails if there are any changes."""
    last_puppet_run = check_icinga_puppet_update_time()
    print(f"Polling LDAP status of users based on last puppet run: {last_puppet_run}...")
    users = db.get_not_fully_registered_users()
    for user in users:
        ldap_status = check_ldap_user_in_group(user.netid)
        if ldap_status.chtc_account != user.chtc_account or ldap_status.spark_account != user.spark_account:
            if ldap_status.modify_timestamp and last_puppet_run - ldap_status.modify_timestamp < PUPPET_WAIT_TIME:
                print(f"User {user.netid} has LDAP modification more recent than last puppet run. Skipping.")
                continue

            db.update_user_chtc_account_status_from_ldap(user.netid, ldap_status)
            if ldap_status.chtc_account and ldap_status.spark_account:
                print(f"User {user.netid} has newly-detected LDAP access. Notifying.")
                send_slurm_account_provisioned_notification(user.netid)
            elif ldap_status.chtc_account:
                print(f"User {user.netid} has newly detected CHTC access, but not LDAP access. Notifying")
                send_chtc_account_provisioned_notification(user.netid)
