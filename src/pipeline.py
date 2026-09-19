from src.storage_drivers import FillingDownloadFailed

def sec_filling_download_pipeline(database_driver, storage_driver, sec_fillings):

    for filling in sec_fillings:
        cik_number = filling["cik"]

        if not database_driver.is_filling_known(cik_number):
            try:
                storage_driver.download(filling)

                # Continue to the other fillings if the insertion fail
                try:
                    database_driver.insert(filling)
                except:
                    continue
            except FillingDownloadFailed as e:
                print(e)


