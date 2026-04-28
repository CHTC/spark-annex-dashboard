"""
Tests for poll_userapp_user_status: verifies that DB updates and notification emails
are sent correctly for all combinations of current user state and updated state
returned by get_userapp_user_status.

Puppet wait guard logic:
  - updated_at is None                → guard blocks spark (unknown change time)
  - updated_at is within PUPPET_WAIT_TIME of last puppet run → guard blocks spark
  - updated_at is beyond PUPPET_WAIT_TIME before last puppet run → guard allows spark
"""

from dataclasses import dataclass
from datetime import datetime

import pytz
import pytest

from src.db_models import RequestStatus
from src.poll_user_status import poll_userapp_user_status
from .mock_json_responses import (
    MockJsonResponse,
    TEST_NETID,
    USER_NOT_IN_USERAPP,
    USER_ACTIVE_NO_SUBMIT_NODES,
    USER_ACTIVE_WITH_SPARK_NODE,
    USER_INACTIVE_NO_FORMS,
    USER_INACTIVE_NON_HPC_FORM,
    USER_INACTIVE_HPC_FORM,
)


# ---------------------------------------------------------------------------
# Mock helpers
# ---------------------------------------------------------------------------

@dataclass
class MockDbUser:
    """Minimal stand-in for a DB user record returned by get_not_fully_registered_users."""
    netid: str
    chtc_account: RequestStatus
    spark_account: RequestStatus
    updated_at: datetime | None = None


# ---------------------------------------------------------------------------
# Fixed timestamps
# ---------------------------------------------------------------------------

# Naive Central Time timestamp as returned by check_icinga_puppet_update_time.
# CDT = UTC-5, so the UTC equivalent is 17:00.
PUPPET_RUN_CT  = datetime(2024, 6, 1, 12, 0, 0)
PUPPET_RUN_UTC = datetime(2024, 6, 1, 17, 0, 0, tzinfo=pytz.UTC)

# With PUPPET_WAIT_TIME = 2 hours (the default):
#   PUPPET_RUN_UTC - UPDATED_AT_OLD_ENOUGH = 3h >= 2h  → guard should PASS
UPDATED_AT_OLD_ENOUGH = datetime(2024, 6, 1, 14, 0, 0, tzinfo=pytz.UTC)
#   PUPPET_RUN_UTC - UPDATED_AT_TOO_RECENT = 1h  < 2h  → guard should BLOCK
UPDATED_AT_TOO_RECENT = datetime(2024, 6, 1, 16, 0, 0, tzinfo=pytz.UTC)


# ---------------------------------------------------------------------------
# Base test class
# ---------------------------------------------------------------------------

class PollUserStatusTest:
    """
    Base class that wires up all external mocks before each test and provides
    convenience helpers for setting per-test inputs and asserting outcomes.
    """

    @pytest.fixture(autouse=True)
    def setup_mocks(self, mocker):
        mocker.patch(
            "src.poll_user_status.check_icinga_puppet_update_time",
            return_value=PUPPET_RUN_CT,
        )
        self.mock_db_update = mocker.patch(
            "src.poll_user_status.db.update_user_chtc_account_status_from_userapp"
        )
        self.mock_chtc_notify = mocker.patch(
            "src.poll_user_status.send_chtc_account_provisioned_notification"
        )
        self.mock_slurm_notify = mocker.patch(
            "src.poll_user_status.send_slurm_account_provisioned_notification"
        )

    def set_db_users(self, mocker, users: list[MockDbUser]):
        mocker.patch(
            "src.poll_user_status.db.get_not_fully_registered_users",
            return_value=users,
        )

    def set_db_user(
        self,
        mocker,
        chtc_account: RequestStatus,
        spark_account: RequestStatus,
        updated_at: datetime | None = None,
    ):
        self.set_db_users(mocker, [MockDbUser(TEST_NETID, chtc_account, spark_account, updated_at=updated_at)])

    def set_userapp_response(self, mocker, json_data):
        mocker.patch(
            "src.userapp_utils.requests.get",
            return_value=MockJsonResponse(json_data=json_data),
        )

    # --- assertion helpers ---

    def assert_no_changes(self):
        self.mock_db_update.assert_not_called()
        self.mock_chtc_notify.assert_not_called()
        self.mock_slurm_notify.assert_not_called()

    def assert_chtc_notification_sent(self):
        self.mock_db_update.assert_called_once()
        self.mock_chtc_notify.assert_called_once_with(TEST_NETID)
        self.mock_slurm_notify.assert_not_called()

    def assert_slurm_notification_sent(self):
        self.mock_db_update.assert_called_once()
        self.mock_slurm_notify.assert_called_once_with(TEST_NETID)
        self.mock_chtc_notify.assert_not_called()


