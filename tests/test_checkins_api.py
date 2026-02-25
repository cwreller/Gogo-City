"""API tests for /api/check-ins endpoints."""
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from app.models.checkin import CheckIn
from app.models.route import InstanceTask, RouteInstance
from app.models.user import User
from app.services.verification_service import VerificationResult
from tests.conftest import TEST_USER_ID


# ── Helpers ──────────────────────────────────────────────────────────

def _make_task(
    *,
    task_id=None,
    instance_id=None,
    verification_type="gps",
    lat=Decimal("36.1627"),
    lng=Decimal("-86.7816"),
    already_checked_in=False,
    xp=100,
):
    task = MagicMock(spec=InstanceTask)
    task.id = task_id or uuid.uuid4()
    task.instance_id = instance_id or uuid.uuid4()
    task.name = "Visit the Parthenon"
    task.task_description = "Take a photo at the Parthenon"
    task.verification_type = verification_type
    task.lat = lat
    task.lng = lng
    task.xp = xp
    task.check_in = MagicMock() if already_checked_in else None
    return task


def _make_mock_user(user_id=None, total_xp=0):
    user = MagicMock(spec=User)
    user.id = user_id or TEST_USER_ID
    user.total_xp = total_xp
    return user


def _make_instance(*, instance_id=None, user_id=None, num_tasks=2, completed=0):
    inst = MagicMock(spec=RouteInstance)
    inst.id = instance_id or uuid.uuid4()
    inst.user_id = user_id or TEST_USER_ID
    inst.status = "active"
    inst.is_complete = completed == num_tasks and num_tasks > 0

    tasks = []
    for i in range(num_tasks):
        t = _make_task(instance_id=inst.id)
        t.check_in = MagicMock() if i < completed else None
        tasks.append(t)
    inst.tasks = tasks
    return inst


def _make_check_in(task_id=None, user_id=None):
    ci = MagicMock(spec=CheckIn)
    ci.id = uuid.uuid4()
    ci.instance_task_id = task_id or uuid.uuid4()
    ci.user_id = user_id or TEST_USER_ID
    ci.verified_by = "gps"
    ci.lat = Decimal("36.1627")
    ci.lng = Decimal("-86.7816")
    ci.checked_in_at = datetime.now(timezone.utc)
    return ci


def _db_with_task_and_instance(mock_db, task, instance, user=None):
    """Wire mock_db so queries return the right objects for the create_check_in flow."""
    mock_user = user or _make_mock_user()

    def query_side_effect(model):
        q = MagicMock()
        if model is InstanceTask:
            q.options.return_value.filter.return_value.first.return_value = task
        elif model is RouteInstance:
            q.filter.return_value.first.return_value = instance
            q.options.return_value.filter.return_value.first.return_value = instance
        elif model is User:
            q.filter.return_value.first.return_value = mock_user
        else:
            q.join.return_value.filter.return_value.all.return_value = []
        return q

    mock_db.query.side_effect = query_side_effect
    return mock_db


# ── POST /check-ins ───────────────────────────────────────────────────

