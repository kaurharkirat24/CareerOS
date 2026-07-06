import os
from playwright.async_api import async_playwright
from backend.utils.playwright_helper import PlaywrightHelper
from pydantic import BaseModel
from typing import Optional

class ApplicationData(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    resume_path: str # Path to the generated PDF
    cover_letter_path: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None

class ApplicationAgent:
    """Agent responsible for navigating application forms and submitting them."""
    
    async def apply(self, job_url: str, app_data: ApplicationData, *, submit: bool = False) -> bool:
        """
        Attempts to apply to a job URL. 
        Note: True robustness requires handling dozens of ATS providers (Greenhouse, Lever, Workday).
        This is a generic baseline implementation focusing on standard inputs.
        If submit is False, the agent stops when the form appears ready for final submission.
        """
        async with async_playwright() as p:
            context = await PlaywrightHelper.create_browser_context(p, headless=False) # Headless=False for debugging/visibility
            page = await context.new_page()
            
            try:
                await page.goto(job_url, wait_until="networkidle")
                await PlaywrightHelper.human_delay(2000, 4000)
                
                # Check if it's an "Easy Apply" or external ATS
                # We will attempt generic selectors common in ATS like Greenhouse/Lever
                
                # 1. First Name
                first_name_input = page.locator('input[name*="first"], input[id*="first"]')
                if await first_name_input.count() > 0:
                    await PlaywrightHelper.human_type(page, 'input[name*="first"], input[id*="first"]', app_data.first_name)
                    
                # 2. Last Name
                last_name_input = page.locator('input[name*="last"], input[id*="last"]')
                if await last_name_input.count() > 0:
                    await PlaywrightHelper.human_type(page, 'input[name*="last"], input[id*="last"]', app_data.last_name)
                    
                # 3. Email
                email_input = page.locator('input[type="email"], input[name*="email"]')
                if await email_input.count() > 0:
                    await PlaywrightHelper.human_type(page, 'input[type="email"], input[name*="email"]', app_data.email)
                    
                # 4. Phone
                phone_input = page.locator('input[type="tel"], input[name*="phone"]')
                if await phone_input.count() > 0:
                    await PlaywrightHelper.human_type(page, 'input[type="tel"], input[name*="phone"]', app_data.phone)
                    
                # 5. Resume Upload
                resume_input = page.locator('input[type="file"][name*="resume"], input[type="file"][id*="resume"]')
                if await resume_input.count() > 0 and os.path.exists(app_data.resume_path):
                    await resume_input.set_input_files(app_data.resume_path)
                    await PlaywrightHelper.human_delay(1000, 2000)
                    
                # 6. Links (LinkedIn/GitHub)
                linkedin_input = page.locator('input[name*="linkedin"], input[name*="url"]')
                if app_data.linkedin and await linkedin_input.count() > 0:
                    await PlaywrightHelper.human_type(page, 'input[name*="linkedin"], input[name*="url"]', app_data.linkedin)
                    
                # 7. Submit. In review mode, stop once the form appears ready.
                submit_btn = page.locator('button[type="submit"], input[type="submit"], button:has-text("Submit Application")')
                if await submit_btn.count() > 0:
                    if submit:
                        await submit_btn.first.click()
                        await PlaywrightHelper.human_delay(2000, 4000)
                        print("Submit button clicked.")
                    else:
                        print("Found submit button. Ready for user-approved submission.")
                    return True
                    
                return False
                
            except Exception as e:
                print(f"Application failed for {job_url}: {e}")
                return False
            finally:
                if context.browser:
                    await context.browser.close()
                else:
                    await context.close()
