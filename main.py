import sys
import os
import pprint
from dotenv import load_dotenv
import feedparser

load_dotenv()

USER_FULL_NAME = os.getenv('USER_FULL_NAME')
RSS_FEED_URL = os.getenv('RSS_FEED_URL')
USER_EMAIL = os.getenv('USER_EMAIL')

def main():
    d = feedparser.parse(RSS_FEED_URL, agent=f'{RSS_FEED_URL} {USER_EMAIL}')
    pprint.pp(d)
    return 0

if __name__ == '__main__':
    sys.exit(main())