class TestCreateCheckIn:

    @patch("app.api.routes.checkins.VerificationService")
    def test_gps_checkin_success(self, MockVerify, client, mock_db):
        """GPS check-in within range returns 200 and check-in data."""
        task = _make_task(verification_type="gps")
        instance = _make_instance(instance_id=task.instance_id)
        _db_with_task_and_instance(mock_db, task, instance)

        ci = _make_check_in(task_id=task.id)
        mock_db.refresh.side_effect = lambda obj, *a: None
        MockVerify.return_value.verify.return_value = VerificationResult(
            passed=True, method="gps", reason="Within range (50m away, limit is 150m)"
        )

        with patch("app.api.routes.checkins.CheckIn", return_value=ci):
            resp = client.post("/api/check-ins/", json={
                "instance_task_id": str(task.id),
                "user_lat": 36.1627,
                "user_lng": -86.7816,
            })

        assert resp.status_code == 200
        data = resp.json()
        assert data["verified"] is True
        assert data["verified_by"] == "gps"
        assert data["xp_earned"] == 100

    @patch("app.api.routes.checkins.VerificationService")
    def test_photo_checkin_success(self, MockVerify, client, mock_db):
        """Photo check-in with valid photo returns 200."""
        task = _make_task(verification_type="photo", lat=None, lng=None)
        instance = _make_instance(instance_id=task.instance_id)
        _db_with_task_and_instance(mock_db, task, instance)

        ci = _make_check_in(task_id=task.id)
        ci.verified_by = "photo"
        mock_db.refresh.side_effect = lambda obj, *a: None
        MockVerify.return_value.verify.return_value = VerificationResult(
            passed=True, method="photo", reason="Photo shows relevant content"
        )

        with patch("app.api.routes.checkins.CheckIn", return_value=ci):
            resp = client.post("/api/check-ins/", json={
                "instance_task_id": str(task.id),
                "photo_base64": "aGVsbG8=",
            })

        assert resp.status_code == 200
        assert resp.json()["verified_by"] == "photo"

    def test_task_not_found(self, client, mock_db):
        """404 when instance task ID doesn't exist."""
        mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = None

        resp = client.post("/api/check-ins/", json={
            "instance_task_id": str(uuid.uuid4()),
        })
        assert resp.status_code == 404
        assert "Instance task not found" in resp.json()["detail"]

    def test_duplicate_checkin(self, client, mock_db):
        """409 when task already has a check-in."""
        task = _make_task(already_checked_in=True)
        mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = task

        resp = client.post("/api/check-ins/", json={
            "instance_task_id": str(task.id),
        })
        assert resp.status_code == 409
        assert "Already checked in" in resp.json()["detail"]

    def test_wrong_user_forbidden(self, client, mock_db):
        """403 when the instance belongs to a different user."""
        task = _make_task()
        other_user_id = uuid.uuid4()
        instance = _make_instance(instance_id=task.instance_id, user_id=other_user_id)
        _db_with_task_and_instance(mock_db, task, instance)

        resp = client.post("/api/check-ins/", json={
            "instance_task_id": str(task.id),
        })
        assert resp.status_code == 403
        assert "not your route instance" in resp.json()["detail"]

    @patch("app.api.routes.checkins.VerificationService")
    def test_gps_verification_fail(self, MockVerify, client, mock_db):
        """422 when GPS check fails (too far away)."""
        task = _make_task(verification_type="gps")
        instance = _make_instance(instance_id=task.instance_id)
        _db_with_task_and_instance(mock_db, task, instance)

        MockVerify.return_value.verify.return_value = VerificationResult(
            passed=False, method="gps", reason="Too far away (800m, need to be within 150m)"
        )

        resp = client.post("/api/check-ins/", json={
            "instance_task_id": str(task.id),
            "user_lat": 36.1900,
            "user_lng": -86.8000,
        })
        assert resp.status_code == 422
        detail = resp.json()["detail"]
        assert detail["verified"] is False
        assert "Too far away" in detail["reason"]

    @patch("app.api.routes.checkins.VerificationService")
    def test_photo_verification_fail(self, MockVerify, client, mock_db):
        """422 when photo check fails (no recognizable content)."""
        task = _make_task(verification_type="photo", lat=None, lng=None)
        instance = _make_instance(instance_id=task.instance_id)
        _db_with_task_and_instance(mock_db, task, instance)

        MockVerify.return_value.verify.return_value = VerificationResult(
            passed=False, method="photo", reason="Photo does not show relevant content"
        )

        resp = client.post("/api/check-ins/", json={
            "instance_task_id": str(task.id),
            "photo_base64": "aGVsbG8=",
        })
        assert resp.status_code == 422
        assert resp.json()["detail"]["verified"] is False


# ── GET /check-ins/instance/{id} ─────────────────────────────────────

