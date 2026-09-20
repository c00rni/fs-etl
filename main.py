import sys
import os
import pprint
from dotenv import load_dotenv
from src.feed import SecFillingFeed

load_dotenv()

USER_FULL_NAME = os.getenv('USER_FULL_NAME')
RSS_FEED_URL = os.getenv('RSS_FEED_URL')
USER_EMAIL = os.getenv('USER_EMAIL')

def main():
    feed = SecFillingFeed(USER_FULL_NAME, USER_EMAIL)
    fillings = feed.extract_fillings(RSS_FEED_URL)
    pprint.pp(fillings)
    return 0

if __name__ == '__main__':
    sys.exit(main())
