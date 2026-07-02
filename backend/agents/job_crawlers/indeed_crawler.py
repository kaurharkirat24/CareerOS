import urllib.parse
from typing import List
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from backend.agents.job_crawlers.base_crawler import BaseCrawler, ScrapedJob
from backend.utils.playwright_helper import PlaywrightHelper

class IndeedCrawler(BaseCrawler):
    """Crawler for Indeed job listings."""
    
    async def crawl(self, keyword: str, location: str, max_results: int = 10) -> List[ScrapedJob]:
        jobs = []
        encoded_keyword = urllib.parse.quote(keyword)
        encoded_location = urllib.parse.quote(location)
        
        # Indeed search URL
        url = f"https://www.indeed.com/jobs?q={encoded_keyword}&l={encoded_location}&sort=date"
        
        async with async_playwright() as p:
            context = await PlaywrightHelper.create_browser_context(p, headless=True)
            page = await context.new_page()
            
            try:
                await page.goto(url, wait_until="domcontentloaded")
                await PlaywrightHelper.human_delay(2000, 4000) # Wait for anti-bot checks if any
                
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Indeed job cards usually have class 'job_seen_beacon' or similar
                job_cards = soup.find_all('div', class_='job_seen_beacon')
                
                for card in job_cards[:max_results]:
                    try:
                        title_elem = card.find('h2', class_='jobTitle')
                        company_elem = card.find('span', class_='companyName') or card.find('span', {'data-testid': 'company-name'})
                        location_elem = card.find('div', class_='companyLocation') or card.find('div', {'data-testid': 'text-location'})
                        
                        if not title_elem:
                            continue
                            
                        # Extract link
                        link_elem = title_elem.find('a')
                        job_url = "https://www.indeed.com" + link_elem.get('href', '') if link_elem else ""
                        title = title_elem.get_text(strip=True)
                        company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
                        loc = location_elem.get_text(strip=True) if location_elem else None
                        
                        # Remove tracking from url if possible
                        if '&vjs=' in job_url:
                            job_url = job_url.split('&vjs=')[0]
                            
                        jobs.append(ScrapedJob(
                            title=title,
                            company=company,
                            location=loc,
                            url=job_url,
                            description="Description fetched on demand.",
                            source="Indeed"
                        ))
                    except Exception as e:
                        print(f"Error parsing Indeed job card: {e}")
                        continue
                        
            except Exception as e:
                print(f"Failed to crawl Indeed: {e}")
            finally:
                if context.browser:
                    await context.browser.close()
                else:
                    await context.close()
                
        return jobs
