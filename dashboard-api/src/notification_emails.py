import os
import smtplib
from email.message import EmailMessage
from api_models import DashboardRequestInfo


def send_email(subject, content):
    """ Send an email with the given subject and content. Not configured for
    use outside the UW SMPT relay.
    """
    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = subject
    msg['From'] = os.environ['FROM_ADDRESS']
    msg['To'] = os.environ['TO_ADDRESS'].split(',')
    s = smtplib.SMTP(os.environ['SMTP_HOST'])
    s.send_message(msg)
    s.quit()


def send_dashboard_request_notification(netid: str, dashboard_request: DashboardRequestInfo):
    """Send a basic plaintext email notification about a new dashboard request."""
    subject = f"New AP Dashboard Request from {netid}"
    content = f"""
A new AP dashboard has been requested by user {netid} with the following parameters:
Job Input Size (GB): {dashboard_request.job_input_size}
Job Output Size (GB): {dashboard_request.job_output_size}
Job Count: {dashboard_request.job_count}
Concurrent Jobs: {dashboard_request.concurrent_jobs}
DAGMan: {'Yes' if dashboard_request.dagman else 'No'}
Local Universe: {'Yes' if dashboard_request.local_universe else 'No'}
"""
    send_email(subject, content)
