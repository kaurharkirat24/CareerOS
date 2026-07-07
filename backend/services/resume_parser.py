"""Resume parsing service: extracts text from PDF files and structures it
into a profile using an LLM."""

import os
from typing import Optional

import pdfplumber
from pydantic import BaseModel

from backend.agents.llm_client import generate_json, generate_text
from backend.core.logger import get_logger

logger = get_logger("resume_parser")


# ---------------------------------------------------------------------------
# Structured profile schema
# ---------------------------------------------------------------------------

class ProfileExperience(BaseModel):
    company: str
    role: str
    duration: str
    bullets: list[str]


class ProfileProject(BaseModel):
    name: str
    description: str
    technologies: list[str]
    bullets: list[str]


class ProfileEducation(BaseModel):
    institution: str
    degree: str
    duration: str


class StructuredProfile(BaseModel):
    """The output schema for LLM-based profile extraction."""
    summary: str
    skills: list[str]
    experience: list[ProfileExperience]
    projects: list[ProfileProject]
    education: list[ProfileEducation]
    links: list[str]
    contact_name: str
    contact_email: str
    contact_phone: str


# ---------------------------------------------------------------------------
# PDF text extraction
# ---------------------------------------------------------------------------

def extract_text_from_pdf(file_path: str) -> str:
    """Extracts plain text from a PDF file using pdfplumber.

    Preserves page-level ordering and basic line structure.
    Returns a single string with pages separated by double newlines.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    pages: list[str] = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text.strip())

    full_text = "\n\n".join(pages)
    if not full_text.strip():
        raise ValueError("PDF contained no extractable text.")

    logger.info(f"Extracted {len(full_text)} chars from {len(pages)} pages of {file_path}")
    return full_text


# ---------------------------------------------------------------------------
# LLM-based structured profile extraction
# ---------------------------------------------------------------------------

def parse_resume_to_profile(resume_text: str) -> StructuredProfile:
    """Uses the LLM to convert raw resume text into a structured profile.

    This extracts key sections (summary, skills, experience, projects,
    education, links, contact details) and returns a validated Pydantic model.
    """
    prompt = f"""You are an expert resume parser. Given the following resume text,
extract the information into a structured profile. Be thorough and accurate.

RULES:
1. Extract EXACTLY what is written. Do NOT invent, embellish, or add information.
2. If a section is missing, return an empty list or empty string.
3. For skills, list each individual skill/tool/technology as a separate item.
4. For experience and projects, preserve the original bullet points faithfully.
5. For contact details, extract the name, email, and phone if present.
6. For links, extract LinkedIn, GitHub, portfolio URLs, etc.

Resume Text:
---
{resume_text}
---

Return the structured profile strictly according to the JSON schema."""

    return generate_json(prompt, StructuredProfile)
