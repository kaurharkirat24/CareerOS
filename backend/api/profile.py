from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from pydantic import BaseModel

from backend.db.session import get_session
from backend.db.models import User
from backend.api.auth import get_current_user
from backend.core.logger import get_logger

router = APIRouter()
logger = get_logger("profile_api")

class ProfileUpdate(BaseModel):
    full_name: str | None = None
    resume_text: str | None = None

@router.get("/")
def get_profile(current_user: User = Depends(get_current_user)):
    """Retrieves the current user's profile."""
    return {
        "email": current_user.email,
        "full_name": current_user.full_name,
        "resume_text": current_user.resume_text
    }

@router.put("/")
def update_profile(profile_data: ProfileUpdate, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Updates the current user's profile."""
    try:
        if profile_data.full_name is not None:
            current_user.full_name = profile_data.full_name
        if profile_data.resume_text is not None:
            current_user.resume_text = profile_data.resume_text
            
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"Profile updated successfully for user: {current_user.email}")
        return {"message": "Profile updated successfully"}
    except Exception as e:
        logger.error(f"Error updating profile for {current_user.email}: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update profile. Please try again.")