# ---------------------------------------------------------------------------
# Test groups
# ---------------------------------------------------------------------------

class TestNoUsersToProcess(PollUserStatusTest):
    """No users in the DB → nothing should happen regardless of userapp state."""

    def test_empty_user_list(self, mocker):
        self.set_db_users(mocker, [])
        self.set_userapp_response(mocker, USER_NOT_IN_USERAPP)
        poll_userapp_user_status()
        self.assert_no_changes()


class TestNoStatusChange(PollUserStatusTest):
    """
    Userapp returns a status that is equal to or lower than what is already in the
    DB. No DB write or notification should occur.
    """

    def test_not_requested_user_not_in_userapp(self, mocker):
        # User has no DB state and is not found in the userapp at all.
        self.set_db_user(mocker, RequestStatus.NOT_REQUESTED, RequestStatus.NOT_REQUESTED)
        self.set_userapp_response(mocker, USER_NOT_IN_USERAPP)
        poll_userapp_user_status()
        self.assert_no_changes()

    def test_request_received_user_not_in_userapp(self, mocker):
        # User already has REQUEST_RECEIVED in DB but is not (yet) in the userapp.
        self.set_db_user(mocker, RequestStatus.REQUEST_RECEIVED, RequestStatus.NOT_REQUESTED)
        self.set_userapp_response(mocker, USER_NOT_IN_USERAPP)
        poll_userapp_user_status()
        self.assert_no_changes()

    def test_inactive_user_no_forms(self, mocker):
        # Inactive user with no forms → userapp status is NOT_REQUESTED/NOT_REQUESTED.
        self.set_db_user(mocker, RequestStatus.NOT_REQUESTED, RequestStatus.NOT_REQUESTED)
        self.set_userapp_response(mocker, [USER_INACTIVE_NO_FORMS])
        poll_userapp_user_status()
        self.assert_no_changes()

    def test_inactive_user_non_hpc_form_chtc_already_received(self, mocker):
        # Inactive user with a non-HPC form; DB already has REQUEST_RECEIVED for chtc.
        # Userapp returns REQUEST_RECEIVED which is not an upgrade → no change.
        self.set_db_user(mocker, RequestStatus.REQUEST_RECEIVED, RequestStatus.NOT_REQUESTED)
        self.set_userapp_response(mocker, [USER_INACTIVE_NON_HPC_FORM])
        poll_userapp_user_status()
        self.assert_no_changes()

    def test_inactive_user_hpc_form_both_already_received(self, mocker):
        # Inactive user with an HPC form; DB already has REQUEST_RECEIVED for both.
        self.set_db_user(mocker, RequestStatus.REQUEST_RECEIVED, RequestStatus.REQUEST_RECEIVED)
        self.set_userapp_response(mocker, [USER_INACTIVE_HPC_FORM])
        poll_userapp_user_status()
        self.assert_no_changes()

    def test_active_user_chtc_already_complete_no_spark(self, mocker):
        # CHTC account is already COMPLETE in the DB; userapp also reports COMPLETE
        # with no spark node → spark stays NOT_REQUESTED, nothing changes.
        self.set_db_user(mocker, RequestStatus.COMPLETE, RequestStatus.NOT_REQUESTED)
        self.set_userapp_response(mocker, [USER_ACTIVE_NO_SUBMIT_NODES])
        poll_userapp_user_status()
        self.assert_no_changes()


class TestChtcAccountBecomesComplete(PollUserStatusTest):
    """
    Userapp reports the CHTC account as newly COMPLETE (spark not yet COMPLETE).
    A CHTC-provisioned notification should be sent.
    """

    def test_from_not_requested(self, mocker):
        # NOT_REQUESTED → COMPLETE for chtc; spark remains NOT_REQUESTED.
        self.set_db_user(mocker, RequestStatus.NOT_REQUESTED, RequestStatus.NOT_REQUESTED)
        self.set_userapp_response(mocker, [USER_ACTIVE_NO_SUBMIT_NODES])
        poll_userapp_user_status()
        self.assert_chtc_notification_sent()

    def test_from_request_received(self, mocker):
        # REQUEST_RECEIVED → COMPLETE for chtc; spark remains NOT_REQUESTED.
        self.set_db_user(mocker, RequestStatus.REQUEST_RECEIVED, RequestStatus.NOT_REQUESTED)
        self.set_userapp_response(mocker, [USER_ACTIVE_NO_SUBMIT_NODES])
        poll_userapp_user_status()
        self.assert_chtc_notification_sent()

    def test_chtc_complete_spark_would_complete_but_puppet_wait_blocks(self, mocker):
        # Userapp reports both COMPLETE, but the puppet guard blocks the spark
        # status because updated_at is too recent. Only the chtc transition is
        # visible → chtc notification only.
        self.set_db_user(mocker, RequestStatus.NOT_REQUESTED, RequestStatus.NOT_REQUESTED, updated_at=UPDATED_AT_TOO_RECENT)
        self.set_userapp_response(mocker, [USER_ACTIVE_WITH_SPARK_NODE])
        poll_userapp_user_status()
        self.assert_chtc_notification_sent()

    def test_chtc_complete_spark_would_complete_but_no_updated_at(self, mocker):
        # Same as above but updated_at is None (new user with no recorded change time).
        self.set_db_user(mocker, RequestStatus.NOT_REQUESTED, RequestStatus.NOT_REQUESTED)
        self.set_userapp_response(mocker, [USER_ACTIVE_WITH_SPARK_NODE])
        poll_userapp_user_status()
        self.assert_chtc_notification_sent()


