import os
import smtplib
from email.message import EmailMessage
from api_models import DashboardRequestInfo, LiveDashboardStatus

SEND_EMAILS = os.environ.get('SEND_EMAILS', "True").lower() != "false"
FROM_ADDRESS = os.environ.get('FROM_ADDRESS')
TO_ADDRESS = os.environ.get('TO_ADDRESS')

# Email subjects
DASHBOARD_REQUEST_SUBJECT = "New AP Dashboard Request from {netid}"
DASHBOARD_CANCELLATION_SUBJECT = "Cancelled AP Dashboard Request from {netid}"
DASHBOARD_REPAIR_REQUEST_SUBJECT = "AP Dashboard Repair Request from {netid}"
SLURM_ACCOUNT_REQUEST_SUBJECT = "Slurm Cluster Access Request from {netid}"
CHTC_ACCOUNT_READY_SUBJECT = "Your CHTC Account is Ready"
SLURM_REQUEST_CONFIRMATION_SUBJECT = "Slurm Cluster Access Request Received"
SLURM_ACCOUNT_READY_SUBJECT = "Your Slurm Account is Ready"
AP_REQUEST_CONFIRMATION_SUBJECT = "Personal Access Point Request Received"
AP_PROVISIONING_STARTED_SUBJECT = "Personal Access Point Provisioning Started"
AP_PROVISIONING_COMPLETE_SUBJECT = "Your Personal Access Point is Ready"
AP_HEALTH_DEGRADED_SUBJECT = "Personal Access Point Health Alert"
AP_REPAIR_COMPLETE_SUBJECT = "Personal Access Point Operational"

# Email content templates

# Admin-facing email texts

DASHBOARD_REQUEST_CONTENT = """
A new AP dashboard has been requested by user {netid} with the following parameters:
Job Input Size (GB): {job_input_size}
Job Output Size (GB): {job_output_size}
Job Count: {job_count}
Concurrent Jobs: {concurrent_jobs}
DAGMan: {dagman}
Local Universe: {local_universe}
"""

DASHBOARD_CANCELLATION_CONTENT = """User {netid} has cancelled their AP dashboard request."""


DASHBOARD_REPAIR_REQUEST_CONTENT = """
User {netid} has reported a problem with their personal AP. 

The current status of the AP is:
pod_health: {pod_health}
pod_health_reason: {pod_health_reason}
collector_health: {collector_health}
collector_health_reason: {collector_health_reason}
dashboard_health: {dashboard_health}
dashboard_health_reason: {dashboard_health_reason}
"""


SLURM_ACCOUNT_REQUEST_CONTENT = """
User {netid} has requested access to the Spark Slurm cluster for the purpose of running a Personal AP annex.
"""
# User-facing email texts

CHTC_ACCOUNT_READY_CONTENT = """
Hello {netid},

Your CHTC account is now ready to use. Please return to the AP dashboard for instructions on requesting Slurm cluster access.

Best regards,
CHTC Support Team
"""

SLURM_REQUEST_CONFIRMATION_CONTENT = """
Hello {netid},

Thank you for requesting access to CHTC's Spark Slurm cluster. We've received your request and will process it within 2-3 business days. If you haven't heard from us within 3 business days, please send a follow-up email to chtc-infrastructure@g-groups.wisc.edu.

Best regards,
CHTC Infrastructure Services Team
"""

SLURM_ACCOUNT_READY_CONTENT = """
Hello {netid},

Your Slurm account is now ready to use. Please return to the AP dashboard for instructions on requesting a Personal Access Point.

Best regards,
CHTC Infrastructure Services Team
"""

AP_REQUEST_CONFIRMATION_CONTENT = """
Hello {netid},

Thank you for requesting a Personal Access Point. We've received your request and will process it within 2-3 business days. If you haven't heard from us within 3 business days, please send a follow-up email to chtc-infrastructure@g-groups.wisc.edu.

Best regards,
CHTC Infrastructure Services Team
"""

AP_PROVISIONING_STARTED_CONTENT = """
Hello {netid},

The infrastructure services team has started work provisioning your Personal Access Point. Your AP should be ready to go within 2-4 hours. You'll receive another notification when your AP is live.

Best regards,
CHTC Infrastructure Services Team
"""

AP_PROVISIONING_COMPLETE_CONTENT = """
Hello {netid},

The infrastructure services team has provisioned your Personal Access Point. Please return to the AP dashboard for instructions to access your Personal AP.

Best regards,
CHTC Infrastructure Services Team
"""

AP_HEALTH_DEGRADED_CONTENT = """
Hello {netid},

We have detected an operational issue with your Personal Access Point. Please visit the AP Dashboard for a detailed health report on your AP. If this issue has not resolved itself within an hour, please reach out to chtc-infrastructure@g-groups.wisc.edu.

Best regards,
CHTC Infrastructure Services Team
"""

AP_REPAIR_COMPLETE_CONTENT = """
Hello {netid},

The operational issue with your Personal Access Point is now resolved. Please return to the AP dashboard for instructions to access your Personal AP.

Best regards,
CHTC Infrastructure Services Team
"""

