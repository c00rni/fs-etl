from abc import ABC, abstractmethod
from typing import BinaryIO
from typing import List
from src.model import Filling
import requests
import feedparser
from src.model import Filling
from datetime import datetime, date

class AbstractFillingSourcePort(ABC):

    @abstractmethod
    def get_fillings(self) -> List[Filling]:
        """
        Retrieves a list of Filling objects from the source.
        """
        pass

class AbstractHttpClientPort(ABC):

    @abstractmethod
    def download(self, url) -> BinaryIO:
        pass

class RequestAdapter(AbstractHttpClientPort):

    def __init__(self, user_agent: str):
        self._user_agent = user_agent

    def download(self, url) -> BinaryIO:
        headers = {'User-Agent': self._user_agent}
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()

        return response.raw

class SecFillingFeed(AbstractFillingSourcePort):

    def __init__(self, rss_feed_url: str, user_full_name: str, user_email: str):
        self._user_agent = f"{user_full_name} {user_email}"
        self.rss_feed_url = rss_feed_url

    def get_fillings(self):
        feed = feedparser.parse(self.rss_feed_url, agent=self._user_agent)
        feed_items = feed.get("entries", [])

        fillings = []

        for item in feed_items:
            title = item.get("title","")
            cik = item.get("edgar_ciknumber","")
            company_name = item.get("edgar_companyname","")
            form_type = item.get("edgar_formtype","")
            link = item.get("guid")
            if isinstance(link, (tuple, list)):
                link = link[0]
            filling_date = datetime.strptime(
                    item.get("edgar_filingdate", date.today().strftime("%m/%d/%Y")),
                    "%m/%d/%Y"
            ).date()

            if not cik or not link:
                continue

            filling = Filling(title, cik, company_name, form_type, link, filling_date)

            fillings.append(filling)

        return fillings

