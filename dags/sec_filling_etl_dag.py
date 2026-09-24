# ── Path setup — MUST come before any `src` imports ─────────────
from airflow.sdk import Variable
from datetime import datetime, timedelta

# Airflow 3.0 SDK imports
from airflow.sdk import dag, task
from airflow.providers.mysql.hooks.mysql import MySqlHook

# Your application imports
from src.pipeline import sec_filling_download_pipeline
from src.database_drivers import MySqlDriver
from src.storage_drivers import LocalStorageDriver
from src.source_adapters import RequestAdapter, SecFillingFeed
from src.model import Filling


# --- Configuration ---
MYSQL_CONN_ID = "my_local_mysql"

@dag(
    dag_id="sec_filling_etl_dag",
    description="Create the DB/table if missing, then run the SEC filling ETL pipeline.",
    schedule="*/10 * * * *",
    start_date=datetime(2026, 9, 1),
    catchup=False,
    default_args={
        "owner": "data-team",
        "retries": 2,
        "retry_delay": timedelta(minutes=1),
    },
    tags=["etl", "sec", "filling"],
)
def sec_filling_etl():

    @task
    def run_etl_pipeline() -> None:
        """Instantiate drivers and launch the SEC filling download pipeline."""

        user_full_name = Variable.get("USER_FULL_NAME")
        rss_feed_url = Variable.get("RSS_FEED_URL")
        user_email = Variable.get("USER_EMAIL")
        staging_dir = Variable.get("STAGING_DIR")

        sec_filling_download_pipeline(
            database_driver=MySqlDriver(
                MYSQL_CONN_ID, model_class=Filling
            ),
            storage_driver=LocalStorageDriver(staging_dir),
            sec_fillings=SecFillingFeed(
                rss_feed_url, user_full_name, user_email
            ),
            http_client_adapter=RequestAdapter(f"{user_full_name} {user_email}"),
        )

    #create_database_and_table() >> run_etl_pipeline()
    run_etl_pipeline()


sec_filling_etl()
