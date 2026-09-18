import requests

def extract_rss(rss_url: str, user_full_name: str, user_email: str) -> str:
    if not rss_url:
        raise ValueError("The rss feed url is required.")
    if not user_full_name:
        raise ValueError("The user name is required.")
    if not user_email:
        raise ValueError("The user contact email is required.")

    headers = {'User-Agent': f'{user_full_name} {user_email}'}

    response = requests.get(rss_url, headers=headers)
    if response.status_code != 200:
        raise FailedRssExtraction()

    return response.text

class FailedRssExtraction(Exception):
    pass

def test_email_required_at_extraction(
        requests_mock,
        rss_feed_url,
        user_full_name):

    requests_mock.get(rss_feed_url, text='')

    with pytest.raises(ValueError):
        extract_rss(rss_feed_url, user_full_name, '') 

