"""
TDD GREEN Phase: Job management API endpoints
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.dependencies import get_current_user
from app.models.job import Job as JobModel, JobStatus
from app.models.plugin import Plugin as PluginModel
from app.models.user import User as UserModel
from app.schemas.job import Job, JobCreate, JobList
from app.services.mq_service import get_mq_service

router = APIRouter()


@router.post("", response_model=Job, status_code=status.HTTP_202_ACCEPTED)
async def create_job(
    job_in: JobCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Create new job.

    Submit a new job for plugin execution. The job will be queued for processing.
    """
    # Verify plugin exists
    plugin = (
        db.query(PluginModel).filter(PluginModel.name == job_in.plugin_name).first()
    )
    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plugin not found",
        )

    # Create job
    db_job = JobModel(
        plugin_name=job_in.plugin_name,
        input_data=job_in.input_data,
        status=JobStatus.QUEUED,
        owner_id=current_user.id,
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)

    # Publish job to RabbitMQ queue
    try:
        mq = get_mq_service()
        mq.publish_job(
            {
                "job_id": db_job.id,
                "plugin_name": db_job.plugin_name,
                "docker_image_url": plugin.docker_image_url,
                "input_data": db_job.input_data,
                "owner_id": db_job.owner_id,
                "created_at": db_job.created_at.isoformat(),
            }
        )
    except Exception as e:
        # Log error but don't fail the request
        # Job is still created and can be retried
        import logging

        logging.error(f"Failed to publish job to queue: {e}")

    return db_job


@router.get("", response_model=JobList)
async def list_jobs(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    plugin_name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    List jobs for current user.

    Retrieve paginated list of jobs submitted by the current user.
    Can be filtered by status and plugin_name.
    """
    # Base query for current user's jobs
    query = db.query(JobModel).filter(JobModel.owner_id == current_user.id)

    # Apply filters
    if status:
        try:
            status_enum = JobStatus(status)
            query = query.filter(JobModel.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}",
            )

    if plugin_name:
        query = query.filter(JobModel.plugin_name == plugin_name)

    # Get total count
    total = query.count()

    # Get paginated jobs
    jobs = query.order_by(JobModel.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "items": jobs,
    }


@router.get("/{job_id}", response_model=Job)
async def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Get job by ID.

    Retrieve detailed information about a specific job.
    Users can only access their own jobs.
    """
    job = db.query(JobModel).filter(JobModel.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    # Verify job belongs to current user
    if job.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this job",
        )

    return job
