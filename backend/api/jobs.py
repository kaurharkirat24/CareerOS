from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from pydantic import BaseModel

from backend.db.session import get_session
from backend.db.models import Job, User, Application
from backend.api.auth import get_current_user
from backend.agents.job_crawlers.linkedin_crawler import LinkedInCrawler
from backend.agents.job_crawlers.indeed_crawler import IndeedCrawler
from backend.graph.pipeline import application_pipeline, JobApplicationState
from backend.core.logger import get_logger
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
async def scrape_jobs(req: ScrapeRequest, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
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
                    source=job_data.source
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
        "Offer": 0
    }
    
    for app in apps:
        if app.status in stats:
            stats[app.status] += 1
            
    return stats

@router.get("/", response_model=List[Job])
def get_jobs(db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Retrieves all jobs."""
    jobs = db.exec(select(Job)).all()
    return jobs

@router.post("/{job_id}/apply")
async def apply_to_job(job_id: int, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Runs the LangGraph automation pipeline for a specific job."""
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if not current_user.resume_text:
        raise HTTPException(status_code=400, detail="User profile/resume text is missing. Please update your profile first.")

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
        db,
        app,
        event_type=ApplicationEventType.CREATED,
        status=ApplicationStatus.DRAFT,
        message="Application record created.",
        metadata={"job_id": job.id, "job_url": job.url, "source": job.source},
    )
    update_application_status(
        db,
        app,
        ApplicationStatus.PENDING,
        stage="Automation Started",
        event_type=ApplicationEventType.AUTOMATION_STARTED,
        message="Application automation started.",
    )

    # Setup initial state for LangGraph
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
        match_score=None,
        match_explanation=None,
        matching_skills=None,
        missing_skills=None,
        should_apply=None,
        reason_skipped=None,
        tailored_resume_text=None,
        resume_path=None,
        cover_letter=None,
        application_success=None
    )
    
    # Run pipeline (For production, this should be a background task. Running directly for MVP)
    # Using ainvoke for async execution
    try:
        final_state = await application_pipeline.ainvoke(initial_state)

        app.match_score = final_state.get("match_score")
        db.add(app)
        db.commit()
        db.refresh(app)

        if final_state.get("match_score") is not None:
            record_application_event(
                db,
                app,
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

        upsert_application_artifact(
            db,
            app,
            tailored_resume_text=final_state.get("tailored_resume_text"),
            resume_pdf_path=final_state.get("resume_path"),
            cover_letter_text=final_state.get("cover_letter"),
            match_explanation=final_state.get("match_explanation"),
            matched_skills=final_state.get("matching_skills"),
            missing_skills=final_state.get("missing_skills"),
        )

        if final_state.get("resume_path"):
            record_application_event(
                db,
                app,
                event_type=ApplicationEventType.RESUME_GENERATED,
                status=ApplicationStatus.PENDING,
                message="Tailored resume PDF generated.",
                metadata={"resume_path": final_state.get("resume_path")},
            )

        if final_state.get("cover_letter"):
            record_application_event(
                db,
                app,
                event_type=ApplicationEventType.COVER_LETTER_GENERATED,
                status=ApplicationStatus.PENDING,
                message="Cover letter generated.",
            )

        # Save final application status
        if final_state.get("application_success"):
            status = ApplicationStatus.APPLIED
            event_type = ApplicationEventType.SUBMITTED
            reason = "Application submitted successfully."
        elif final_state.get("should_apply") is False:
            status = ApplicationStatus.SKIPPED
            event_type = ApplicationEventType.SKIPPED
            reason = final_state.get("reason_skipped") or "Application skipped by match analysis."
        else:
            status = ApplicationStatus.FAILED
            event_type = ApplicationEventType.FAILED
            reason = "Automation finished without confirming submission."

        update_application_status(
            db,
            app,
            status,
            reason=reason,
            event_type=event_type,
            message=reason,
            metadata={
                "match_score": final_state.get("match_score"),
                "should_apply": final_state.get("should_apply"),
                "application_success": final_state.get("application_success"),
            },
        )
        
        return {
            "message": "Automation completed",
            "application_id": app.id,
            "status": status,
            "match_score": final_state.get("match_score"),
            "reason_skipped": final_state.get("reason_skipped")
        }
        
    except Exception as e:
        logger.error(f"Error in application pipeline for job {job_id}: {e}", exc_info=True)
        update_application_status(
            db,
            app,
            ApplicationStatus.FAILED,
            reason="Application automation failed. Please check server logs.",
            event_type=ApplicationEventType.FAILED,
            message="Application automation failed.",
            metadata={"error": str(e), "job_id": job_id},
        )
        raise HTTPException(status_code=500, detail="An error occurred during the application automation. Please check server logs.")
