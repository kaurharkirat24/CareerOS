from abc import ABC, abstractmethod
from typing import List
from pydantic import BaseModel

class ScrapedJob(BaseModel):
    title: str
    company: str
    location: str | None = None
    url: str
    description: str
    salary: str | None = None
    source: str

class BaseCrawler(ABC):
    """Abstract base class for all job crawlers."""
    
    @abstractmethod
    async def crawl(self, keyword: str, location: str, max_results: int = 10) -> List[ScrapedJob]:
        """
        Scrape jobs based on keyword and location.
        Returns a list of ScrapedJob objects.
        """
        pass