class TestSparkAccountBecomesComplete(PollUserStatusTest):
    """
    Userapp reports the spark account as newly COMPLETE. The puppet wait guard
    controls whether this transition is accepted.
    """

    def test_puppet_wait_satisfied(self, mocker):
        # updated_at is old enough → guard passes → spark transitions to COMPLETE.
        # chtc was already COMPLETE → slurm notification is sent.
        self.set_db_user(mocker, RequestStatus.COMPLETE, RequestStatus.REQUEST_RECEIVED, updated_at=UPDATED_AT_OLD_ENOUGH)
        self.set_userapp_response(mocker, [USER_ACTIVE_WITH_SPARK_NODE])
        poll_userapp_user_status()
        self.assert_slurm_notification_sent()

    def test_puppet_wait_satisfied_spark_from_not_requested(self, mocker):
        # spark goes directly from NOT_REQUESTED to COMPLETE when puppet guard passes.
        self.set_db_user(mocker, RequestStatus.COMPLETE, RequestStatus.NOT_REQUESTED, updated_at=UPDATED_AT_OLD_ENOUGH)
        self.set_userapp_response(mocker, [USER_ACTIVE_WITH_SPARK_NODE])
        poll_userapp_user_status()
        self.assert_slurm_notification_sent()

    def test_puppet_wait_not_satisfied(self, mocker):
        # updated_at is too recent → guard blocks spark → no transition → no notification.
        self.set_db_user(mocker, RequestStatus.COMPLETE, RequestStatus.REQUEST_RECEIVED, updated_at=UPDATED_AT_TOO_RECENT)
        self.set_userapp_response(mocker, [USER_ACTIVE_WITH_SPARK_NODE])
        poll_userapp_user_status()
        self.assert_no_changes()

    def test_puppet_wait_no_updated_at(self, mocker):
        # updated_at is None → guard blocks spark → no transition → no notification.
        self.set_db_user(mocker, RequestStatus.COMPLETE, RequestStatus.REQUEST_RECEIVED)
        self.set_userapp_response(mocker, [USER_ACTIVE_WITH_SPARK_NODE])
        poll_userapp_user_status()
        self.assert_no_changes()


class TestBothAccountsBecomeComplete(PollUserStatusTest):
    """
    Both chtc and spark become COMPLETE in a single poll cycle (e.g. user was
    provisioned fully before we ever detected either transition).
    """

    def test_from_not_requested_puppet_wait_satisfied(self, mocker):
        # NOT_REQUESTED/NOT_REQUESTED → COMPLETE/COMPLETE with puppet guard passing.
        self.set_db_user(mocker, RequestStatus.NOT_REQUESTED, RequestStatus.NOT_REQUESTED, updated_at=UPDATED_AT_OLD_ENOUGH)
        self.set_userapp_response(mocker, [USER_ACTIVE_WITH_SPARK_NODE])
        poll_userapp_user_status()
        self.assert_slurm_notification_sent()

    def test_from_request_received_puppet_wait_satisfied(self, mocker):
        # REQUEST_RECEIVED/REQUEST_RECEIVED → COMPLETE/COMPLETE with puppet guard passing.
        self.set_db_user(mocker, RequestStatus.REQUEST_RECEIVED, RequestStatus.REQUEST_RECEIVED, updated_at=UPDATED_AT_OLD_ENOUGH)
        self.set_userapp_response(mocker, [USER_ACTIVE_WITH_SPARK_NODE])
        poll_userapp_user_status()
        self.assert_slurm_notification_sent()