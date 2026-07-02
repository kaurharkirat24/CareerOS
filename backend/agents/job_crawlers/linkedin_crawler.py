import urllib.parse
from typing import List
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from backend.agents.job_crawlers.base_crawler import BaseCrawler, ScrapedJob
from backend.utils.playwright_helper import PlaywrightHelper

class LinkedInCrawler(BaseCrawler):
    """Crawler for LinkedIn public job listings."""
    
    async def crawl(self, keyword: str, location: str, max_results: int = 10) -> List[ScrapedJob]:
        jobs = []
        encoded_keyword = urllib.parse.quote(keyword)
        encoded_location = urllib.parse.quote(location)
        
        # Public LinkedIn jobs search URL
        url = f"https://www.linkedin.com/jobs/search?keywords={encoded_keyword}&location={encoded_location}&f_TPR=r86400"
        
        async with async_playwright() as p:
            context = await PlaywrightHelper.create_browser_context(p, headless=True)
            page = await context.new_page()
            
            try:
                await page.goto(url, wait_until="domcontentloaded")
                await PlaywrightHelper.human_delay(2000, 4000) # Wait for initial load
                
                # Scroll a bit to trigger lazy loading if needed
                for _ in range(3):
                    await page.mouse.wheel(0, 1000)
                    await PlaywrightHelper.human_delay(500, 1500)
                
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                job_cards = soup.find_all('div', class_='base-card')
                
                for card in job_cards[:max_results]:
                    try:
                        title_elem = card.find('h3', class_='base-search-card__title')
                        company_elem = card.find('h4', class_='base-search-card__subtitle')
                        location_elem = card.find('span', class_='job-search-card__location')
                        link_elem = card.find('a', class_='base-card__full-link')
                        
                        if not all([title_elem, company_elem, link_elem]):
                            continue
                            
                        title = title_elem.get_text(strip=True)
                        company = company_elem.get_text(strip=True)
                        loc = location_elem.get_text(strip=True) if location_elem else None
                        job_url = link_elem.get('href', '')
                        
                        # Clean up URL (remove tracking params)
                        if '?' in job_url:
                            job_url = job_url.split('?')[0]
                            
                        jobs.append(ScrapedJob(
                            title=title,
                            company=company,
                            location=loc,
                            url=job_url,
                            description="Description fetched on demand.", # We can fetch full JD later if needed
                            source="LinkedIn"
                        ))
                    except Exception as e:
                        print(f"Error parsing LinkedIn job card: {e}")
                        continue
                        
            except Exception as e:
                print(f"Failed to crawl LinkedIn: {e}")
            finally:
                if context.browser:
                    await context.browser.close()
                else:
                    await context.close()
                
        return jobs
