from src.storage_drivers import FillingWriteFailed, AbstractStoragePort
from src.database_drivers import AbstractDatabasePort
from src.source_adapters import AbstractFillingSourcePort, AbstractHttpClientPort

def sec_filling_download_pipeline(database_driver: AbstractDatabasePort,
                                  storage_driver: AbstractStoragePort,
                                  sec_fillings: AbstractFillingSourcePort,
                                  http_client_adapter: AbstractHttpClientPort):

    for filling in sec_fillings.get_fillings():

       if not database_driver.find_by_id('cik', filling.cik):
            try:

                file_stream = http_client_adapter.download(url=filling.link)
                storage_driver.write(file_stream, f"{filling.cik}.zip")

                # Continue to the other fillings if the insertion fail
                try:
                    database_driver.save(filling)
                except:
                    continue
            except FillingWriteFailed as e:
                print(e)


