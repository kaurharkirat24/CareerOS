from pydantic import BaseModel
from typing import List, Optional
from backend.agents.llm_client import generate_json

class MatchAnalysis(BaseModel):
    match_score: int
    fit_analysis: str
    matching_skills: List[str]
    missing_skills: List[str]
    should_apply: bool
    reason_skipped: Optional[str] = None

class MatchingAgent:
    def __init__(self, threshold: int = 70):
        self.threshold = threshold

    def analyze(self, job_description: str, user_profile: str) -> MatchAnalysis:
        prompt = f"""
        You are an expert technical recruiter and career coach.
        Analyze the following job description against the user's profile.
        
        Job Description:
        {job_description}
        
        User Profile:
        {user_profile}
        
        Evaluate the match based on skills, experience level, and role requirements.
        Output a detailed JSON response according to the provided schema.
        Set 'should_apply' to true if the match_score is >= {self.threshold}. If false, provide a 'reason_skipped'.
        """
        
        result = generate_json(prompt, MatchAnalysis)
        
        # Enforce threshold logic safely
        if result.match_score < self.threshold:
            result.should_apply = False
            if not result.reason_skipped:
                result.reason_skipped = f"Match score ({result.match_score}%) is below the {self.threshold}% threshold."
        else:
            result.should_apply = True
            result.reason_skipped = None
            
        return result
