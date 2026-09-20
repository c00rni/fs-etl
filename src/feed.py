import feedparser
from src.model import Filling

class SecFillingFeed:

    def __init__(self, user_full_name: str, user_email: str, http_client=None):
        self._http_client = http_client or feedparser
        self._user_agent = f"{user_full_name} {user_email}"

    def extract_fillings(self, rss_feed_url: str):
        feed = self._http_client.parse(rss_feed_url, agent=self._user_agent)
        feed_items = feed.get("entries", [])

        fillings = []

        for item in feed_items:
            title = item.get("title","")
            cik = item.get("edgar_ciknumber","")
            company_name = item.get("edgar_companyname","")
            form_type = item.get("edgar_formtype","")
            link = item.get("link",""),
            filling_date = item.get("edgar_filingdate","")

            if not cik or not link:
                continue

            filling = Filling(title, cik, company_name, form_type, link, filling_date)

            fillings.append(filling)

        return fillings


class FailedRssExtraction(Exception):
    pass


