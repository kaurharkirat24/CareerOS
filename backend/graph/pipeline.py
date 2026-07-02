from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from backend.agents.matching_agent import MatchingAgent
from backend.agents.resume_agent import ResumeAgent
from backend.agents.cover_letter_agent import CoverLetterAgent
from backend.agents.application_agent import ApplicationAgent, ApplicationData
import uuid
import os

class JobApplicationState(TypedDict):
    user_id: int
    user_profile: str
    user_data: dict # dict containing first_name, last_name, email, phone etc
    job_id: int
    job_url: str
    job_description: str
    company: str
    role_title: str
    
    # Agent Outcomes
    match_score: Optional[int]
    should_apply: Optional[bool]
    reason_skipped: Optional[str]
    resume_path: Optional[str]
    cover_letter: Optional[str]
    application_success: Optional[bool]

def match_node(state: JobApplicationState):
    agent = MatchingAgent(threshold=70)
    result = agent.analyze(state["job_description"], state["user_profile"])
    return {
        "match_score": result.match_score,
        "should_apply": result.should_apply,
        "reason_skipped": result.reason_skipped
    }

async def prepare_node(state: JobApplicationState):
    resume_agent = ResumeAgent()
    cl_agent = CoverLetterAgent()
    
    # 1. Optimize Resume
    optimized_resume = resume_agent.optimize(state["job_description"], state["user_profile"])
    
    # Setup PDF path
    os.makedirs("generated_resumes", exist_ok=True)
    pdf_path = os.path.abspath(f"generated_resumes/resume_{uuid.uuid4().hex[:8]}.pdf")
    
    await resume_agent.generate_pdf(optimized_resume, pdf_path)
    
    # 2. Generate Cover Letter
    cover_letter = cl_agent.generate(
        job_description=state["job_description"],
        user_profile=state["user_profile"],
        company_name=state["company"],
        role_title=state["role_title"]
    )
    
    return {
        "resume_path": pdf_path,
        "cover_letter": cover_letter
    }

async def apply_node(state: JobApplicationState):
    app_agent = ApplicationAgent()
    
    # Basic fallbacks in case user_data is sparse
    app_data = ApplicationData(
        first_name=state["user_data"].get("first_name", "FirstName"),
        last_name=state["user_data"].get("last_name", "LastName"),
        email=state["user_data"].get("email", "email@example.com"),
        phone=state["user_data"].get("phone", "0000000000"),
        resume_path=state["resume_path"],
        linkedin=state["user_data"].get("linkedin"),
        github=state["user_data"].get("github")
    )
    
    success = await app_agent.apply(state["job_url"], app_data)
    
    return {
        "application_success": success
    }

# Edge routing logic
def check_match_score(state: JobApplicationState):
    if state.get("should_apply") is True:
        return "prepare"
    return END

# Build the LangGraph Workflow
workflow = StateGraph(JobApplicationState)

workflow.add_node("match", match_node)
workflow.add_node("prepare", prepare_node)
workflow.add_node("apply", apply_node)

workflow.set_entry_point("match")

workflow.add_conditional_edges(
    "match",
    check_match_score,
    {
        "prepare": "prepare",
        END: END
    }
)

workflow.add_edge("prepare", "apply")
workflow.add_edge("apply", END)

application_pipeline = workflow.compile()
