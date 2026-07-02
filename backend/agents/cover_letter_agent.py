from backend.agents.llm_client import generate_text

class CoverLetterAgent:
    def generate(self, job_description: str, user_profile: str, company_name: str, role_title: str) -> str:
        prompt = f"""
        You are an expert career coach writing a personalized cover letter.
        Write a compelling, professional cover letter for the '{role_title}' position at '{company_name}'.
        
        Use the following Job Description to understand what the company needs:
        {job_description}
        
        Use the following User Profile to highlight the most relevant experience and skills:
        {user_profile}
        
        Guidelines:
        - Keep it under 350 words.
        - Do not use generic openers. Start with a strong hook about why the candidate is a great fit.
        - Highlight 1-2 specific achievements from the profile that directly address the JD.
        - Tone should be professional, enthusiastic, and confident.
        - Do not hallucinate skills or experiences not present in the user profile.
        
        Output ONLY the cover letter text (without any markdown formatting blocks).
        """
        
        return generate_text(prompt)
