"""API tests for /api/routes/share and /api/routes/import endpoints."""
import uuid
from unittest.mock import MagicMock, patch

import pytest

from tests.conftest import make_instance, make_template


class TestPreviewSharedRoute:
    @patch("app.api.routes.sharing.InstanceService")
    def test_preview_success(self, MockSvc, client, mock_db):
        template = make_template(share_code="ABC12345", num_tasks=2)
        MockSvc.return_value.preview_shared_route.return_value = template

        resp = client.get("/api/routes/share/ABC12345")
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Nashville Highlights"
        assert data["share_code"] == "ABC12345"
        assert len(data["tasks"]) == 2
        assert data["estimated_duration_minutes"] == 180
        assert "foodie" in data["vibe_tags"]

    @patch("app.api.routes.sharing.InstanceService")
    def test_preview_not_found(self, MockSvc, client, mock_db):
        MockSvc.return_value.preview_shared_route.return_value = None
        resp = client.get("/api/routes/share/INVALID")
        assert resp.status_code == 404
        assert "Shared route not found" in resp.json()["detail"]

    @patch("app.api.routes.sharing.InstanceService")
    def test_preview_tasks_always_not_completed(self, MockSvc, client, mock_db):
        template = make_template(num_tasks=3)
        MockSvc.return_value.preview_shared_route.return_value = template

        resp = client.get("/api/routes/share/ABC12345")
        tasks = resp.json()["tasks"]
        assert all(t["is_completed"] is False for t in tasks)


class TestImportSharedRoute:
    @patch("app.api.routes.sharing.InstanceService")
    def test_import_creates_independent_instance(self, MockSvc, client, mock_db):
        user_id = uuid.uuid4()
        instance = make_instance(user_id=user_id, num_tasks=3, completed_tasks=0)
        MockSvc.return_value.import_shared_route.return_value = instance

        resp = client.post("/api/routes/import/ABC12345", json={
            "user_id": str(user_id),
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "active"
        assert data["progress"]["completed_tasks"] == 0
        assert data["progress"]["total_tasks"] == 3
        assert len(data["tasks"]) == 3

    @patch("app.api.routes.sharing.InstanceService")
    def test_import_bad_share_code(self, MockSvc, client, mock_db):
        MockSvc.return_value.import_shared_route.side_effect = ValueError(
            "No route found for share code: NOPE"
        )
        resp = client.post("/api/routes/import/NOPE", json={
            "user_id": str(uuid.uuid4()),
        })
        assert resp.status_code == 404

    @patch("app.api.routes.sharing.InstanceService")
    def test_two_imports_are_independent(self, MockSvc, client, mock_db):
        """Importing the same share code twice should produce distinct instances."""
        user_a = uuid.uuid4()
        user_b = uuid.uuid4()
        inst_a = make_instance(user_id=user_a, num_tasks=2)
        inst_b = make_instance(user_id=user_b, num_tasks=2)
        MockSvc.return_value.import_shared_route.side_effect = [inst_a, inst_b]

        resp_a = client.post("/api/routes/import/SHARED", json={"user_id": str(user_a)})
        resp_b = client.post("/api/routes/import/SHARED", json={"user_id": str(user_b)})

        assert resp_a.status_code == 201
        assert resp_b.status_code == 201
        assert resp_a.json()["id"] != resp_b.json()["id"]
