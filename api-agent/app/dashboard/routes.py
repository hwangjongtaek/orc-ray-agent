"""
Dashboard routes for web UI
"""

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.db import get_db
from app.core.security import get_current_user, verify_password, create_access_token
from app.models.user import User as UserModel
from app.models.job import Job as JobModel, JobStatus
from app.models.plugin import Plugin as PluginModel

router = APIRouter()
templates = Jinja2Templates(directory="app/dashboard/templates")


async def get_current_user_optional(request: Request, db: Session = Depends(get_db)):
    """Get current user from cookie, return None if not authenticated"""
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        from app.core.security import decode_access_token

        payload = decode_access_token(token)
        if payload is None:
            return None
        user_id = payload.get("sub")
        if user_id is None:
            return None
        user = db.query(UserModel).filter(UserModel.id == int(user_id)).first()
        return user
    except Exception:
        return None


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Render login page"""
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(request: Request, response: Response, db: Session = Depends(get_db)):
    """Handle login form submission"""
    form = await request.form()
    email = form.get("username")
    password = form.get("password")

    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return Response(
            content='{"detail":"Incorrect email or password"}',
            status_code=status.HTTP_401_UNAUTHORIZED,
            media_type="application/json",
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response


@router.get("/logout")
async def logout():
    """Handle logout"""
    response = RedirectResponse(
        url="/dashboard/login", status_code=status.HTTP_303_SEE_OTHER
    )
    response.delete_cookie(key="access_token")
    return response


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def dashboard_home(
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user_optional),
):
    """Render dashboard overview"""
    if not current_user:
        return RedirectResponse(url="/dashboard/login")

    return templates.TemplateResponse(
        "overview.html", {"request": request, "current_user": current_user}
    )


@router.get("/jobs", response_class=HTMLResponse)
async def jobs_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user_optional),
):
    """Render jobs list page"""
    if not current_user:
        return RedirectResponse(url="/dashboard/login")

    return templates.TemplateResponse(
        "jobs.html", {"request": request, "current_user": current_user}
    )


@router.get("/users", response_class=HTMLResponse)
async def users_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user_optional),
):
    """Render users list page"""
    if not current_user:
        return RedirectResponse(url="/dashboard/login")

    return templates.TemplateResponse(
        "users.html", {"request": request, "current_user": current_user}
    )


@router.get("/plugins", response_class=HTMLResponse)
async def plugins_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user_optional),
):
    """Render plugins list page"""
    if not current_user:
        return RedirectResponse(url="/dashboard/login")

    return templates.TemplateResponse(
        "plugins.html", {"request": request, "current_user": current_user}
    )


# API endpoint for dashboard stats
@router.get("/api/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)
):
    """Get dashboard statistics"""
    total_jobs = db.query(JobModel).count()
    queued_jobs = db.query(JobModel).filter(JobModel.status == JobStatus.QUEUED).count()
    processing_jobs = (
        db.query(JobModel).filter(JobModel.status == JobStatus.PROCESSING).count()
    )
    active_users = db.query(UserModel).filter(UserModel.is_active == True).count()

    recent_jobs = (
        db.query(JobModel).order_by(JobModel.created_at.desc()).limit(10).all()
    )

    return {
        "stats": {
            "total_jobs": total_jobs,
            "queued_jobs": queued_jobs,
            "processing_jobs": processing_jobs,
            "active_users": active_users,
        },
        "recent_jobs": [
            {
                "id": job.id,
                "plugin_name": job.plugin_name,
                "status": job.status.value,
                "created_at": job.created_at.isoformat(),
            }
            for job in recent_jobs
        ],
    }
