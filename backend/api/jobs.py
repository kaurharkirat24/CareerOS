from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel

from backend.db.session import get_session
from backend.db.models import Job, User, Application, ApplicationArtifact
from backend.api.auth import get_current_user
from backend.agents.job_crawlers.linkedin_crawler import LinkedInCrawler
from backend.agents.job_crawlers.indeed_crawler import IndeedCrawler
from backend.agents.application_agent import ApplicationAgent, ApplicationData
from backend.graph.pipeline import application_pipeline, JobApplicationState
from backend.core.logger import get_logger
from backend.services.authenticity import analyze_resume_authenticity
from backend.services.application_tracking import (
    ApplicationEventType,
    ApplicationStatus,
    record_application_event,
    update_application_status,
    upsert_application_artifact,
)

router = APIRouter()
logger = get_logger("jobs_api")


class ScrapeRequest(BaseModel):
    keyword: str
    location: str
    max_results: int = 5


@router.post("/scrape")
async def scrape_jobs(
    req: ScrapeRequest,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Scrapes jobs from LinkedIn and Indeed and saves them to the database."""
    linkedin = LinkedInCrawler()
    indeed = IndeedCrawler()

    try:
        scraped_linkedin = await linkedin.crawl(req.keyword, req.location, req.max_results)
        scraped_indeed = await indeed.crawl(req.keyword, req.location, req.max_results)

        all_scraped = scraped_linkedin + scraped_indeed
        saved_jobs = []

        for job_data in all_scraped:
            existing = db.exec(select(Job).where(Job.url == job_data.url)).first()
            if not existing:
                new_job = Job(
                    title=job_data.title,
                    company=job_data.company,
                    location=job_data.location,
                    url=job_data.url,
                    description=job_data.description,
                    source=job_data.source,
                )
                db.add(new_job)
                db.commit()
                db.refresh(new_job)
                saved_jobs.append(new_job)

        logger.info(f"Scraped and saved {len(saved_jobs)} new jobs for keyword: {req.keyword}")
        return {"message": f"Successfully scraped and saved {len(saved_jobs)} new jobs.", "jobs": saved_jobs}
    except Exception as e:
        logger.error(f"Error during job scraping: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while scraping jobs. Please check server logs.")


@router.get("/stats")
def get_stats(db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Retrieves application statistics for the dashboard."""
    apps = db.exec(select(Application).where(Application.user_id == current_user.id)).all()

    stats = {
        "Total": len(apps),
        "Draft": 0,
        "Pending": 0,
        "Ready": 0,
        "Applied": 0,
        "Failed": 0,
        "Skipped": 0,
        "Needs Review": 0,
        "Rejected": 0,
        "Interview": 0,
        "Offer": 0,
    }

    for app in apps:
        if app.status in stats:
            stats[app.status] += 1

    return stats


@router.get("/")
def get_jobs(db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Retrieves all jobs with the current user's latest application status."""
    jobs = db.exec(select(Job)).all()

    # Batch-fetch user's applications keyed by job_id
    user_apps = db.exec(
        select(Application).where(Application.user_id == current_user.id)
    ).all()
    app_by_job: dict[int, Application] = {}
    for app in user_apps:
        existing = app_by_job.get(app.job_id)
        if existing is None or (app.applied_at and (existing.applied_at is None or app.applied_at > existing.applied_at)):
            app_by_job[app.job_id] = app

    result = []
    for job in jobs:
        job_dict = {
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
        app = app_by_job.get(job.id)
        if app:
            job_dict["application"] = {
                "id": app.id,
                "status": app.status,
                "match_score": app.match_score,
            }
        else:
            job_dict["application"] = None
        result.append(job_dict)

    return result


# ---------------------------------------------------------------------------
# Prepare-first application flow
# ---------------------------------------------------------------------------


@router.post("/{job_id}/apply")
async def apply_to_job(
    job_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Runs the LangGraph pipeline in prepare-first mode: generates match analysis,
    tailored resume, and cover letter, then stops for user review."""
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if not current_user.resume_text:
        raise HTTPException(
            status_code=400,
            detail="User profile/resume text is missing. Please update your profile first.",
        )

    app = Application(
        user_id=current_user.id,
        job_id=job.id,
        status=ApplicationStatus.DRAFT,
        stage=ApplicationStatus.DRAFT,
        source_url=job.url,
    )
    db.add(app)
    db.commit()
    db.refresh(app)

    record_application_event(
        db, app,
        event_type=ApplicationEventType.CREATED,
        status=ApplicationStatus.DRAFT,
        message="Application record created.",
        metadata={"job_id": job.id, "job_url": job.url, "source": job.source},
    )
    update_application_status(
        db, app,
        ApplicationStatus.PENDING,
        stage="Automation Started",
        event_type=ApplicationEventType.AUTOMATION_STARTED,
        message="Application automation started (prepare-first mode).",
    )

    initial_state = JobApplicationState(
        user_id=current_user.id,
        user_profile=current_user.resume_text,
        user_data={
            "first_name": current_user.full_name.split()[0] if current_user.full_name else "FirstName",
            "last_name": current_user.full_name.split()[-1] if current_user.full_name and len(current_user.full_name.split()) > 1 else "LastName",
            "email": current_user.email,
        },
        job_id=job.id,
        job_url=job.url,
        job_description=job.description,
        company=job.company,
        role_title=job.title,
        auto_submit=False,
        match_score=None,
        match_explanation=None,
        matching_skills=None,
        missing_skills=None,
        should_apply=None,
        reason_skipped=None,
        tailored_resume_text=None,
        resume_path=None,
        cover_letter=None,
        application_success=None,
    )

    try:
        final_state = await application_pipeline.ainvoke(initial_state)

        app.match_score = final_state.get("match_score")
        db.add(app)
        db.commit()
        db.refresh(app)

        if final_state.get("match_score") is not None:
            record_application_event(
                db, app,
                event_type=ApplicationEventType.MATCH_SCORED,
                status=ApplicationStatus.PENDING,
                message=f"Job match score calculated: {final_state.get('match_score')}%.",
                metadata={
                    "match_score": final_state.get("match_score"),
                    "match_explanation": final_state.get("match_explanation"),
                    "matching_skills": final_state.get("matching_skills"),
                    "missing_skills": final_state.get("missing_skills"),
                    "should_apply": final_state.get("should_apply"),
                    "reason_skipped": final_state.get("reason_skipped"),
                },
            )

        authenticity = analyze_resume_authenticity(
            current_user.resume_text,
            final_state.get("tailored_resume_text"),
        )

        upsert_application_artifact(
            db, app,
            tailored_resume_text=final_state.get("tailored_resume_text"),
            resume_pdf_path=final_state.get("resume_path"),
            cover_letter_text=final_state.get("cover_letter"),
            match_explanation=final_state.get("match_explanation"),
            matched_skills=final_state.get("matching_skills"),
            missing_skills=final_state.get("missing_skills"),
            change_classifications=authenticity["change_classifications"],
            resume_diff=authenticity["resume_diff"],
            authenticity_flags=authenticity["authenticity_flags"],
            authenticity_requires_review=authenticity["requires_review"],
        )

        if final_state.get("resume_path"):
            record_application_event(
                db, app,
                event_type=ApplicationEventType.RESUME_GENERATED,
                status=ApplicationStatus.PENDING,
                message="Tailored resume PDF generated.",
                metadata={"resume_path": final_state.get("resume_path")},
            )

        if final_state.get("cover_letter"):
            record_application_event(
                db, app,
                event_type=ApplicationEventType.COVER_LETTER_GENERATED,
                status=ApplicationStatus.PENDING,
                message="Cover letter generated.",
            )

        if authenticity["requires_review"]:
            record_application_event(
                db, app,
                event_type=ApplicationEventType.STATUS_CHANGED,
                status=ApplicationStatus.PENDING,
                message="Authenticity guardrails flagged resume claims for review.",
                metadata={
                    "flag_count": len(authenticity["authenticity_flags"]),
                    "review_item_count": len(
                        [
                            item
                            for item in authenticity["change_classifications"]
                            if item.get("requires_review")
                        ]
                    ),
                },
            )

        # Determine final status for prepare-first mode
        if final_state.get("should_apply") is False:
            status = ApplicationStatus.SKIPPED
            event_type = ApplicationEventType.SKIPPED
            reason = final_state.get("reason_skipped") or "Application skipped by match analysis."
        else:
            status = ApplicationStatus.NEEDS_REVIEW
            event_type = ApplicationEventType.STATUS_CHANGED
            reason = "Artifacts ready for review. Approve to submit."

        update_application_status(
            db, app, status,
            reason=reason,
            needs_user_review=(status == ApplicationStatus.NEEDS_REVIEW),
            event_type=event_type,
            message=reason,
            metadata={
                "match_score": final_state.get("match_score"),
                "should_apply": final_state.get("should_apply"),
                "auto_submit": False,
            },
        )

        return {
            "message": "Preparation complete. Review artifacts before submitting.",
            "application_id": app.id,
            "status": status,
            "match_score": final_state.get("match_score"),
            "reason_skipped": final_state.get("reason_skipped"),
        }

    except Exception as e:
        logger.error(f"Error in application pipeline for job {job_id}: {e}", exc_info=True)
        update_application_status(
            db, app, ApplicationStatus.FAILED,
            reason="Application automation failed. Please check server logs.",
            event_type=ApplicationEventType.FAILED,
            message="Application automation failed.",
            metadata={"error": str(e), "job_id": job_id},
        )
        raise HTTPException(
            status_code=500,
            detail="An error occurred during the application automation. Please check server logs.",
        )


# ---------------------------------------------------------------------------
# Explicit submit after user approval
# ---------------------------------------------------------------------------


@router.post("/{job_id}/submit")
async def submit_application(
    job_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Runs the browser automation apply step after the user has reviewed
    the generated artifacts. Only works on applications in 'Needs Review' or 'Ready'."""
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    app = db.exec(
        select(Application)
        .where(Application.job_id == job_id, Application.user_id == current_user.id)
        .order_by(Application.applied_at.desc())
    ).first()

    if not app:
        raise HTTPException(status_code=404, detail="No application found. Run 'Prepare' first.")

    if app.status not in (ApplicationStatus.NEEDS_REVIEW, ApplicationStatus.READY):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot submit application in '{app.status}' status. Must be 'Needs Review' or 'Ready'.",
        )

    artifact = db.exec(
        select(ApplicationArtifact).where(ApplicationArtifact.application_id == app.id)
    ).first()

    resume_path = artifact.resume_pdf_path if artifact else None
    if not resume_path:
        raise HTTPException(status_code=400, detail="No generated resume found. Run 'Prepare' again.")

    update_application_status(
        db, app, ApplicationStatus.PENDING,
        stage="Submitting",
        event_type=ApplicationEventType.AUTOMATION_STARTED,
        message="User approved. Starting browser submission.",
        metadata={"approved_by": current_user.email},
    )

    try:
        app_agent = ApplicationAgent()
        app_data = ApplicationData(
            first_name=current_user.full_name.split()[0] if current_user.full_name else "FirstName",
            last_name=current_user.full_name.split()[-1] if current_user.full_name and len(current_user.full_name.split()) > 1 else "LastName",
            email=current_user.email,
            phone="0000000000",
            resume_path=resume_path,
            linkedin=None,
            github=None,
        )

        success = await app_agent.apply(job.url, app_data, submit=True)

        if success:
            status = ApplicationStatus.APPLIED
            event_type = ApplicationEventType.SUBMITTED
            reason = "Application submitted successfully via browser automation."
        else:
            status = ApplicationStatus.FAILED
            event_type = ApplicationEventType.FAILED
            reason = "Browser automation completed but submission was not confirmed."

        update_application_status(
            db, app, status,
            reason=reason,
            needs_user_review=False,
            event_type=event_type,
            message=reason,
            metadata={"application_success": success},
        )

        return {
            "message": reason,
            "application_id": app.id,
            "status": status,
        }

    except Exception as e:
        logger.error(f"Error submitting application for job {job_id}: {e}", exc_info=True)
        update_application_status(
            db, app, ApplicationStatus.FAILED,
            reason="Submission failed. Please check server logs.",
            event_type=ApplicationEventType.FAILED,
            message="Submission automation failed.",
            metadata={"error": str(e), "job_id": job_id},
        )
        raise HTTPException(
            status_code=500,
            detail="An error occurred during submission. Please check server logs.",
        )
