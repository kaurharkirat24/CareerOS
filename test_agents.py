import asyncio
from backend.agents.matching_agent import MatchingAgent
from backend.agents.resume_agent import ResumeAgent
from backend.agents.cover_letter_agent import CoverLetterAgent

# Sample Data
SAMPLE_JD = """
We are looking for a Python Backend Developer with 3+ years of experience.
Must have strong skills in FastAPI, SQLModel, Docker, and REST APIs.
Experience with AI tools (LangChain, OpenAI, Gemini) is a huge plus.
"""

SAMPLE_PROFILE = """
I am a software engineer with 2 years of experience.
I have built backend systems using Python, Django, and FastAPI.
I am familiar with PostgreSQL and have deployed apps using Docker.
I also built a side project using the Gemini API.
"""

async def run_tests():
    print("--- 1. Testing Matching Agent ---")
    matcher = MatchingAgent(threshold=70)
    match_result = matcher.analyze(SAMPLE_JD, SAMPLE_PROFILE)
    print(f"Match Score: {match_result.match_score}%")
    print(f"Should Apply: {match_result.should_apply}")
    print(f"Matching Skills: {', '.join(match_result.matching_skills)}")
    print(f"Missing Skills: {', '.join(match_result.missing_skills)}")
    print("\n")

    print("--- 2. Testing Cover Letter Agent ---")
    cover_letter_agent = CoverLetterAgent()
    cover_letter = cover_letter_agent.generate(
        job_description=SAMPLE_JD,
        user_profile=SAMPLE_PROFILE,
        company_name="TechCorp AI",
        role_title="Python Backend Developer"
    )
    print(cover_letter)
    print("\n")

    print("--- 3. Testing Resume Agent (JSON + PDF Generation) ---")
    resume_agent = ResumeAgent()
    optimized_resume = resume_agent.optimize(SAMPLE_JD, SAMPLE_PROFILE)
    print("Optimized Summary:", optimized_resume.summary)
    
    # Generate the PDF
    pdf_path = "test_resume.pdf"
    await resume_agent.generate_pdf(optimized_resume, pdf_path)
    print(f"PDF generated successfully at {pdf_path}")

if __name__ == "__main__":
    asyncio.run(run_tests())
