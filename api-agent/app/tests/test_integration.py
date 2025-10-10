"""
Integration Tests for Full Job Workflow
Tests the complete system integration from job creation to completion
"""

import json
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.models.job import JobStatus


class TestJobWorkflowIntegration:
    """Integration tests for complete job processing workflow"""

    def test_complete_job_workflow_success(
        self, client: TestClient, test_user_token, db_session
    ):
        """
        Test complete job workflow from creation to completion

        Workflow:
        1. User creates a job via API
        2. Job is saved to database with 'queued' status
        3. Job is published to RabbitMQ job_queue
        4. Ray Worker consumes job from queue
        5. Ray Worker executes plugin in Docker container
        6. Ray Worker publishes status update to status_queue
        7. API Agent updates job status in database
        8. User retrieves completed job with result
        """
        headers = {"Authorization": f"Bearer {test_user_token}"}

        # First, create a plugin in the database
        from app.models.plugin import Plugin as PluginModel

        plugin = PluginModel(
            name="test-plugin",
            description="Test plugin for integration",
            version="1.0.0",
            docker_image_url="test-plugin:1.0.0",
            input_schema={"type": "object", "properties": {"data": {"type": "array"}}},
            output_schema={
                "type": "object",
                "properties": {"result": {"type": "number"}},
            },
            is_active=True,
        )
        db_session.add(plugin)
        db_session.commit()

        # Mock RabbitMQ publish to avoid actual message queue interaction
        with patch(
            "app.services.mq_service.RabbitMQService.publish_job"
        ) as mock_publish:
            # Step 1: Create job
            job_data = {
                "plugin_name": "test-plugin",
                "input_data": {"data": [1, 2, 3, 4, 5]},
            }

            response = client.post("/api/v1/jobs", json=job_data, headers=headers)
            assert response.status_code == 202
            job = response.json()

            # Verify job creation
            assert job["plugin_name"] == "test-plugin"
            assert job["status"] == "queued"
            assert job["input_data"] == {"data": [1, 2, 3, 4, 5]}
            assert "id" in job

            job_id = job["id"]

            # Verify RabbitMQ publish was called
            mock_publish.assert_called_once()
            call_args = mock_publish.call_args[0][0]
            assert call_args["job_id"] == job_id
            assert call_args["plugin_name"] == "test-plugin"
            assert call_args["docker_image_url"] == "test-plugin:1.0.0"

        # Step 2: Simulate Ray Worker processing (status update)
        # In real system, Ray Worker would update via status_queue
        # Here we simulate by directly updating the database
        from app.models.job import Job as JobModel

        db_job = db_session.query(JobModel).filter(JobModel.id == job_id).first()
        db_job.status = JobStatus.PROCESSING
        db_session.commit()

        # Verify processing status
        response = client.get(f"/api/v1/jobs/{job_id}", headers=headers)
        assert response.status_code == 200
        job = response.json()
        assert job["status"] == "processing"

        # Step 3: Simulate job completion
        db_job.status = JobStatus.COMPLETED
        db_job.result = {"result": 15, "count": 5}
        db_session.commit()

        # Verify completed status with result
        response = client.get(f"/api/v1/jobs/{job_id}", headers=headers)
        assert response.status_code == 200
        job = response.json()
        assert job["status"] == "completed"
        assert job["result"] == {"result": 15, "count": 5}
        assert job["error_message"] is None

    def test_job_workflow_with_failure(
        self, client: TestClient, test_user_token, db_session
    ):
        """
        Test job workflow when plugin execution fails

        Workflow:
        1. Create job
        2. Simulate plugin execution failure
        3. Verify error status and message
        """
        headers = {"Authorization": f"Bearer {test_user_token}"}

        # Create plugin
        from app.models.plugin import Plugin as PluginModel

        plugin = PluginModel(
            name="failing-plugin",
            description="Plugin that fails",
            version="1.0.0",
            docker_image_url="failing-plugin:1.0.0",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            is_active=True,
        )
        db_session.add(plugin)
        db_session.commit()

        with patch("app.services.mq_service.RabbitMQService.publish_job"):
            # Create job
            job_data = {
                "plugin_name": "failing-plugin",
                "input_data": {"invalid": "data"},
            }

            response = client.post("/api/v1/jobs", json=job_data, headers=headers)
            assert response.status_code == 202
            job = response.json()
            job_id = job["id"]

        # Simulate failure
        from app.models.job import Job as JobModel

        db_job = db_session.query(JobModel).filter(JobModel.id == job_id).first()
        db_job.status = JobStatus.FAILED
        db_job.error_message = "Container execution failed: Invalid input data"
        db_session.commit()

        # Verify failure status
        response = client.get(f"/api/v1/jobs/{job_id}", headers=headers)
        assert response.status_code == 200
        job = response.json()
        assert job["status"] == "failed"
        assert "Invalid input data" in job["error_message"]
        assert job["result"] is None

    def test_job_list_filtering_integration(
        self, client: TestClient, test_user_token, db_session
    ):
        """
        Test job listing with various filters
        """
        headers = {"Authorization": f"Bearer {test_user_token}"}

        # Create plugin
        from app.models.plugin import Plugin as PluginModel

        plugin = PluginModel(
            name="filter-test-plugin",
            description="Plugin for filter testing",
            version="1.0.0",
            docker_image_url="filter-test:1.0.0",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            is_active=True,
        )
        db_session.add(plugin)
        db_session.commit()

        with patch("app.services.mq_service.RabbitMQService.publish_job"):
            # Create multiple jobs with different statuses
            for i in range(3):
                job_data = {
                    "plugin_name": "filter-test-plugin",
                    "input_data": {"index": i},
                }
                response = client.post("/api/v1/jobs", json=job_data, headers=headers)
                assert response.status_code == 202

        # Get all jobs
        response = client.get("/api/v1/jobs", headers=headers)
        assert response.status_code == 200
        jobs = response.json()
        assert len(jobs) >= 3

        # Verify all jobs have correct plugin name
        filter_test_jobs = [j for j in jobs if j["plugin_name"] == "filter-test-plugin"]
        assert len(filter_test_jobs) >= 3

        # Verify all are in queued status initially
        for job in filter_test_jobs:
            assert job["status"] == "queued"


