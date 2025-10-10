"""
TDD RED Phase: Tests for Job model
These tests will fail until we implement the Job model
"""

import pytest
from datetime import datetime


def test_job_model_creation(db_session):
    """Test that a Job can be created with required fields"""
    from app.models.user import User
    from app.models.job import Job, JobStatus

    # Create a user first
    user = User(email="jobowner@example.com", hashed_password="pass")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Create a job
    job = Job(
        plugin_name="test-plugin",
        status=JobStatus.QUEUED,
        input_data={"features": [1.0, 2.0]},
        owner_id=user.id,
    )

    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    # Assertions
    assert job.id is not None
    assert job.plugin_name == "test-plugin"
    assert job.status == JobStatus.QUEUED
    assert job.input_data == {"features": [1.0, 2.0]}
    assert job.result is None
    assert job.error_message is None
    assert job.owner_id == user.id
    assert isinstance(job.created_at, datetime)


def test_job_status_enum_values(db_session):
    """Test JobStatus enum has all required values"""
    from app.models.job import JobStatus

    assert JobStatus.QUEUED == "queued"
    assert JobStatus.PROCESSING == "processing"
    assert JobStatus.COMPLETED == "completed"
    assert JobStatus.FAILED == "failed"


def test_job_default_status_is_queued(db_session):
    """Test that status defaults to QUEUED"""
    from app.models.user import User
    from app.models.job import Job, JobStatus

    user = User(email="user@example.com", hashed_password="pass")
    db_session.add(user)
    db_session.commit()

    job = Job(plugin_name="plugin", owner_id=user.id)
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    assert job.status == JobStatus.QUEUED


def test_job_relationship_with_user(db_session):
    """Test Job has relationship with User"""
    from app.models.user import User
    from app.models.job import Job

    user = User(email="user@example.com", hashed_password="pass")
    db_session.add(user)
    db_session.commit()

    job = Job(plugin_name="plugin", owner_id=user.id)
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    # Test relationship
    assert job.owner is not None
    assert job.owner.email == "user@example.com"
    assert user.jobs[0].id == job.id


def test_job_with_result_and_timestamps(db_session):
    """Test Job can store result and timestamps"""
    from app.models.user import User
    from app.models.job import Job, JobStatus

    user = User(email="user@example.com", hashed_password="pass")
    db_session.add(user)
    db_session.commit()

    job = Job(
        plugin_name="plugin",
        owner_id=user.id,
        status=JobStatus.COMPLETED,
        result={"prediction": "class_A", "confidence": 0.95},
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    assert job.result == {"prediction": "class_A", "confidence": 0.95}
    assert isinstance(job.started_at, datetime)
    assert isinstance(job.completed_at, datetime)


def test_job_with_error_message(db_session):
    """Test Job can store error message when failed"""
    from app.models.user import User
    from app.models.job import Job, JobStatus

    user = User(email="user@example.com", hashed_password="pass")
    db_session.add(user)
    db_session.commit()

    job = Job(
        plugin_name="plugin",
        owner_id=user.id,
        status=JobStatus.FAILED,
        error_message="Plugin execution failed",
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    assert job.error_message == "Plugin execution failed"
    assert job.status == JobStatus.FAILED
