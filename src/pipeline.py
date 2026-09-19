def sec_filling_download_pipeline(database_driver, storage_driver, sec_fillings):

    for filling in sec_fillings:
        cik_number = filling["cik"]

        if not database_driver.filling_is_known(cik_number):
            storage_driver.download(filling)
            database_driver.insert(filling)