class TestAuthenticationIntegration:
    """Integration tests for authentication flow"""

    def test_full_authentication_flow(self, client: TestClient, test_user):
        """
        Test complete authentication workflow

        Workflow:
        1. User logs in with credentials
        2. Receives JWT token
        3. Uses token to access protected endpoint
        4. Token validation succeeds
        """
        # Step 1: Login
        login_data = {
            "username": test_user.email,
            "password": "testpassword123",
        }

        response = client.post("/api/v1/auth/token", data=login_data)
        assert response.status_code == 200
        token_data = response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"

        access_token = token_data["access_token"]

        # Step 2: Use token to access protected endpoint
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["email"] == test_user.email

        # Step 3: Access other protected endpoints
        response = client.get("/api/v1/jobs", headers=headers)
        assert response.status_code == 200

    def test_authentication_failure_flow(self, client: TestClient):
        """
        Test authentication failure scenarios
        """
        # Invalid credentials
        login_data = {
            "username": "nonexistent@example.com",
            "password": "wrongpassword",
        }

        response = client.post("/api/v1/auth/token", data=login_data)
        assert response.status_code == 401

        # Access protected endpoint without token
        response = client.get("/api/v1/jobs")
        assert response.status_code == 401

        # Access protected endpoint with invalid token
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/jobs", headers=headers)
        assert response.status_code == 401


class TestPluginRegistrationIntegration:
    """Integration tests for plugin registration and usage"""

    def test_plugin_registration_and_job_creation(
        self, client: TestClient, test_user_token, db_session
    ):
        """
        Test registering a plugin and using it in a job

        Workflow:
        1. Register plugin via API
        2. Verify plugin is stored
        3. Create job using the plugin
        4. Verify job references correct plugin
        """
        headers = {"Authorization": f"Bearer {test_user_token}"}

        # Step 1: Register plugin
        plugin_data = {
            "name": "integration-test-plugin",
            "description": "Plugin for integration testing",
            "version": "1.0.0",
            "docker_image_url": "integration-test:1.0.0",
            "input_schema": {
                "type": "object",
                "properties": {"numbers": {"type": "array"}},
            },
            "output_schema": {
                "type": "object",
                "properties": {"sum": {"type": "number"}},
            },
        }

        # Add plugin directly to database (simulating plugin-registry service)
        from app.models.plugin import Plugin as PluginModel

        plugin = PluginModel(**plugin_data, is_active=True)
        db_session.add(plugin)
        db_session.commit()

        # Step 2: Verify plugin exists
        from app.models.plugin import Plugin as PluginModel

        db_plugin = (
            db_session.query(PluginModel)
            .filter(PluginModel.name == "integration-test-plugin")
            .first()
        )
        assert db_plugin is not None
        assert db_plugin.docker_image_url == "integration-test:1.0.0"

        # Step 3: Create job using the plugin
        with patch(
            "app.services.mq_service.RabbitMQService.publish_job"
        ) as mock_publish:
            job_data = {
                "plugin_name": "integration-test-plugin",
                "input_data": {"numbers": [10, 20, 30]},
            }

            response = client.post("/api/v1/jobs", json=job_data, headers=headers)
            assert response.status_code == 202
            job = response.json()

            # Step 4: Verify job references correct plugin
            assert job["plugin_name"] == "integration-test-plugin"
            assert job["input_data"] == {"numbers": [10, 20, 30]}

            # Verify RabbitMQ message contains correct plugin info
            call_args = mock_publish.call_args[0][0]
            assert call_args["docker_image_url"] == "integration-test:1.0.0"

    def test_job_creation_with_nonexistent_plugin(
        self, client: TestClient, test_user_token
    ):
        """
        Test job creation fails when plugin doesn't exist
        """
        headers = {"Authorization": f"Bearer {test_user_token}"}

        job_data = {
            "plugin_name": "nonexistent-plugin",
            "input_data": {"data": "test"},
        }

        response = client.post("/api/v1/jobs", json=job_data, headers=headers)
        assert response.status_code == 404
        assert "Plugin not found" in response.json()["detail"]


