"""API tests for /api/instances endpoints."""
import uuid
from unittest.mock import MagicMock, patch

import pytest

from tests.conftest import make_instance, make_instance_task


class TestCreateInstance:
    @patch("app.api.routes.instances.InstanceService")
    def test_import_template_success(self, MockSvc, client, mock_db):
        instance = make_instance(num_tasks=2, completed_tasks=0)
        MockSvc.return_value.import_template.return_value = instance

        template_id = str(uuid.uuid4())
        user_id = str(instance.user_id)

        resp = client.post("/api/instances/", json={
            "template_id": template_id,
            "user_id": user_id,
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Nashville Highlights"
        assert data["status"] == "active"
        assert data["progress"]["completed_tasks"] == 0
        assert data["progress"]["total_tasks"] == 2
        assert len(data["tasks"]) == 2

    @patch("app.api.routes.instances.InstanceService")
    def test_import_template_not_found(self, MockSvc, client, mock_db):
        MockSvc.return_value.import_template.side_effect = ValueError("Template not found: xyz")

        resp = client.post("/api/instances/", json={
            "template_id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
        })
        assert resp.status_code == 404
        assert "Template not found" in resp.json()["detail"]


class TestListInstances:
    @patch("app.api.routes.instances.InstanceService")
    def test_list_returns_instances(self, MockSvc, client, mock_db):
        user_id = uuid.uuid4()
        instances = [
            make_instance(user_id=user_id, num_tasks=3, completed_tasks=1),
            make_instance(user_id=user_id, num_tasks=2, completed_tasks=2),
        ]
        MockSvc.return_value.list_instances.return_value = instances

        resp = client.get(f"/api/instances/?user_id={user_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert data[0]["progress"]["completed_tasks"] == 1
        assert data[1]["progress"]["is_complete"] is True

    @patch("app.api.routes.instances.InstanceService")
    def test_list_empty(self, MockSvc, client, mock_db):
        MockSvc.return_value.list_instances.return_value = []
        resp = client.get(f"/api/instances/?user_id={uuid.uuid4()}")
        assert resp.status_code == 200
        assert resp.json() == []


class TestGetInstance:
    @patch("app.api.routes.instances.InstanceService")
    def test_get_instance_success(self, MockSvc, client, mock_db):
        user_id = uuid.uuid4()
        instance = make_instance(user_id=user_id, num_tasks=3, completed_tasks=2)
        MockSvc.return_value.get_instance.return_value = instance

        resp = client.get(f"/api/instances/{instance.id}?user_id={user_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["progress"]["completed_tasks"] == 2
        assert data["progress"]["total_tasks"] == 3
        assert data["progress"]["percent"] == pytest.approx(66.7, abs=0.1)
        assert len(data["tasks"]) == 3

    @patch("app.api.routes.instances.InstanceService")
    def test_get_instance_not_found(self, MockSvc, client, mock_db):
        MockSvc.return_value.get_instance.return_value = None
        resp = client.get(f"/api/instances/{uuid.uuid4()}?user_id={uuid.uuid4()}")
        assert resp.status_code == 404

    @patch("app.api.routes.instances.InstanceService")
    def test_tasks_show_completion_status(self, MockSvc, client, mock_db):
        user_id = uuid.uuid4()
        instance = make_instance(user_id=user_id, num_tasks=2, completed_tasks=1)
        MockSvc.return_value.get_instance.return_value = instance

        resp = client.get(f"/api/instances/{instance.id}?user_id={user_id}")
        tasks = resp.json()["tasks"]
        completed_flags = [t["is_completed"] for t in tasks]
        assert True in completed_flags
        assert False in completed_flags


# ── Sprint 2 API tests ──────────────────────────────────────────────


class TestDeleteInstance:
    @patch("app.api.routes.instances.InstanceService")
    def test_delete_success(self, MockSvc, client, mock_db):
        MockSvc.return_value.delete_instance.return_value = True
        resp = client.delete(f"/api/instances/{uuid.uuid4()}?user_id={uuid.uuid4()}")
        assert resp.status_code == 200
        assert resp.json()["status"] == "deleted"

    @patch("app.api.routes.instances.InstanceService")
    def test_delete_not_found(self, MockSvc, client, mock_db):
        MockSvc.return_value.delete_instance.return_value = False
        resp = client.delete(f"/api/instances/{uuid.uuid4()}?user_id={uuid.uuid4()}")
        assert resp.status_code == 404


class TestUpdateInstanceStatus:
    @patch("app.api.routes.instances.InstanceService")
    def test_update_to_archived(self, MockSvc, client, mock_db):
        user_id = uuid.uuid4()
        instance = make_instance(user_id=user_id, status="archived")
        MockSvc.return_value.update_status.return_value = instance

        resp = client.patch(
            f"/api/instances/{instance.id}?user_id={user_id}",
            json={"status": "archived"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "archived"

    @patch("app.api.routes.instances.InstanceService")
    def test_update_to_completed(self, MockSvc, client, mock_db):
        user_id = uuid.uuid4()
        instance = make_instance(user_id=user_id, status="completed", num_tasks=2, completed_tasks=2)
        MockSvc.return_value.update_status.return_value = instance

        resp = client.patch(
            f"/api/instances/{instance.id}?user_id={user_id}",
            json={"status": "completed"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "completed"

    @patch("app.api.routes.instances.InstanceService")
    def test_update_invalid_status(self, MockSvc, client, mock_db):
        MockSvc.return_value.update_status.side_effect = ValueError("Invalid status: banana")
        resp = client.patch(
            f"/api/instances/{uuid.uuid4()}?user_id={uuid.uuid4()}",
            json={"status": "banana"},
        )
        assert resp.status_code == 400

    @patch("app.api.routes.instances.InstanceService")
    def test_update_not_found(self, MockSvc, client, mock_db):
        MockSvc.return_value.update_status.return_value = None
        resp = client.patch(
            f"/api/instances/{uuid.uuid4()}?user_id={uuid.uuid4()}",
            json={"status": "archived"},
        )
        assert resp.status_code == 404


class TestUpdateTask:
    @patch("app.api.routes.instances.InstanceService")
    def test_update_notes(self, MockSvc, client, mock_db):
        user_id = uuid.uuid4()
        task = make_instance_task(notes="Updated note")
        MockSvc.return_value.update_task.return_value = task

        resp = client.patch(
            f"/api/instances/{uuid.uuid4()}/tasks/{task.id}?user_id={user_id}",
            json={"notes": "Updated note"},
        )
        assert resp.status_code == 200
        assert resp.json()["notes"] == "Updated note"

    @patch("app.api.routes.instances.InstanceService")
    def test_update_task_not_found(self, MockSvc, client, mock_db):
        MockSvc.return_value.update_task.return_value = None
        resp = client.patch(
            f"/api/instances/{uuid.uuid4()}/tasks/{uuid.uuid4()}?user_id={uuid.uuid4()}",
            json={"notes": "x"},
        )
        assert resp.status_code == 404


class TestDeleteTask:
    @patch("app.api.routes.instances.InstanceService")
    def test_delete_task_success(self, MockSvc, client, mock_db):
        MockSvc.return_value.delete_task.return_value = True
        resp = client.delete(
            f"/api/instances/{uuid.uuid4()}/tasks/{uuid.uuid4()}?user_id={uuid.uuid4()}"
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "deleted"

    @patch("app.api.routes.instances.InstanceService")
    def test_delete_task_not_found(self, MockSvc, client, mock_db):
        MockSvc.return_value.delete_task.return_value = False
        resp = client.delete(
            f"/api/instances/{uuid.uuid4()}/tasks/{uuid.uuid4()}?user_id={uuid.uuid4()}"
        )
        assert resp.status_code == 404
