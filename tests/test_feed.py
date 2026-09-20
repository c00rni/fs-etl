import pytest
import feedparser
from src.feed import SecFillingFeed
from src.model import Filling

@pytest.fixture
def rss_feed_url():
    return "https://example.com/rss"

@pytest.fixture
def user_full_name():
    return "john doe"

@pytest.fixture
def user_email():
    return "john.doe@email.com"

@pytest.fixture
def sec_filling_item():
    return {'title': 'Lakewood-Amedex Biotherapeutics Inc. (0002079272) (Filer)',
              'title_detail': {'type': 'text/plain',
                               'language': None,
                               'base': 'https://www.sec.gov/Archives/edgar/usgaap.rss.xml',
                               'value': 'Lakewood-Amedex Biotherapeutics Inc. (0002079272) '
                                        '(Filer)'},
              'links': [{'rel': 'alternate',
                         'type': 'text/html',
                         'href': 'https://www.sec.gov/Archives/edgar/data/2079272/000121390026101512/0001213900-26-101512-index.htm'},
                        {'length': '2612970',
                         'type': 'application/zip',
                         'href': 'https://www.sec.gov/Archives/edgar/data/2079272/000121390026101512/0001213900-26-101512-xbrl.zip',
                         'rel': 'enclosure'}],
              'link': 'https://www.sec.gov/Archives/edgar/data/2079272/000121390026101512/0001213900-26-101512-index.htm',
              'id': 'https://www.sec.gov/Archives/edgar/data/2079272/000121390026101512/0001213900-26-101512-xbrl.zip',
              'guidislink': False,
              'summary': 'S-1',
              'summary_detail': {'type': 'text/html',
                                 'language': None,
                                 'base': 'https://www.sec.gov/Archives/edgar/usgaap.rss.xml',
                                 'value': 'S-1'},
              'published': 'Fri, 18 Sep 2026 17:30:46 EDT',
              'edgar_companyname': 'Lakewood-Amedex Biotherapeutics Inc.',
              'edgar_formtype': 'S-1',
              'edgar_filingdate': '09/18/2026',
              'edgar_ciknumber': '0002079272',
              'edgar_accessionnumber': '0001213900-26-101512',
              'edgar_filenumber': '333-299027',
              'edgar_acceptancedatetime': '20260918173046',
              'edgar_period': '19691231',
              'edgar_assistantdirector': 'Office of Life Sciences',
              'edgar_assignedsic': '2834',
              'edgar_fiscalyearend': '1231',
              'edgar_xbrlfile': {'sequence': '27',
                                 'file': 'ea030580301_ex5-1img2.jpg',
                                 'type': 'graphic',
                                 'size': '28203',
                                 'description': 'GRAPHIC',
                                 'url': 'https://www.sec.gov/Archives/edgar/data/2079272/000121390026101512/ea030580301_ex5-1img2.jpg',
                                 'edgar:sequence': '27',
                                 'edgar:file': 'ea030580301_ex5-1img2.jpg',
                                 'edgar:type': 'GRAPHIC',
                                 'edgar:size': '28203',
                                 'edgar:description': 'GRAPHIC',
                                 'edgar:url': 'https://www.sec.gov/Archives/edgar/data/2079272/000121390026101512/ea030580301_ex5-1img2.jpg'},
              'edgar_xbrlfiles': '',
              'edgar_xbrlfiling': ''}


def test_parser_return_empty_list_for_empty_feed(user_email, user_full_name,rss_feed_url):

    class Http_client_stub:
 
        def parse(self, url, agent):
            return {'entries': []}

    http_client = Http_client_stub()

    feed = SecFillingFeed(user_email, user_full_name, http_client)

    assert feed.extract_fillings(rss_feed_url) == []

def test_extract_items_from_rss_feed(user_email, user_full_name, rss_feed_url, sec_filling_item):

    class Http_client_stub:

        def parse(self, url, agent):
            return {'entries': [sec_filling_item]}

    http_client = Http_client_stub()

    feed = SecFillingFeed(user_full_name, user_email, http_client)

    fillings = feed.extract_fillings(rss_feed_url)

    assert len(fillings) == 1

def test_fetch_passes_user_agent_to_feedparser(mocker, user_email, user_full_name, rss_feed_url):
    mocker.patch.object(feedparser, "parse", return_value={"entries": []})
    spy_parse = mocker.spy(feedparser, "parse")

    feed = SecFillingFeed(user_full_name, user_email)

    feed.extract_fillings(rss_feed_url)

    spy_parse.assert_called_once_with(
        rss_feed_url,
        agent=f"{user_full_name} {user_email}",
    )