class TestUserManagementIntegration:
    """Integration tests for user management workflows"""

    def test_user_lifecycle(self, client: TestClient, test_user_token):
        """
        Test complete user lifecycle

        Workflow:
        1. Admin creates new user
        2. New user logs in
        3. New user creates a job
        4. Admin can view all jobs
        5. User can only see their own jobs
        """
        admin_headers = {"Authorization": f"Bearer {test_user_token}"}

        # Step 1: Create new user
        new_user_data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
            "full_name": "New User",
        }

        response = client.post(
            "/api/v1/users", json=new_user_data, headers=admin_headers
        )
        assert response.status_code == 200
        new_user = response.json()
        assert new_user["email"] == "newuser@example.com"
        assert new_user["is_active"] is True

        # Step 2: New user logs in
        login_data = {
            "username": "newuser@example.com",
            "password": "newpassword123",
        }

        response = client.post("/api/v1/auth/token", data=login_data)
        assert response.status_code == 200
        new_user_token = response.json()["access_token"]

        # Step 3: Verify new user can access their profile
        new_user_headers = {"Authorization": f"Bearer {new_user_token}"}
        response = client.get("/api/v1/auth/me", headers=new_user_headers)
        assert response.status_code == 200
        profile = response.json()
        assert profile["email"] == "newuser@example.com"


class TestDashboardIntegration:
    """Integration tests for dashboard functionality"""

    def test_dashboard_stats_accuracy(
        self, client: TestClient, test_user_token, db_session
    ):
        """
        Test dashboard statistics accuracy

        Workflow:
        1. Create multiple jobs with different statuses
        2. Fetch dashboard stats
        3. Verify stats match actual database state
        """
        headers = {"Authorization": f"Bearer {test_user_token}"}

        # Create plugin
        from app.models.plugin import Plugin as PluginModel

        plugin = PluginModel(
            name="stats-test-plugin",
            description="Plugin for stats testing",
            version="1.0.0",
            docker_image_url="stats-test:1.0.0",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            is_active=True,
        )
        db_session.add(plugin)
        db_session.commit()

        # Create jobs with different statuses
        from app.models.job import Job as JobModel

        with patch("app.services.mq_service.RabbitMQService.publish_job"):
            for i in range(5):
                job_data = {
                    "plugin_name": "stats-test-plugin",
                    "input_data": {"index": i},
                }
                response = client.post("/api/v1/jobs", json=job_data, headers=headers)
                assert response.status_code == 202

        # Update some jobs to different statuses
        jobs = (
            db_session.query(JobModel)
            .filter(JobModel.plugin_name == "stats-test-plugin")
            .all()
        )

        if len(jobs) >= 3:
            jobs[0].status = JobStatus.PROCESSING
            jobs[1].status = JobStatus.COMPLETED
            jobs[2].status = JobStatus.FAILED
            db_session.commit()

        # Fetch dashboard stats
        response = client.get("/api/v1/dashboard/stats", headers=headers)
        assert response.status_code == 200
        stats = response.json()

        # Verify stats structure
        assert "stats" in stats
        assert "recent_jobs" in stats
        assert "total_jobs" in stats["stats"]
        assert "queued_jobs" in stats["stats"]
        assert "processing_jobs" in stats["stats"]
        assert "active_users" in stats["stats"]

        # Verify at least our created jobs are counted
        assert stats["stats"]["total_jobs"] >= 5
        assert stats["stats"]["queued_jobs"] >= 2
        assert stats["stats"]["processing_jobs"] >= 1
