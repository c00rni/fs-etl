from src.rss import extract_rss, FailedRssExtraction
import pytest

@pytest.fixture
def rss_feed_url():
    return "https://example.com/rss"

@pytest.fixture
def user_full_name():
    return "john doe"

@pytest.fixture
def user_email():
    return "john.doe@email.com"

def test_rss_channel_successfully_extracted(
        requests_mock,
        rss_feed_url,
        user_full_name,
        user_email):

    expected_rss_content = 'raw data'

    requests_mock.get(rss_feed_url, text=expected_rss_content)

    raw_rss_feed = extract_rss(rss_feed_url, user_full_name, user_email) 

    assert raw_rss_feed == expected_rss_content

def test_failed_to_extract_rss_feed(
        requests_mock,
        rss_feed_url,
        user_full_name,
        user_email):

    requests_mock.get(rss_feed_url, status_code=403)

    with pytest.raises(FailedRssExtraction):
        extract_rss(rss_feed_url, user_full_name, user_email) 

def test_url_required_at_extraction(
        requests_mock,
        user_full_name,
        user_email):

    requests_mock.get(rss_feed_url, text='')

    with pytest.raises(ValueError):
        extract_rss('', user_full_name, user_email) 

def test_full_name_required_at_extraction(
        requests_mock,
        rss_feed_url,
        user_email):

    requests_mock.get(rss_feed_url, text='')

    with pytest.raises(ValueError):
        extract_rss(rss_feed_url, '', user_email) 

def test_email_required_at_extraction(
        requests_mock,
        rss_feed_url,
        user_full_name):

    requests_mock.get(rss_feed_url, text='')

    with pytest.raises(ValueError):
        extract_rss(rss_feed_url, user_full_name, '') 
