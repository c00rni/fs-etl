import sys
import os
import pprint
from dotenv import load_dotenv
from src.pipeline import sec_filling_download_pipeline
from src.database_drivers import MySqlDriver
from src.storage_drivers import LocalStorageDriver
from src.source_adapters import RequestAdapter, SecFillingFeed
from src.model import Filling

load_dotenv()

USER_FULL_NAME = os.getenv('USER_FULL_NAME', "")
RSS_FEED_URL = os.getenv('RSS_FEED_URL', "")
USER_EMAIL = os.getenv('USER_EMAIL', "")

def main():
    sec_filling_download_pipeline(
       database_driver = MySqlDriver("my_local_mysql", model_class=Filling),
       storage_driver = LocalStorageDriver("./tmp"),
       sec_fillings = SecFillingFeed(RSS_FEED_URL, USER_FULL_NAME, USER_EMAIL), 
       http_client_adapter = RequestAdapter(f"{USER_FULL_NAME} {USER_EMAIL}")
    )
    return 0

if __name__ == '__main__':
    sys.exit(main())
