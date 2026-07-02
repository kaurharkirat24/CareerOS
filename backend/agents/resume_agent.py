import json
import os
from pydantic import BaseModel
from typing import List, Optional
from playwright.async_api import async_playwright
from backend.agents.llm_client import generate_json

class ResumeExperience(BaseModel):
    company: str
    role: str
    duration: str
    bullets: List[str]

class ResumeProject(BaseModel):
    name: str
    description: str
    technologies: List[str]
    bullets: List[str]

class OptimizedResume(BaseModel):
    name: str
    email: str
    phone: str
    linkedin: Optional[str] = None
    github: Optional[str] = None
    summary: str
    skills: List[str]
    experience: List[ResumeExperience]
    projects: List[ResumeProject]
    education: str

class ResumeAgent:
    def optimize(self, job_description: str, user_profile: str) -> OptimizedResume:
        prompt = f"""
        You are an expert ATS Resume Optimizer.
        Rewrite the user's profile to perfectly match the provided Job Description without hallucinating fake experience.
        Highlight relevant projects, rephrase bullet points to emphasize keywords from the JD, and ensure the summary reflects the role.
        
        Job Description:
        {job_description}
        
        Original User Profile:
        {user_profile}
        
        Return the optimized resume strictly according to the JSON schema.
        """
        
        return generate_json(prompt, OptimizedResume)

    async def generate_pdf(self, resume_data: OptimizedResume, output_path: str):
        # Basic clean ATS-friendly HTML template
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Arial', sans-serif; line-height: 1.4; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
                h1 {{ font-size: 24px; text-align: center; margin-bottom: 5px; text-transform: uppercase; }}
                .contact {{ text-align: center; font-size: 12px; margin-bottom: 20px; }}
                .contact a {{ color: #333; text-decoration: none; }}
                h2 {{ font-size: 16px; border-bottom: 1px solid #333; text-transform: uppercase; margin-top: 15px; padding-bottom: 2px; }}
                .section-content {{ margin-bottom: 15px; font-size: 13px; }}
                .item-header {{ display: flex; justify-content: space-between; font-weight: bold; margin-bottom: 2px; }}
                .item-sub {{ display: flex; justify-content: space-between; font-style: italic; margin-bottom: 5px; }}
                ul {{ margin-top: 0; padding-left: 20px; }}
                li {{ margin-bottom: 3px; }}
                .skills {{ font-size: 13px; }}
            </style>
        </head>
        <body>
            <h1>{resume_data.name}</h1>
            <div class="contact">
                {resume_data.email} | {resume_data.phone}
                {f' | <a href="{resume_data.linkedin}">LinkedIn</a>' if resume_data.linkedin else ''}
                {f' | <a href="{resume_data.github}">GitHub</a>' if resume_data.github else ''}
            </div>

            <h2>Summary</h2>
            <div class="section-content">
                {resume_data.summary}
            </div>

            <h2>Skills</h2>
            <div class="section-content skills">
                {', '.join(resume_data.skills)}
            </div>

            <h2>Experience</h2>
            <div class="section-content">
                {''.join([f'''
                <div class="item">
                    <div class="item-header"><span>{exp.role}</span><span>{exp.duration}</span></div>
                    <div class="item-sub"><span>{exp.company}</span></div>
                    <ul>
                        {''.join([f"<li>{bullet}</li>" for bullet in exp.bullets])}
                    </ul>
                </div>
                ''' for exp in resume_data.experience])}
            </div>

            <h2>Projects</h2>
            <div class="section-content">
                {''.join([f'''
                <div class="item">
                    <div class="item-header"><span>{proj.name}</span></div>
                    <div class="item-sub"><span>{', '.join(proj.technologies)}</span></div>
                    <ul>
                        {''.join([f"<li>{bullet}</li>" for bullet in proj.bullets])}
                    </ul>
                </div>
                ''' for proj in resume_data.projects])}
            </div>

            <h2>Education</h2>
            <div class="section-content">
                {resume_data.education}
            </div>
        </body>
        </html>
        """
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.set_content(html_content)
            await page.pdf(path=output_path, format="A4", margin={"top": "20px", "bottom": "20px", "left": "20px", "right": "20px"})
            await browser.close()
