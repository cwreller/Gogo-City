"""API tests for /api/templates public discovery and toggle endpoints."""
import uuid
from unittest.mock import MagicMock, patch

import pytest

from tests.conftest import make_template


class TestListPublicTemplates:
    @patch("app.api.routes.templates.InstanceService")
    def test_list_public(self, MockSvc, client, mock_db):
        templates = [make_template(is_public=True), make_template(is_public=True)]
        MockSvc.return_value.list_public_templates.return_value = templates

        resp = client.get("/api/templates/public")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert all(t["is_public"] is True for t in data)

    @patch("app.api.routes.templates.InstanceService")
    def test_list_public_empty(self, MockSvc, client, mock_db):
        MockSvc.return_value.list_public_templates.return_value = []
        resp = client.get("/api/templates/public")
        assert resp.status_code == 200
        assert resp.json() == []

    @patch("app.api.routes.templates.InstanceService")
    def test_list_public_with_city_filter(self, MockSvc, client, mock_db):
        city_id = uuid.uuid4()
        templates = [make_template(is_public=True, city_id=city_id)]
        MockSvc.return_value.list_public_templates.return_value = templates

        resp = client.get(f"/api/templates/public?city_id={city_id}")
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        MockSvc.return_value.list_public_templates.assert_called_once_with(
            city_id=city_id, vibe_tags=None
        )

    @patch("app.api.routes.templates.InstanceService")
    def test_list_public_with_vibe_tags(self, MockSvc, client, mock_db):
        templates = [make_template(is_public=True)]
        MockSvc.return_value.list_public_templates.return_value = templates

        resp = client.get("/api/templates/public?vibe_tags=foodie&vibe_tags=cultural")
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        MockSvc.return_value.list_public_templates.assert_called_once_with(
            city_id=None, vibe_tags=["foodie", "cultural"]
        )


class TestTogglePublic:
    @patch("app.api.routes.templates.InstanceService")
    def test_toggle_on(self, MockSvc, client, mock_db):
        user_id = uuid.uuid4()
        template = make_template(is_public=True, author_id=user_id)
        MockSvc.return_value.toggle_public.return_value = template

        resp = client.patch(
            f"/api/templates/{template.id}?user_id={user_id}",
            json={"is_public": True},
        )
        assert resp.status_code == 200
        assert resp.json()["is_public"] is True

    @patch("app.api.routes.templates.InstanceService")
    def test_toggle_off(self, MockSvc, client, mock_db):
        user_id = uuid.uuid4()
        template = make_template(is_public=False, author_id=user_id)
        MockSvc.return_value.toggle_public.return_value = template

        resp = client.patch(
            f"/api/templates/{template.id}?user_id={user_id}",
            json={"is_public": False},
        )
        assert resp.status_code == 200
        assert resp.json()["is_public"] is False

    @patch("app.api.routes.templates.InstanceService")
    def test_toggle_not_found_or_not_author(self, MockSvc, client, mock_db):
        MockSvc.return_value.toggle_public.return_value = None
        resp = client.patch(
            f"/api/templates/{uuid.uuid4()}?user_id={uuid.uuid4()}",
            json={"is_public": True},
        )
        assert resp.status_code == 404
        assert "not authorized" in resp.json()["detail"]