def send_email(subject, content, to_address = TO_ADDRESS):
    """ Send an email with the given subject and content. Not configured for
    use outside the UW SMPT relay.
    """
    if not SEND_EMAILS:
        print("Would send email:", subject, content)
        return
    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = subject
    msg['From'] = FROM_ADDRESS
    msg['To'] = to_address
    s = smtplib.SMTP(os.environ['SMTP_HOST'])
    s.send_message(msg)
    s.quit()



##############################################################################
#
# Admin-Facing emails: Sent by the dashboard to notify admins that they
# need to take action on behalf of the user
#
##############################################################################


def send_dashboard_request_notification(netid: str, dashboard_request: DashboardRequestInfo):
    """Send a basic plaintext email notification about a new dashboard request."""
    send_email(
        DASHBOARD_REQUEST_SUBJECT.format(netid=netid),
        DASHBOARD_REQUEST_CONTENT.format(
            netid=netid,
            job_input_size=dashboard_request.job_input_size,
            job_output_size=dashboard_request.job_output_size,
            job_count=dashboard_request.job_count,
            concurrent_jobs=dashboard_request.concurrent_jobs,
            dagman='Yes' if dashboard_request.dagman else 'No',
            local_universe='Yes' if dashboard_request.local_universe else 'No'
        ))


def send_dashboard_cancellation_notification(netid: str):
    """Send a basic plaintext email notification about the cancellation of a dashboard request."""
    send_email(
        DASHBOARD_CANCELLATION_SUBJECT.format(netid=netid), 
        DASHBOARD_CANCELLATION_CONTENT.format(netid=netid))

def send_ap_repair_requested_notification(netid: str, dashboard_status: LiveDashboardStatus):
    """ Send an email notification about a user request for help fixing an AP. """
    send_email(
        DASHBOARD_REPAIR_REQUEST_SUBJECT.format(netid=netid),
        DASHBOARD_REPAIR_REQUEST_CONTENT.format(
            netid=netid,
            pod_health=dashboard_status.pod_health,
            pod_health_reason=dashboard_status.pod_health_reason,
            collector_health=dashboard_status.collector_health,
            collector_health_reason=dashboard_status.collector_health_reason,
            dashboard_health=dashboard_status.dashboard_health,
            dashboard_health_reason=dashboard_status.dashboard_health_reason)
    )
    
def send_slurm_account_requested_notification(netid: str):
    """Send email notification that a user has requested access to the Spark Slurm cluster."""
    send_email(
        SLURM_ACCOUNT_REQUEST_SUBJECT.format(netid=netid),
        SLURM_ACCOUNT_REQUEST_CONTENT.format(netid=netid)
    )


##############################################################################
#
# User-Facing emails: Sent by the dashboard to notify users that they
# need to wait for an admin-initiated action to progress their enrollment
#
##############################################################################

def send_chtc_account_provisioned_notification(netid: str):
    """Send email notification that CHTC account has been provisioned."""
    send_email(
        CHTC_ACCOUNT_READY_SUBJECT.format(netid=netid), 
        CHTC_ACCOUNT_READY_CONTENT.format(netid=netid), 
        f"{netid}@wisc.edu")


def send_slurm_request_confirmation_notification(netid: str):
    """Send email confirmation that Slurm account request has been received."""
    send_email(
        SLURM_REQUEST_CONFIRMATION_SUBJECT, 
        SLURM_REQUEST_CONFIRMATION_CONTENT.format(netid=netid), 
        f"{netid}@wisc.edu")


def send_slurm_account_provisioned_notification(netid: str):
    """Send email notification that Slurm account has been provisioned."""
    send_email(
        SLURM_ACCOUNT_READY_SUBJECT,
        SLURM_ACCOUNT_READY_CONTENT.format(netid=netid),
        f"{netid}@wisc.edu")


def send_ap_request_confirmation_notification(netid: str):
    """Send email confirmation that AP request has been received."""
    send_email(
        AP_REQUEST_CONFIRMATION_SUBJECT,
        AP_REQUEST_CONFIRMATION_CONTENT.format(netid=netid),
        f"{netid}@wisc.edu")


def send_ap_provisioning_started_notification(netid: str):
    """Send email notification that AP provisioning has started."""
    send_email(
        AP_PROVISIONING_STARTED_SUBJECT, 
        AP_PROVISIONING_STARTED_CONTENT.format(netid=netid), 
        f"{netid}@wisc.edu")


def send_ap_provisioning_complete_notification(netid: str):
    """Send email notification that AP has been provisioned and is ready."""
    send_email(
        AP_PROVISIONING_COMPLETE_SUBJECT,
        AP_PROVISIONING_COMPLETE_CONTENT.format(netid=netid),
        f"{netid}@wisc.edu")


def send_ap_health_degraded_notification(netid: str):
    """Send email notification that AP has detected health issues."""
    send_email(
         AP_HEALTH_DEGRADED_SUBJECT,
         AP_HEALTH_DEGRADED_CONTENT.format(netid=netid),
         f"{netid}@wisc.edu")


def send_ap_repair_complete_notification(netid: str):
    """Send email notification that AP has been repaired and is operational."""
    send_email(
         AP_REPAIR_COMPLETE_SUBJECT,
         AP_REPAIR_COMPLETE_CONTENT.format(netid=netid),
         f"{netid}@wisc.edu")
