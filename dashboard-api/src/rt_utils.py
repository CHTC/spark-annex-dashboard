import os
from datetime import datetime, timedelta
from rt_api_helper import RtApiHelper

RT_BASE_URL = os.environ.get("RT_BASE_URL", "https://crt.cs.wisc.edu/rt/REST/1.0/")
RT_USERNAME = os.environ.get("RT_USERNAME", "")
RT_PASSWORD = os.environ.get("RT_PASSWORD", "")
RT_QUEUE = os.environ.get("RT_QUEUE", "chtc-requests")
RT_SUBJECT = os.environ.get("RT_QUEUE", "CHTC Account Request")

def check_user_account_request_exists(netid: str) -> bool:
    now = datetime.now()
    last_month = (now - timedelta(days=31)).strftime("%Y-%m-%d")
    
    query_str = f"Created > '{last_month}' AND Queue = '{RT_QUEUE}' AND Requestors = '{netid}'"
    with RtApiHelper(RT_BASE_URL, RT_USERNAME, RT_PASSWORD) as rt:
        tickets = rt.request("/search/ticket", {"query": query_str})
        return len(tickets) > 0
