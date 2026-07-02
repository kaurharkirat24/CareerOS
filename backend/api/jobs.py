from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select
from typing import List, Dict, Any
from pydantic import BaseModel

from backend.db.session import get_session
from backend.db.models import Job, User, Application
from backend.api.auth import get_current_user
from backend.agents.job_crawlers.linkedin_crawler import LinkedInCrawler
from backend.agents.job_crawlers.indeed_crawler import IndeedCrawler
from backend.graph.pipeline import application_pipeline, JobApplicationState
from backend.core.logger import get_logger

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
        "Pending": 0,
        "Applied": 0,
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
        should_apply=None,
        reason_skipped=None,
        resume_path=None,
        cover_letter=None,
        application_success=None
    )
    
    # Run pipeline (For production, this should be a background task. Running directly for MVP)
    # Using ainvoke for async execution
    try:
        final_state = await application_pipeline.ainvoke(initial_state)
        
        # Save application status
        status = "Applied" if final_state.get("application_success") else ("Skipped" if not final_state.get("should_apply") else "Failed")
        
        app = Application(
            user_id=current_user.id,
            job_id=job.id,
            status=status,
            match_score=final_state.get("match_score")
        )
        db.add(app)
        db.commit()
        db.refresh(app)
        
        return {
            "message": "Automation completed",
            "status": status,
            "match_score": final_state.get("match_score"),
            "reason_skipped": final_state.get("reason_skipped")
        }
        
    except Exception as e:
        logger.error(f"Error in application pipeline for job {job_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred during the application automation. Please check server logs.")
