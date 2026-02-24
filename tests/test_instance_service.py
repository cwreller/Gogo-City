"""Unit tests for InstanceService business logic."""
import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.services.instance_service import InstanceService
from tests.conftest import make_instance, make_template


class TestImportTemplate:
    def test_creates_instance_from_template(self, mock_db):
        template = make_template(num_tasks=3)
        user_id = uuid.uuid4()

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = template

        mock_db.flush = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()

        svc = InstanceService(mock_db)
        svc.import_template(template.id, user_id)

        assert mock_db.add.call_count == 1 + 3  # 1 instance + 3 tasks

    def test_raises_on_missing_template(self, mock_db):
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        svc = InstanceService(mock_db)
        with pytest.raises(ValueError, match="Template not found"):
            svc.import_template(uuid.uuid4(), uuid.uuid4())

    def test_snapshot_copies_all_task_fields(self, mock_db):
        template = make_template(num_tasks=1)
        tt = template.tasks[0]
        user_id = uuid.uuid4()

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = template
        mock_db.flush = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()

        added_objects = []
        mock_db.add.side_effect = lambda obj: added_objects.append(obj)

        svc = InstanceService(mock_db)
        svc.import_template(template.id, user_id)

        instance_tasks = [o for o in added_objects if hasattr(o, "source_template_task_id")]
        assert len(instance_tasks) == 1
        it = instance_tasks[0]
        assert it.source_template_task_id == tt.id
        assert it.name == tt.name
        assert it.address == tt.address
        assert it.lat == tt.lat
        assert it.lng == tt.lng
        assert it.task_description == tt.task_description
        assert it.verification_type == tt.verification_type


class TestListInstances:
    def test_returns_user_instances(self, mock_db):
        user_id = uuid.uuid4()
        instances = [make_instance(user_id=user_id), make_instance(user_id=user_id)]

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_unique = MagicMock()
        mock_db.execute.return_value = mock_result
        mock_result.scalars.return_value = mock_scalars
        mock_scalars.unique.return_value = mock_unique
        mock_unique.all.return_value = instances

        svc = InstanceService(mock_db)
        result = svc.list_instances(user_id)
        assert len(result) == 2


class TestGetInstance:
    def test_returns_instance_for_owner(self, mock_db):
        user_id = uuid.uuid4()
        instance = make_instance(user_id=user_id)

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_unique = MagicMock()
        mock_db.execute.return_value = mock_result
        mock_result.scalars.return_value = mock_scalars
        mock_scalars.unique.return_value = mock_unique
        mock_unique.first.return_value = instance

        svc = InstanceService(mock_db)
        result = svc.get_instance(instance.id, user_id)
        assert result is instance

    def test_returns_none_for_non_owner(self, mock_db):
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_unique = MagicMock()
        mock_db.execute.return_value = mock_result
        mock_result.scalars.return_value = mock_scalars
        mock_scalars.unique.return_value = mock_unique
        mock_unique.first.return_value = None

        svc = InstanceService(mock_db)
        result = svc.get_instance(uuid.uuid4(), uuid.uuid4())
        assert result is None


class TestGetProgress:
    def test_zero_tasks(self, mock_db):
        inst = make_instance(num_tasks=0)
        inst.progress = (0, 0)
        inst.is_complete = False

        svc = InstanceService(mock_db)
        p = svc.get_progress(inst)
        assert p["total_tasks"] == 0
        assert p["completed_tasks"] == 0
        assert p["percent"] == 0.0
        assert p["is_complete"] is False

    def test_partial_progress(self, mock_db):
        inst = make_instance(num_tasks=4, completed_tasks=1)
        svc = InstanceService(mock_db)
        p = svc.get_progress(inst)
        assert p["completed_tasks"] == 1
        assert p["total_tasks"] == 4
        assert p["percent"] == 25.0
        assert p["is_complete"] is False

    def test_full_progress(self, mock_db):
        inst = make_instance(num_tasks=3, completed_tasks=3)
        svc = InstanceService(mock_db)
        p = svc.get_progress(inst)
        assert p["completed_tasks"] == 3
        assert p["total_tasks"] == 3
        assert p["percent"] == 100.0
        assert p["is_complete"] is True


