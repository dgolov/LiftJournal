from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.template import TemplateRepository
from tests.conftest import scalar_result, scalars_result


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.add = MagicMock()
    db.delete = AsyncMock()
    return db


def _make_template(id="tpl-1", user_id=1):
    t = MagicMock()
    t.id = id
    t.user_id = user_id
    t.title = "Push day"
    t.type = "Силовая"
    t.created_at = datetime(2026, 1, 1)
    t.exercises = []
    return t


def _make_exercise_in(exercise_id="ex-1", name="Bench Press", sets=None):
    ex = MagicMock()
    ex.exerciseId = exercise_id
    ex.exerciseName = name
    ex.sets = sets or []
    return ex


class TestGetAllByUser:
    async def test_returns_list(self, mock_db):
        templates = [_make_template("tpl-1"), _make_template("tpl-2")]
        mock_db.execute.return_value = scalars_result(templates)

        result = await TemplateRepository(mock_db).get_all_by_user(user_id=1)

        assert result == templates

    async def test_empty(self, mock_db):
        mock_db.execute.return_value = scalars_result([])

        result = await TemplateRepository(mock_db).get_all_by_user(user_id=1)

        assert result == []


class TestGetById:
    async def test_found(self, mock_db):
        template = _make_template()
        mock_db.execute.return_value = scalar_result(template)

        result = await TemplateRepository(mock_db).get_by_id("tpl-1")

        assert result == template

    async def test_not_found(self, mock_db):
        mock_db.execute.return_value = scalar_result(None)

        result = await TemplateRepository(mock_db).get_by_id("missing")

        assert result is None


class TestCreate:
    async def test_adds_and_commits(self, mock_db):
        created = _make_template()
        # get_by_id is called after insert: first execute for insert, second for get_by_id
        mock_db.execute.return_value = scalar_result(created)

        repo = TemplateRepository(mock_db)
        await repo.create(
            user_id=1,
            title="Push day",
            type="Силовая",
            exercises_data=[],
        )

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()


class TestUpdate:
    async def test_updates_fields(self, mock_db):
        template = _make_template()
        updated = _make_template()
        updated.title = "New Title"
        mock_db.execute.return_value = scalar_result(updated)

        await TemplateRepository(mock_db).update(template, title="New Title")

        assert template.title == "New Title"
        mock_db.commit.assert_called_once()

    async def test_skips_none_fields(self, mock_db):
        template = _make_template()
        original_title = template.title
        mock_db.execute.return_value = scalar_result(template)

        await TemplateRepository(mock_db).update(template, title=None, type=None)

        assert template.title == original_title


class TestDelete:
    async def test_deletes_and_commits(self, mock_db):
        template = _make_template()

        await TemplateRepository(mock_db).delete(template)

        mock_db.delete.assert_called_once_with(template)
        mock_db.commit.assert_called_once()


class TestBuildExercises:
    def test_builds_exercise_with_sets(self):
        repo = TemplateRepository(MagicMock())
        s = MagicMock()
        s.weight = 100.0
        s.reps = 5
        ex_in = _make_exercise_in(sets=[s])

        result = repo._build_exercises([ex_in])

        assert len(result) == 1
        assert result[0].exercise_id == "ex-1"
        assert result[0].exercise_name == "Bench Press"
        assert result[0].order == 0
        assert len(result[0].sets) == 1
        assert result[0].sets[0].weight == 100.0
        assert result[0].sets[0].reps == 5

    def test_empty_exercises(self):
        repo = TemplateRepository(MagicMock())
        result = repo._build_exercises([])
        assert result == []
