import pytest
import io
from src.pipeline import sec_filling_download_pipeline
from src.storage_drivers import FillingWriteFailed, AbstractStoragePort
from src.database_drivers import AbstractDatabasePort
from src.source_adapters import AbstractFillingSourcePort, AbstractHttpClientPort
from datetime import datetime
from src.model import Filling
from typing import BinaryIO

@pytest.fixture
def unknown_filling_cik_number():
    return "0001294273"

@pytest.fixture
def known_filling_cik_number():
    return "0001534254"

@pytest.fixture
def known_sec_filling(known_filling_cik_number):
    return Filling(
        title = "",
        cik =  known_filling_cik_number,
        form_type = "",
        company_name = "",
        link = "",
        filling_date = datetime.today()
    )

@pytest.fixture
def unknown_sec_filling(unknown_filling_cik_number):
    return Filling(
        title = "",
        cik =  unknown_filling_cik_number,
        form_type = "",
        company_name = "",
        link = "",
        filling_date = datetime.today()
    )

@pytest.fixture
def feed_sec_fillings_with_unknowns(unknown_sec_filling, known_sec_filling):
    return [
        known_sec_filling,
        unknown_sec_filling
    ]

def test_download_only_unknow_sec_filling(unknown_filling_cik_number,
                                          known_filling_cik_number,
                                          known_sec_filling,
                                          feed_sec_fillings_with_unknowns):

    class Database_driver_stub(AbstractDatabasePort):

        def __init__(self, known_fillings: list):
            self._known_fillings = known_fillings

        def find_by_id(self, primary_key_name: str, value):
            for filling in self._known_fillings:
                if filling.cik == value:
                    return {'cik': value}
            return None

        def save(self, item):
            self._known_fillings.append(item)

    class Storage_driver_stub(AbstractStoragePort):

        def __init__(self, file_names: set):
            self._file_names = file_names

        def exists(self, path: str) -> bool:
            return path in self._file_names

        def write(self, stream: BinaryIO, destination: str):
            self._file_names.add(destination)

    class Rss_feed_adapter_stub(AbstractFillingSourcePort):

        def __init__(self, rss_feed_url: str):
            self._rss_feed_url = rss_feed_url

        def get_fillings(self) -> list:
            return feed_sec_fillings_with_unknowns

    class Http_client_adapter_stub(AbstractHttpClientPort):

        def download(self, url) -> BinaryIO:
            return io.BytesIO()


    fake_database = Database_driver_stub(known_fillings=[known_sec_filling])
    fake_storage = Storage_driver_stub(set(f'{known_filling_cik_number}.zip'))
    fake_source = Rss_feed_adapter_stub('https://rss-feed-com/rss')
    fake_http_client = Http_client_adapter_stub()

    sec_filling_download_pipeline(fake_database, fake_storage, fake_source, fake_http_client)

    assert fake_storage.exists(f"{unknown_filling_cik_number}.zip") == True
    assert fake_database.find_by_id('cik', unknown_filling_cik_number)

def test_filling_stay_unknown_when_write_fail(unknown_filling_cik_number,
                                                 known_filling_cik_number,
                                                 known_sec_filling,
                                                 feed_sec_fillings_with_unknowns):

    class Database_driver_stub(AbstractDatabasePort):

        def __init__(self, known_fillings: list):
            self._known_fillings = known_fillings

        def find_by_id(self, primary_key_name: str, value):
            for filling in self._known_fillings:
                if filling.cik == value:
                    return {'cik': value}
            return None

        def save(self, item):
            self._known_fillings.append(item)

    class Storage_driver_stub(AbstractStoragePort):

        def __init__(self, file_names: set):
            self._file_names = file_names

        def exists(self, path: str) -> bool:
            return path in self._file_names

        def write(self, stream: BinaryIO, destination: str):
            raise FillingWriteFailed("Failed to write file to the storage.")

    class Rss_feed_adapter_stub(AbstractFillingSourcePort):

        def __init__(self, rss_feed_url: str):
            self._rss_feed_url = rss_feed_url

        def get_fillings(self) -> list:
            return feed_sec_fillings_with_unknowns

    class Http_client_adapter_stub(AbstractHttpClientPort):

        def download(self, url) -> BinaryIO:
            return io.BytesIO()

    fake_database = Database_driver_stub(known_fillings=[known_sec_filling])
    fake_storage = Storage_driver_stub(set(f'{known_filling_cik_number}.zip'))
    fake_source = Rss_feed_adapter_stub('https://rss-feed-com/rss')
    fake_http_client = Http_client_adapter_stub()

    sec_filling_download_pipeline(fake_database, fake_storage, fake_source, fake_http_client)

    assert fake_storage.exists(f"{unknown_filling_cik_number}.zip") == False
    assert fake_database.find_by_id('cik',unknown_filling_cik_number) == None

def test_execution_continue_when_insertion_fail(unknown_filling_cik_number,
                                                 known_filling_cik_number,
                                                 known_sec_filling,
                                                 feed_sec_fillings_with_unknowns):

    class Database_driver_stub(AbstractDatabasePort):

        def __init__(self, known_fillings: list):
            self._known_fillings = known_fillings

        def find_by_id(self, primary_key_name: str, value):
            for filling in self._known_fillings:
                if filling.cik == value:
                    return {'cik': value}
            return None

        def save(self, item):
            raise Exception()

    class Storage_driver_stub(AbstractStoragePort):

        def __init__(self, file_names: set):
            self._file_names = file_names

        def exists(self, path: str) -> bool:
            return path in self._file_names

        def write(self, stream: BinaryIO, destination: str):
            self._file_names.add(destination)

    class Rss_feed_adapter_stub(AbstractFillingSourcePort):
        
        def __init__(self, rss_feed_url: str):
            self._rss_feed_url = rss_feed_url

        def get_fillings(self) -> list:
            return feed_sec_fillings_with_unknowns

    class Http_client_adapter_stub(AbstractHttpClientPort):

        def download(self, url) -> BinaryIO:
            return io.BytesIO()

    fake_database = Database_driver_stub(known_fillings=[known_sec_filling])
    fake_storage = Storage_driver_stub(set(f'{known_filling_cik_number}.zip'))
    fake_source = Rss_feed_adapter_stub('https://rss-feed-com/rss')
    fake_http_client = Http_client_adapter_stub()

    sec_filling_download_pipeline(fake_database, fake_storage, fake_source, fake_http_client)

    assert fake_storage.exists(f"{unknown_filling_cik_number}.zip") == True
    assert fake_database.find_by_id('cik', unknown_filling_cik_number) == None
