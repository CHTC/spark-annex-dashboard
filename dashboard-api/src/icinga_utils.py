"""
Utility functions for interacting with the Icinga monitoring system.
Used to determine the last user account update time on the Slurm cluster login node.
"""

import requests
import os
import re
from datetime import datetime
from typing import Any

# Icinga base URL
ICINGA_BASE_URL = os.environ.get('ICINGA_BASE_URL', 'https://icinga0000.chtc.wisc.edu:5665')
# Icinga credentials
ICINGA_USER = os.environ.get('ICINGA_USER')
ICINGA_PASSWORD = os.environ.get('ICINGA_PASSWORD')
# Spark login node name
SPARK_LOGIN_NODE = os.environ.get('SPARK_LOGIN_NODE', 'spark-login')
# Static URL to query icinga for the last puppet runtime on the spark login node
ICINGA_URL = f'{ICINGA_BASE_URL}/v1/objects/services?filter=match(%22{SPARK_LOGIN_NODE}*puppet%22,service.__name)'

def extract_puppet_last_run_time(service_obj: dict) -> datetime:
    """
    Safely extract the puppet last run datetime from an Icinga service object.

    Expected output format: "OK - puppet last ran 2026-03-06T12:00:50 - environment: puppet8"

    Args:
        service_obj: The service object from Icinga API response

    Returns:
        datetime object parsed from the output string

    Raises:
        ValueError: If required fields are missing or datetime string cannot be parsed
    """
    # Safely navigate nested structure with null checks
    attrs: dict[str, Any] = service_obj.get("attrs", {})
    if not attrs:
        raise ValueError("Missing or invalid 'attrs' field in service object")

    last_check_result: dict[str, Any] = attrs.get("last_check_result", {})
    if not last_check_result:
        raise ValueError("Missing or invalid 'last_check_result' field in attrs")

    output: str = last_check_result.get("output", "")
    if not output:
        raise ValueError("Missing or invalid 'output' field in last_check_result")

    # Pattern to match ISO 8601 datetime format (YYYY-MM-DDTHH:MM:SS)
    pattern = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})'
    match = re.search(pattern, output)

    if not match:
        raise ValueError(f"Could not find datetime in puppet check output: {output}")

    datetime_str = match.group(1)
    return datetime.fromisoformat(datetime_str)


def check_icinga_puppet_update_time() -> datetime:
    """
    Check the last puppet update time for the Spark login node via Icinga API.

    Returns:
        datetime object of the last puppet run

    Raises:
        requests.exceptions.RequestException: If the API request fails
        ValueError: If the response format is unexpected or no service is found
    """
    response = requests.get(ICINGA_URL, auth=(f"{ICINGA_USER}", f"{ICINGA_PASSWORD}"), verify=False)
    response.raise_for_status()
    data = response.json()
    return extract_puppet_last_run_time(data["results"][0])
