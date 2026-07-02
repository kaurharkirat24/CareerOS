from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

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
    applied_at: datetime = Field(default_factory=datetime.utcnow)
    match_score: Optional[int] = None
    
    user: Optional[User] = Relationship(back_populates="applications")
    job: Optional[Job] = Relationship(back_populates="applications")
