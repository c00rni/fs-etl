import pytest
from src.pipeline import sec_filling_download_pipeline
from src.storage_drivers import FillingDownloadFailed

@pytest.fixture
def unknown_filling_cik_number():
    return "0001294273"

@pytest.fixture
def known_filling_cik_number():
    return "0001534254"

@pytest.fixture
def known_sec_filling(known_filling_cik_number):
    return {"cik": known_filling_cik_number}

@pytest.fixture
def unknown_sec_filling(unknown_filling_cik_number):
    return {"cik": unknown_filling_cik_number}

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

    class Database_stud:

        def __init__(self, known_fillings: list):
            self._known_fillings = known_fillings

        def is_filling_known(self, unique_identifier: str) -> bool:
            for filling in self._known_fillings:
                if filling["cik"] == unique_identifier:
                    return True
            return False

        def insert(self, filling):
            self._known_fillings.append(filling)

    class Storage_stud:

        def __init__(self, file_names: set):
            self._file_names = file_names

        def contain(self, unique_identifier: str) -> bool:
            return f"{unique_identifier}.zip" in self._file_names

        def download(self, filling):
            file_name = f"{filling['cik']}.zip"
            self._file_names.add(file_name)

    fake_database = Database_stud(known_fillings=[known_sec_filling])
    fake_storage = Storage_stud(set(f'{known_filling_cik_number}.zip'))

    sec_filling_download_pipeline(fake_database, fake_storage, feed_sec_fillings_with_unknowns)

    assert fake_storage.contain(unknown_filling_cik_number) == True
    assert fake_database.is_filling_known(unknown_filling_cik_number) == True

def test_filling_stay_unknown_when_download_fail(unknown_filling_cik_number,
                                                 known_filling_cik_number,
                                                 known_sec_filling,
                                                 feed_sec_fillings_with_unknowns):

    class Storage_stud:

        def __init__(self, file_names: set):
            self._file_names = file_names

        def contain(self, unique_identifier: str) -> bool:
            return f"{unique_identifier}.zip" in self._file_names

        def download(self, filling):
            raise FillingDownloadFailed("Failed to download file to the storage.")

    class Database_stud:

        def __init__(self, known_fillings: list):
            self._known_fillings = known_fillings

        def is_filling_known(self, unique_identifier: str) -> bool:
            for filling in self._known_fillings:
                if filling["cik"] == unique_identifier:
                    return True
            return False

        def insert(self, filling):
            self._known_fillings.append(filling)

    fake_database = Database_stud(known_fillings=[known_sec_filling])
    fake_storage = Storage_stud(set(f'{known_filling_cik_number}.zip'))

    sec_filling_download_pipeline(fake_database, fake_storage, feed_sec_fillings_with_unknowns)

    assert fake_storage.contain(unknown_filling_cik_number) == False
    assert fake_database.is_filling_known(unknown_filling_cik_number) == False

def test_execution_continue_when_insertion_fail(unknown_filling_cik_number,
                                                 known_filling_cik_number,
                                                 known_sec_filling,
                                                 feed_sec_fillings_with_unknowns):
    class Storage_stud:

        def __init__(self, file_names: set):
            self._file_names = file_names

        def contain(self, unique_identifier: str) -> bool:
            return f"{unique_identifier}.zip" in self._file_names

        def download(self, filling):
            file_name = f"{filling['cik']}.zip"
            self._file_names.add(file_name)

    class Database_stud:

        def __init__(self, known_fillings: list):
            self._known_fillings = known_fillings

        def is_filling_known(self, unique_identifier: str) -> bool:
            for filling in self._known_fillings:
                if filling["cik"] == unique_identifier:
                    return True
            return False

        def insert(self, filling):
            raise Exception()

    fake_database = Database_stud(known_fillings=[known_sec_filling])
    fake_storage = Storage_stud(set(f'{known_filling_cik_number}.zip'))

    sec_filling_download_pipeline(fake_database, fake_storage, feed_sec_fillings_with_unknowns)

    assert fake_storage.contain(unknown_filling_cik_number) == True
    assert fake_database.is_filling_known(unknown_filling_cik_number) == False
