"""
TDD RED Phase: Tests for job management API endpoints
These tests will fail until we implement the job endpoints
"""

import pytest


def test_create_job_success(client, test_user, test_plugin, auth_headers):
    """Test successful job creation"""
    response = client.post(
        "/api/v1/jobs",
        headers=auth_headers,
        json={
            "plugin_name": "test-plugin",
            "input_data": {"features": [1.0, 2.0, 3.0]},
        },
    )

    assert response.status_code == 202  # Accepted
    data = response.json()
    assert data["plugin_name"] == "test-plugin"
    assert data["status"] == "queued"
    assert data["input_data"] == {"features": [1.0, 2.0, 3.0]}
    assert data["owner_id"] == test_user.id
    assert "id" in data
    assert "created_at" in data


def test_create_job_requires_auth(client):
    """Test job creation requires authentication"""
    response = client.post(
        "/api/v1/jobs",
        json={
            "plugin_name": "test-plugin",
            "input_data": {},
        },
    )

    assert response.status_code == 401


def test_create_job_plugin_not_found(client, auth_headers):
    """Test job creation with non-existent plugin fails"""
    response = client.post(
        "/api/v1/jobs",
        headers=auth_headers,
        json={
            "plugin_name": "nonexistent-plugin",
            "input_data": {},
        },
    )

    assert response.status_code == 404
    assert "plugin not found" in response.json()["detail"].lower()


def test_create_job_invalid_plugin_name(client, auth_headers):
    """Test job creation with invalid plugin name fails"""
    response = client.post(
        "/api/v1/jobs",
        headers=auth_headers,
        json={
            "plugin_name": "Invalid Name!",  # Contains spaces and special chars
            "input_data": {},
        },
    )

    assert response.status_code == 422  # Validation error


def test_list_jobs(client, test_user, test_plugin, auth_headers, db_session):
    """Test listing jobs for current user"""
    from app.models.job import Job, JobStatus

    # Create some jobs
    job1 = Job(
        plugin_name="test-plugin", status=JobStatus.QUEUED, owner_id=test_user.id
    )
    job2 = Job(
        plugin_name="test-plugin", status=JobStatus.COMPLETED, owner_id=test_user.id
    )
    db_session.add_all([job1, job2])
    db_session.commit()

    response = client.get("/api/v1/jobs", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert data["total"] >= 2
    assert len(data["items"]) >= 2


def test_list_jobs_with_status_filter(
    client, test_user, test_plugin, auth_headers, db_session
):
    """Test listing jobs filtered by status"""
    from app.models.job import Job, JobStatus

    # Create jobs with different statuses
    job1 = Job(
        plugin_name="test-plugin", status=JobStatus.QUEUED, owner_id=test_user.id
    )
    job2 = Job(
        plugin_name="test-plugin", status=JobStatus.COMPLETED, owner_id=test_user.id
    )
    db_session.add_all([job1, job2])
    db_session.commit()

    response = client.get("/api/v1/jobs?status=completed", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    # All returned jobs should have completed status
    for job in data["items"]:
        assert job["status"] == "completed"


def test_list_jobs_pagination(client, test_user, test_plugin, auth_headers, db_session):
    """Test job list pagination"""
    from app.models.job import Job, JobStatus

    # Create multiple jobs
    for i in range(5):
        job = Job(
            plugin_name="test-plugin", status=JobStatus.QUEUED, owner_id=test_user.id
        )
        db_session.add(job)
    db_session.commit()

    # Test with limit
    response = client.get("/api/v1/jobs?limit=2", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) <= 2


def test_get_job_by_id(client, test_user, test_plugin, auth_headers, db_session):
    """Test getting specific job by ID"""
    from app.models.job import Job, JobStatus

    job = Job(
        plugin_name="test-plugin",
        status=JobStatus.COMPLETED,
        input_data={"test": "data"},
        result={"prediction": "class_A"},
        owner_id=test_user.id,
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    response = client.get(f"/api/v1/jobs/{job.id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == job.id
    assert data["status"] == "completed"
    assert data["result"] == {"prediction": "class_A"}


def test_get_job_not_found(client, auth_headers):
    """Test getting non-existent job returns 404"""
    response = client.get("/api/v1/jobs/99999", headers=auth_headers)

    assert response.status_code == 404


def test_get_job_not_owner(client, test_plugin, auth_headers, db_session):
    """Test user cannot access another user's job"""
    from app.models.user import User
    from app.models.job import Job, JobStatus
    from app.core.security import get_password_hash

    # Create another user
    other_user = User(
        email="other@example.com",
        hashed_password=get_password_hash("password"),
    )
    db_session.add(other_user)
    db_session.commit()
    db_session.refresh(other_user)

    # Create job for other user
    job = Job(
        plugin_name="test-plugin", status=JobStatus.QUEUED, owner_id=other_user.id
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    # Try to access with different user's token
    response = client.get(f"/api/v1/jobs/{job.id}", headers=auth_headers)

    assert response.status_code == 403  # Forbidden


@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    from app.models.user import User
    from app.core.security import get_password_hash

    user = User(
        email="testuser@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test User",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_plugin(db_session):
    """Create a test plugin"""
    from app.models.plugin import Plugin

    plugin = Plugin(
        name="test-plugin",
        version="1.0.0",
        description="Test plugin",
        docker_image_url="registry.example.com/test:1.0.0",
    )
    db_session.add(plugin)
    db_session.commit()
    db_session.refresh(plugin)
    return plugin


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers with valid token"""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "testuser@example.com", "password": "password123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
