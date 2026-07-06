"""Application detail and manual status management endpoints."""

import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel

from backend.db.session import get_session
from backend.db.models import Application, ApplicationArtifact, ApplicationEvent, Job, User
from backend.api.auth import get_current_user
from backend.services.application_tracking import (
    ApplicationEventType,
    ApplicationStatus,
    update_application_status,
)
from backend.core.logger import get_logger

router = APIRouter()
logger = get_logger("applications_api")

ALLOWED_MANUAL_STATUSES = {
    ApplicationStatus.PENDING,
    ApplicationStatus.READY,
    ApplicationStatus.APPLIED,
    ApplicationStatus.INTERVIEW,
    ApplicationStatus.OFFER,
    ApplicationStatus.REJECTED,
    ApplicationStatus.SKIPPED,
    ApplicationStatus.NEEDS_REVIEW,
}


class StatusUpdateRequest(BaseModel):
    status: str
    note: str | None = None


def _parse_json_list(raw: str | None) -> list[str]:
    """Safely parse a JSON-encoded list string, returning [] on failure."""
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, list) else []
    except (json.JSONDecodeError, TypeError):
        return []


def _parse_json_dict(raw: str | None) -> dict:
    """Safely parse a JSON-encoded dict string, returning {} on failure."""
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else {}
    except (json.JSONDecodeError, TypeError):
        return {}


def _serialize_artifact(artifact: ApplicationArtifact | None) -> dict | None:
    if artifact is None:
        return None
    return {
        "tailored_resume_text": artifact.tailored_resume_text,
        "cover_letter_text": artifact.cover_letter_text,
        "resume_pdf_path": artifact.resume_pdf_path,
        "match_explanation": artifact.match_explanation,
        "matched_skills": _parse_json_list(artifact.matched_skills_json),
        "missing_skills": _parse_json_list(artifact.missing_skills_json),
        "weak_skills": _parse_json_list(artifact.weak_skills_json),
        "change_classifications": _parse_json_list(artifact.change_classifications_json),
        "resume_diff": _parse_json_list(artifact.resume_diff_json),
        "authenticity_flags": _parse_json_list(artifact.authenticity_flags_json),
        "authenticity_requires_review": artifact.authenticity_requires_review,
        "created_at": artifact.created_at.isoformat() if artifact.created_at else None,
        "updated_at": artifact.updated_at.isoformat() if artifact.updated_at else None,
    }


def _serialize_event(event: ApplicationEvent) -> dict:
    return {
        "id": event.id,
        "event_type": event.event_type,
        "status": event.status,
        "message": event.message,
        "metadata": _parse_json_dict(event.metadata_json),
        "created_at": event.created_at.isoformat() if event.created_at else None,
    }


def _serialize_application(app: Application) -> dict:
    return {
        "id": app.id,
        "status": app.status,
        "stage": app.stage,
        "status_reason": app.status_reason,
        "source_url": app.source_url,
        "match_score": app.match_score,
        "needs_user_review": app.needs_user_review,
        "applied_at": app.applied_at.isoformat() if app.applied_at else None,
        "submitted_at": app.submitted_at.isoformat() if app.submitted_at else None,
        "last_event_at": app.last_event_at.isoformat() if app.last_event_at else None,
    }


def _serialize_job(job: Job) -> dict:
    return {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "url": job.url,
        "description": job.description,
        "source": job.source,
        "salary": job.salary,
        "experience_level": job.experience_level,
    }


def _get_latest_application_for_job(db: Session, job_id: int, user_id: int) -> Application | None:
    return db.exec(
        select(Application)
        .where(
            Application.job_id == job_id,
            Application.user_id == user_id,
        )
        .order_by(Application.applied_at.desc(), Application.id.desc())
    ).first()


def _get_application_detail_payload(db: Session, app: Application) -> dict:
    job = db.get(Job, app.job_id)
    artifact = db.exec(
        select(ApplicationArtifact).where(
            ApplicationArtifact.application_id == app.id
        )
    ).first()
    events = db.exec(
        select(ApplicationEvent)
        .where(ApplicationEvent.application_id == app.id)
        .order_by(ApplicationEvent.created_at.desc(), ApplicationEvent.id.desc())
    ).all()

    return {
        "application": _serialize_application(app),
        "job": _serialize_job(job) if job else None,
        "artifact": _serialize_artifact(artifact),
        "events": [_serialize_event(e) for e in events],
    }


@router.get("/by-job/{job_id}")
def get_applications_for_job(
    job_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Returns all applications the current user has for a given job."""
    apps = db.exec(
        select(Application)
        .where(
            Application.job_id == job_id,
            Application.user_id == current_user.id,
        )
        .order_by(Application.applied_at.desc(), Application.id.desc())
    ).all()
    return [_serialize_application(a) for a in apps]


@router.get("/by-job/{job_id}/detail")
def get_latest_application_detail_for_job(
    job_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Returns job detail plus the current user's latest application, if one exists."""
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    app = _get_latest_application_for_job(db, job_id, current_user.id)
    if not app:
        return {
            "application": None,
            "job": _serialize_job(job),
            "artifact": None,
            "events": [],
        }

    return _get_application_detail_payload(db, app)


@router.get("/{application_id}")
def get_application_detail(
    application_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Returns the full detail view for a single application."""
    app = db.get(Application, application_id)
    if not app or app.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Application not found.")

    return _get_application_detail_payload(db, app)


@router.patch("/{application_id}/status")
def update_status(
    application_id: int,
    body: StatusUpdateRequest,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Manually update the status of an application and log the change."""
    if body.status not in ALLOWED_MANUAL_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid status '{body.status}'. Allowed: {sorted(ALLOWED_MANUAL_STATUSES)}",
        )

    app = db.get(Application, application_id)
    if not app or app.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Application not found.")

    old_status = app.status
    update_application_status(
        db,
        app,
        body.status,
        reason=body.note,
        event_type=ApplicationEventType.STATUS_CHANGED,
        message=body.note or f"Status manually changed from {old_status} to {body.status}.",
        metadata={"old_status": old_status, "new_status": body.status, "manual": True},
    )

    logger.info(
        f"Application {application_id} status changed: {old_status} -> {body.status} by {current_user.email}"
    )
    return _serialize_application(app)