class TestGetInstanceCheckIns:

    def test_returns_check_ins(self, client, mock_db):
        """Returns list of check-ins for the authenticated user's instance."""
        instance = _make_instance()
        task = instance.tasks[0]

        ci = _make_check_in(task_id=task.id)
        ci.instance_task = task

        def query_side_effect(model):
            q = MagicMock()
            if model is RouteInstance:
                q.filter.return_value.first.return_value = instance
            elif model is CheckIn:
                q.join.return_value.filter.return_value.all.return_value = [ci]
            return q

        mock_db.query.side_effect = query_side_effect

        resp = client.get(f"/api/check-ins/instance/{instance.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["verified_by"] == "gps"

    def test_empty_list(self, client, mock_db):
        """Returns empty list if no check-ins yet."""
        instance = _make_instance()

        def query_side_effect(model):
            q = MagicMock()
            if model is RouteInstance:
                q.filter.return_value.first.return_value = instance
            elif model is CheckIn:
                q.join.return_value.filter.return_value.all.return_value = []
            return q

        mock_db.query.side_effect = query_side_effect

        resp = client.get(f"/api/check-ins/instance/{instance.id}")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_instance_not_found(self, client, mock_db):
        """404 when instance doesn't exist."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        resp = client.get(f"/api/check-ins/instance/{uuid.uuid4()}")
        assert resp.status_code == 404

    def test_wrong_user_forbidden(self, client, mock_db):
        """403 when instance belongs to a different user."""
        instance = _make_instance(user_id=uuid.uuid4())
        mock_db.query.return_value.filter.return_value.first.return_value = instance

        resp = client.get(f"/api/check-ins/instance/{instance.id}")
        assert resp.status_code == 403


# ── GET /check-ins/instance/{id}/progress ────────────────────────────

class TestGetInstanceProgress:

    def _setup_db(self, mock_db, instance):
        def query_side_effect(model):
            q = MagicMock()
            if model is RouteInstance:
                q.options.return_value.filter.return_value.first.return_value = instance
                q.filter.return_value.first.return_value = instance
            return q
        mock_db.query.side_effect = query_side_effect

    def test_partial_progress(self, client, mock_db):
        """Returns correct counts for a partially completed instance."""
        instance = _make_instance(num_tasks=3, completed=1)
        self._setup_db(mock_db, instance)

        resp = client.get(f"/api/check-ins/instance/{instance.id}/progress")
        assert resp.status_code == 200
        data = resp.json()
        assert data["completed"] == 1
        assert data["total"] == 3
        assert data["progress_pct"] == 33

    def test_fully_complete(self, client, mock_db):
        """100% progress when all tasks are checked in."""
        instance = _make_instance(num_tasks=2, completed=2)
        self._setup_db(mock_db, instance)

        resp = client.get(f"/api/check-ins/instance/{instance.id}/progress")
        assert resp.status_code == 200
        data = resp.json()
        assert data["completed"] == 2
        assert data["total"] == 2
        assert data["progress_pct"] == 100

    def test_zero_tasks(self, client, mock_db):
        """0% progress when instance has no tasks."""
        instance = _make_instance(num_tasks=0, completed=0)
        self._setup_db(mock_db, instance)

        resp = client.get(f"/api/check-ins/instance/{instance.id}/progress")
        assert resp.status_code == 200
        assert resp.json()["progress_pct"] == 0

    def test_instance_not_found(self, client, mock_db):
        """404 when instance doesn't exist."""
        mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = None

        resp = client.get(f"/api/check-ins/instance/{uuid.uuid4()}/progress")
        assert resp.status_code == 404

    def test_wrong_user_forbidden(self, client, mock_db):
        """403 when the instance belongs to a different user."""
        instance = _make_instance(user_id=uuid.uuid4())

        def query_side_effect(model):
            q = MagicMock()
            q.options.return_value.filter.return_value.first.return_value = instance
            q.filter.return_value.first.return_value = instance
            return q

        mock_db.query.side_effect = query_side_effect

        resp = client.get(f"/api/check-ins/instance/{instance.id}/progress")
        assert resp.status_code == 403
