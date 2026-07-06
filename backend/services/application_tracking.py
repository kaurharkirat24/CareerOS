import json
from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from backend.db.models import Application, ApplicationArtifact, ApplicationEvent


class ApplicationStatus:
    DRAFT = "Draft"
    READY = "Ready"
    APPLIED = "Applied"
    FAILED = "Failed"
    SKIPPED = "Skipped"
    NEEDS_REVIEW = "Needs Review"
    PENDING = "Pending"
    REJECTED = "Rejected"
    INTERVIEW = "Interview"
    OFFER = "Offer"


class ApplicationEventType:
    CREATED = "application_created"
    AUTOMATION_STARTED = "automation_started"
    MATCH_SCORED = "match_scored"
    RESUME_GENERATED = "resume_generated"
    COVER_LETTER_GENERATED = "cover_letter_generated"
    SUBMITTED = "submitted"
    SKIPPED = "skipped"
    FAILED = "failed"
    STATUS_CHANGED = "status_changed"


def _json_dumps(value: Any) -> str:
    return json.dumps(value, default=str)


def record_application_event(
    db: Session,
    application: Application,
    event_type: str,
    status: str,
    message: str | None = None,
    metadata: dict[str, Any] | None = None,
    commit: bool = True,
) -> ApplicationEvent:
    if application.id is None:
        raise ValueError("Application must be persisted before events can be recorded.")

    now = datetime.utcnow()
    event = ApplicationEvent(
        application_id=application.id,
        event_type=event_type,
        status=status,
        message=message,
        metadata_json=_json_dumps(metadata or {}),
        created_at=now,
    )
    application.last_event_at = now

    db.add(application)
    db.add(event)
    if commit:
        db.commit()
        db.refresh(application)
        db.refresh(event)

    return event


def update_application_status(
    db: Session,
    application: Application,
    status: str,
    *,
    stage: str | None = None,
    reason: str | None = None,
    needs_user_review: bool | None = None,
    event_type: str = ApplicationEventType.STATUS_CHANGED,
    message: str | None = None,
    metadata: dict[str, Any] | None = None,
    commit: bool = True,
) -> ApplicationEvent:
    application.status = status
    application.stage = stage or status
    application.status_reason = reason
    if needs_user_review is not None:
        application.needs_user_review = needs_user_review
    if status == ApplicationStatus.APPLIED and application.submitted_at is None:
        application.submitted_at = datetime.utcnow()

    return record_application_event(
        db=db,
        application=application,
        event_type=event_type,
        status=status,
        message=message or reason,
        metadata=metadata,
        commit=commit,
    )


def upsert_application_artifact(
    db: Session,
    application: Application,
    *,
    tailored_resume_text: str | None = None,
    resume_pdf_path: str | None = None,
    cover_letter_text: str | None = None,
    match_explanation: str | None = None,
    matched_skills: list[str] | None = None,
    missing_skills: list[str] | None = None,
    weak_skills: list[str] | None = None,
    change_classifications: list[dict[str, Any]] | None = None,
    resume_diff: list[dict[str, Any]] | None = None,
    authenticity_flags: list[dict[str, Any]] | None = None,
    authenticity_requires_review: bool | None = None,
    commit: bool = True,
) -> ApplicationArtifact:
    if application.id is None:
        raise ValueError("Application must be persisted before artifacts can be stored.")

    artifact = db.exec(
        select(ApplicationArtifact).where(ApplicationArtifact.application_id == application.id)
    ).first()
    if artifact is None:
        artifact = ApplicationArtifact(application_id=application.id)

    if tailored_resume_text is not None:
        artifact.tailored_resume_text = tailored_resume_text
    if resume_pdf_path is not None:
        artifact.resume_pdf_path = resume_pdf_path
    if cover_letter_text is not None:
        artifact.cover_letter_text = cover_letter_text
    if match_explanation is not None:
        artifact.match_explanation = match_explanation
    if matched_skills is not None:
        artifact.matched_skills_json = _json_dumps(matched_skills)
    if missing_skills is not None:
        artifact.missing_skills_json = _json_dumps(missing_skills)
    if weak_skills is not None:
        artifact.weak_skills_json = _json_dumps(weak_skills)
    if change_classifications is not None:
        artifact.change_classifications_json = _json_dumps(change_classifications)
    if resume_diff is not None:
        artifact.resume_diff_json = _json_dumps(resume_diff)
    if authenticity_flags is not None:
        artifact.authenticity_flags_json = _json_dumps(authenticity_flags)
    if authenticity_requires_review is not None:
        artifact.authenticity_requires_review = authenticity_requires_review

    artifact.updated_at = datetime.utcnow()
    db.add(artifact)
    if commit:
        db.commit()
        db.refresh(artifact)

    return artifact
