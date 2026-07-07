"""Profile management endpoints including resume file upload and parsing."""

import json
import os
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlmodel import Session

from backend.api.auth import get_current_user
from backend.core.logger import get_logger
from backend.db.models import User
from backend.db.session import get_session
from backend.services.resume_parser import (
    StructuredProfile,
    extract_text_from_pdf,
    parse_resume_to_profile,
)

router = APIRouter()
logger = get_logger("profile_api")

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploaded_resumes")


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    resume_text: Optional[str] = None


# ---------------------------------------------------------------------------
# Profile CRUD
# ---------------------------------------------------------------------------


@router.get("/")
def get_profile(current_user: User = Depends(get_current_user)):
    """Retrieves the current user's profile including parsed profile data."""
    parsed_profile = None
    if current_user.parsed_profile_json:
        try:
            parsed_profile = json.loads(current_user.parsed_profile_json)
        except (json.JSONDecodeError, TypeError):
            parsed_profile = None

    return {
        "email": current_user.email,
        "full_name": current_user.full_name,
        "resume_text": current_user.resume_text,
        "resume_file_path": current_user.resume_file_path,
        "parsed_profile": parsed_profile,
    }


@router.put("/")
def update_profile(
    profile_data: ProfileUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Updates the current user's text-based profile fields."""
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


# ---------------------------------------------------------------------------
# Resume upload + parse
# ---------------------------------------------------------------------------


@router.post("/resume/upload")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Uploads a PDF resume, extracts text, and returns it for user review.

    The file is saved to disk and the extracted text is returned.
    The user can review/edit the text before confirming via the /resume/confirm endpoint.
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")

    allowed_extensions = (".pdf",)
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Only PDF files are accepted.",
        )

    # Validate file size (max 10 MB)
    content = await file.read()
    max_size = 10 * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10 MB.")

    # Save to disk
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    safe_filename = f"{current_user.id}_{uuid.uuid4().hex[:8]}{ext}"
    file_path = os.path.abspath(os.path.join(UPLOAD_DIR, safe_filename))

    with open(file_path, "wb") as f:
        f.write(content)

    logger.info(f"Resume uploaded for user {current_user.email}: {file_path}")

    # Extract text from PDF
    try:
        extracted_text = extract_text_from_pdf(file_path)
    except (FileNotFoundError, ValueError) as e:
        # Clean up the file if extraction fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"PDF extraction failed for {file_path}: {e}", exc_info=True)
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail="Failed to extract text from PDF.")

    # Save the file path to user record (text is saved only after user confirms)
    current_user.resume_file_path = file_path
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return {
        "message": "Resume uploaded and text extracted. Review and confirm below.",
        "file_path": file_path,
        "extracted_text": extracted_text,
    }


@router.post("/resume/confirm")
def confirm_resume(
    body: ProfileUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Saves the user-reviewed resume text and runs structured profile extraction.

    Called after the user reviews (and optionally edits) the extracted text
    returned by /resume/upload.
    """
    if not body.resume_text or not body.resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume text cannot be empty.")

    # Save the plain text
    current_user.resume_text = body.resume_text.strip()

    # Run LLM-based structured extraction
    try:
        structured: StructuredProfile = parse_resume_to_profile(current_user.resume_text)
        current_user.parsed_profile_json = structured.model_dump_json()
        logger.info(f"Structured profile extracted for user {current_user.email}")
    except Exception as e:
        logger.warning(
            f"Structured profile extraction failed for {current_user.email}: {e}. "
            "Saving plain text only.",
            exc_info=True,
        )
        # Don't block saving — the text is the critical piece
        current_user.parsed_profile_json = None

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    parsed_profile = None
    if current_user.parsed_profile_json:
        try:
            parsed_profile = json.loads(current_user.parsed_profile_json)
        except (json.JSONDecodeError, TypeError):
            pass

    return {
        "message": "Resume saved and profile extracted successfully.",
        "parsed_profile": parsed_profile,
    }
