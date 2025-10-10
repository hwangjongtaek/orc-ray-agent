"""
TDD RED Phase: Tests for Plugin model
These tests will fail until we implement the Plugin model
"""

import pytest
from datetime import datetime


def test_plugin_model_creation(db_session):
    """Test that a Plugin can be created with all required fields"""
    from app.models.plugin import Plugin

    plugin = Plugin(
        name="test-classifier",
        version="1.0.0",
        description="Test ML classifier",
        docker_image_url="registry.example.com/test-classifier:1.0.0",
        input_schema={"type": "object", "properties": {"features": {"type": "array"}}},
        output_schema={
            "type": "object",
            "properties": {"prediction": {"type": "string"}},
        },
    )

    db_session.add(plugin)
    db_session.commit()
    db_session.refresh(plugin)

    assert plugin.id is not None
    assert plugin.name == "test-classifier"
    assert plugin.version == "1.0.0"
    assert plugin.description == "Test ML classifier"
    assert plugin.docker_image_url == "registry.example.com/test-classifier:1.0.0"
    assert plugin.input_schema == {
        "type": "object",
        "properties": {"features": {"type": "array"}},
    }
    assert plugin.output_schema == {
        "type": "object",
        "properties": {"prediction": {"type": "string"}},
    }
    assert isinstance(plugin.created_at, datetime)


def test_plugin_name_must_be_unique(db_session):
    """Test that plugin name must be unique"""
    from app.models.plugin import Plugin
    from sqlalchemy.exc import IntegrityError

    plugin1 = Plugin(
        name="unique-plugin",
        version="1.0.0",
        docker_image_url="registry.example.com/unique:1.0.0",
    )
    db_session.add(plugin1)
    db_session.commit()

    plugin2 = Plugin(
        name="unique-plugin",
        version="2.0.0",
        docker_image_url="registry.example.com/unique:2.0.0",
    )
    db_session.add(plugin2)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_plugin_with_minimal_fields(db_session):
    """Test Plugin can be created with minimal required fields"""
    from app.models.plugin import Plugin

    plugin = Plugin(
        name="minimal-plugin",
        version="1.0.0",
        docker_image_url="registry.example.com/minimal:1.0.0",
    )

    db_session.add(plugin)
    db_session.commit()
    db_session.refresh(plugin)

    assert plugin.id is not None
    assert plugin.name == "minimal-plugin"
    assert plugin.description is None
    assert plugin.input_schema is None
    assert plugin.output_schema is None
