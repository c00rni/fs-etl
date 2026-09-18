import sys
import os
from src.rss import extract_rss
from dotenv import load_dotenv

load_dotenv()

USER_FULL_NAME = os.getenv('USER_FULL_NAME')
RSS_FEED_URL = os.getenv('RSS_FEED_URL')
USER_EMAIL = os.getenv('USER_EMAIL')

def main():
    response = extract_rss(
        RSS_FEED_URL,
        USER_FULL_NAME,
        USER_EMAIL
    )
    print(response)
    return 0

if __name__ == '__main__':
    sys.exit(main())
