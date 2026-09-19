import pytest
from src.pipeline import sec_filling_download_pipeline


def test_download_only_unknow_sec_filling():

    class Database_stud:

        def __init__(self, known_fillings: list):
            self._known_fillings = known_fillings

        def filling_is_known(self, unique_identifier: str) -> bool:
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

    unknown_filling_cik_number = "0001294273"
    known_filling_cik_number = "0001534254"

    known_sec_filling = {"cik": known_filling_cik_number}
    unknown_sec_filling = {"cik": unknown_filling_cik_number}

    feed_sec_fillings = [
        known_sec_filling,
        unknown_sec_filling
    ]
    fake_database = Database_stud(known_fillings=[known_sec_filling])
    fake_storage = Storage_stud(set(f'{known_filling_cik_number}.zip'))

    sec_filling_download_pipeline(fake_database, fake_storage, feed_sec_fillings)

    assert fake_storage.contain(unknown_filling_cik_number) == True
    assert fake_database.filling_is_known(unknown_filling_cik_number) == True

