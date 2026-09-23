# ── Path setup — MUST come before any `src` imports ─────────────
import sys
from pathlib import Path
from airflow.sdk import Variable

# Project root = parent of this `dags/` folder
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

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
DATABASE_NAME = "sec_fillings_db"
TABLE_NAME = "filling"
STAGING_DIR = "/opt/airflow/staging"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS filling (
    cik VARCHAR(20) PRIMARY KEY,
    title VARCHAR(255),
    form_type VARCHAR(20),
    company_name VARCHAR(255),
    link VARCHAR(500),
    filling_date DATE
)
"""


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
    def create_database_and_table() -> None:
        """Idempotently create the database and table if they don't exist."""
        # Connect to the server (no schema required for CREATE DATABASE)
        hook = MySqlHook(mysql_conn_id=MYSQL_CONN_ID)
        hook.run(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}")
        print(f"Database '{DATABASE_NAME}' is ready.")

        # Connect specifically to the target schema for the table creation
        hook = MySqlHook(mysql_conn_id=MYSQL_CONN_ID, schema=DATABASE_NAME)
        hook.run(CREATE_TABLE_SQL)
        print(f"Table '{TABLE_NAME}' is ready in '{DATABASE_NAME}'.")

    @task
    def run_etl_pipeline() -> None:
        """Instantiate drivers and launch the SEC filling download pipeline."""
        user_full_name = Variable.get("USER_FULL_NAME")
        rss_feed_url = Variable.get("RSS_FEED_URL")
        user_email = Variable.get("USER_EMAIL")

        sec_filling_download_pipeline(
            database_driver=MySqlDriver(
                MYSQL_CONN_ID, model_class=Filling
            ),
            storage_driver=LocalStorageDriver(STAGING_DIR),
            sec_fillings=SecFillingFeed(
                rss_feed_url, user_full_name, user_email
            ),
            http_client_adapter=RequestAdapter(f"{user_full_name} {user_email}"),
        )

    create_database_and_table() >> run_etl_pipeline()


sec_filling_etl()
