from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from sqlalchemy import Column, Text

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    full_name: Optional[str] = None
    resume_text: Optional[str] = None
    # Add other profile fields (skills, experience, etc.) as needed later, perhaps as JSON

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    applications: List["Application"] = Relationship(back_populates="user")

class JobBase(SQLModel):
    title: str
    company: str
    location: Optional[str] = None
    url: str
    description: str
    salary: Optional[str] = None
    experience_level: Optional[str] = None
    source: str # e.g., 'LinkedIn', 'Indeed'

class Job(JobBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    applications: List["Application"] = Relationship(back_populates="job")

class Application(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    job_id: Optional[int] = Field(default=None, foreign_key="job.id")
    status: str = Field(default="Pending") # Pending, Applied, Rejected, Interview, Offer, etc.
    stage: str = Field(default="Draft", index=True)
    status_reason: Optional[str] = Field(default=None, sa_column=Column(Text))
    source_url: Optional[str] = None
    applied_at: datetime = Field(default_factory=datetime.utcnow)
    submitted_at: Optional[datetime] = None
    last_event_at: Optional[datetime] = None
    needs_user_review: bool = Field(default=False)
    match_score: Optional[int] = None
    
    user: Optional[User] = Relationship(back_populates="applications")
    job: Optional[Job] = Relationship(back_populates="applications")
    events: List["ApplicationEvent"] = Relationship(back_populates="application")
    artifact: Optional["ApplicationArtifact"] = Relationship(
        back_populates="application",
        sa_relationship_kwargs={"uselist": False},
    )

class ApplicationEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    application_id: int = Field(foreign_key="application.id", index=True)
    event_type: str = Field(index=True)
    status: str = Field(index=True)
    message: Optional[str] = Field(default=None, sa_column=Column(Text))
    metadata_json: Optional[str] = Field(default=None, sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    application: Optional[Application] = Relationship(back_populates="events")

class ApplicationArtifact(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    application_id: int = Field(foreign_key="application.id", unique=True, index=True)
    tailored_resume_text: Optional[str] = Field(default=None, sa_column=Column(Text))
    resume_pdf_path: Optional[str] = None
    cover_letter_text: Optional[str] = Field(default=None, sa_column=Column(Text))
    match_explanation: Optional[str] = Field(default=None, sa_column=Column(Text))
    matched_skills_json: str = Field(default="[]", sa_column=Column(Text))
    missing_skills_json: str = Field(default="[]", sa_column=Column(Text))
    weak_skills_json: str = Field(default="[]", sa_column=Column(Text))
    change_classifications_json: str = Field(default="[]", sa_column=Column(Text))
    resume_diff_json: str = Field(default="[]", sa_column=Column(Text))
    authenticity_flags_json: str = Field(default="[]", sa_column=Column(Text))
    authenticity_requires_review: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    application: Optional[Application] = Relationship(back_populates="artifact")