class TestPreviewSharedRoute:
    def test_returns_template_for_valid_code(self, mock_db):
        template = make_template(share_code="XYZ999")

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_unique = MagicMock()
        mock_db.execute.return_value = mock_result
        mock_result.scalars.return_value = mock_scalars
        mock_scalars.unique.return_value = mock_unique
        mock_unique.first.return_value = template

        svc = InstanceService(mock_db)
        result = svc.preview_shared_route("XYZ999")
        assert result.share_code == "XYZ999"

    def test_returns_none_for_invalid_code(self, mock_db):
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_unique = MagicMock()
        mock_db.execute.return_value = mock_result
        mock_result.scalars.return_value = mock_scalars
        mock_scalars.unique.return_value = mock_unique
        mock_unique.first.return_value = None

        svc = InstanceService(mock_db)
        result = svc.preview_shared_route("INVALID")
        assert result is None


class TestImportSharedRoute:
    def test_raises_on_bad_share_code(self, mock_db):
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_unique = MagicMock()
        mock_db.execute.return_value = mock_result
        mock_result.scalars.return_value = mock_scalars
        mock_scalars.unique.return_value = mock_unique
        mock_unique.first.return_value = None

        svc = InstanceService(mock_db)
        with pytest.raises(ValueError, match="No route found for share code"):
            svc.import_shared_route("NOPE", uuid.uuid4())


# ── Sprint 2 tests ──────────────────────────────────────────────────


class TestDeleteInstance:
    def _setup_get(self, mock_db, instance):
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_unique = MagicMock()
        mock_db.execute.return_value = mock_result
        mock_result.scalars.return_value = mock_scalars
        mock_scalars.unique.return_value = mock_unique
        mock_unique.first.return_value = instance

    def test_deletes_existing_instance(self, mock_db):
        inst = make_instance()
        self._setup_get(mock_db, inst)
        svc = InstanceService(mock_db)
        assert svc.delete_instance(inst.id, inst.user_id) is True
        mock_db.delete.assert_called_once_with(inst)
        mock_db.commit.assert_called_once()

    def test_returns_false_when_not_found(self, mock_db):
        self._setup_get(mock_db, None)
        svc = InstanceService(mock_db)
        assert svc.delete_instance(uuid.uuid4(), uuid.uuid4()) is False


class TestUpdateStatus:
    def _setup_get(self, mock_db, instance):
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_unique = MagicMock()
        mock_db.execute.return_value = mock_result
        mock_result.scalars.return_value = mock_scalars
        mock_scalars.unique.return_value = mock_unique
        mock_unique.first.return_value = instance

    def test_updates_to_archived(self, mock_db):
        inst = make_instance(status="active")
        self._setup_get(mock_db, inst)
        mock_db.refresh = MagicMock()
        svc = InstanceService(mock_db)
        result = svc.update_status(inst.id, inst.user_id, "archived")
        assert result.status == "archived"

    def test_updates_to_completed_sets_timestamp(self, mock_db):
        inst = make_instance(status="active")
        self._setup_get(mock_db, inst)
        mock_db.refresh = MagicMock()
        svc = InstanceService(mock_db)
        result = svc.update_status(inst.id, inst.user_id, "completed")
        assert result.status == "completed"
        assert result.completed_at is not None

    def test_rejects_invalid_status(self, mock_db):
        svc = InstanceService(mock_db)
        with pytest.raises(ValueError, match="Invalid status"):
            svc.update_status(uuid.uuid4(), uuid.uuid4(), "banana")

    def test_returns_none_when_not_found(self, mock_db):
        self._setup_get(mock_db, None)
        svc = InstanceService(mock_db)
        assert svc.update_status(uuid.uuid4(), uuid.uuid4(), "archived") is None


class TestAutoComplete:
    def test_marks_complete_when_all_tasks_done(self, mock_db):
        inst = make_instance(num_tasks=3, completed_tasks=3)
        inst.status = "active"
        mock_db.refresh = MagicMock()
        svc = InstanceService(mock_db)
        result = svc.check_auto_complete(inst)
        assert result.status == "completed"
        assert result.completed_at is not None

    def test_does_not_change_incomplete_instance(self, mock_db):
        inst = make_instance(num_tasks=3, completed_tasks=1)
        inst.status = "active"
        svc = InstanceService(mock_db)
        result = svc.check_auto_complete(inst)
        assert result.status == "active"

    def test_does_not_re_complete_archived(self, mock_db):
        inst = make_instance(num_tasks=2, completed_tasks=2)
        inst.status = "archived"
        svc = InstanceService(mock_db)
        result = svc.check_auto_complete(inst)
        assert result.status == "archived"


class TestUpdateTask:
    def _setup_get(self, mock_db, instance):
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_unique = MagicMock()
        mock_db.execute.return_value = mock_result
        mock_result.scalars.return_value = mock_scalars
        mock_scalars.unique.return_value = mock_unique
        mock_unique.first.return_value = instance

    def test_updates_notes(self, mock_db):
        inst = make_instance(num_tasks=2)
        task = inst.tasks[0]
        self._setup_get(mock_db, inst)
        mock_db.refresh = MagicMock()
        svc = InstanceService(mock_db)
        result = svc.update_task(inst.id, task.id, inst.user_id, notes="New note")
        assert result.notes == "New note"

    def test_returns_none_for_missing_task(self, mock_db):
        inst = make_instance(num_tasks=1)
        self._setup_get(mock_db, inst)
        svc = InstanceService(mock_db)
        result = svc.update_task(inst.id, uuid.uuid4(), inst.user_id, notes="x")
        assert result is None

    def test_returns_none_for_missing_instance(self, mock_db):
        self._setup_get(mock_db, None)
        svc = InstanceService(mock_db)
        result = svc.update_task(uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), notes="x")
        assert result is None


class TestDeleteTask:
    def _setup_get(self, mock_db, instance):
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_unique = MagicMock()
        mock_db.execute.return_value = mock_result
        mock_result.scalars.return_value = mock_scalars
        mock_scalars.unique.return_value = mock_unique
        mock_unique.first.return_value = instance

    def test_deletes_task(self, mock_db):
        inst = make_instance(num_tasks=2)
        task = inst.tasks[0]
        self._setup_get(mock_db, inst)
        svc = InstanceService(mock_db)
        assert svc.delete_task(inst.id, task.id, inst.user_id) is True
        mock_db.delete.assert_called_once_with(task)

    def test_returns_false_for_missing_task(self, mock_db):
        inst = make_instance(num_tasks=1)
        self._setup_get(mock_db, inst)
        svc = InstanceService(mock_db)
        assert svc.delete_task(inst.id, uuid.uuid4(), inst.user_id) is False


class TestListPublicTemplates:
    def test_returns_public_templates(self, mock_db):
        templates = [make_template(is_public=True), make_template(is_public=True)]
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_unique = MagicMock()
        mock_db.execute.return_value = mock_result
        mock_result.scalars.return_value = mock_scalars
        mock_scalars.unique.return_value = mock_unique
        mock_unique.all.return_value = templates

        svc = InstanceService(mock_db)
        result = svc.list_public_templates()
        assert len(result) == 2


class TestTogglePublic:
    def test_toggles_on(self, mock_db):
        template = make_template(is_public=False)
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = template
        mock_db.refresh = MagicMock()

        svc = InstanceService(mock_db)
        result = svc.toggle_public(template.id, template.author_id, True)
        assert result.is_public is True

    def test_returns_none_for_non_author(self, mock_db):
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        svc = InstanceService(mock_db)
        assert svc.toggle_public(uuid.uuid4(), uuid.uuid4(), True) is None
