from testcontainers.community.mysql import MySqlContainer
from airflow.providers.mysql.hooks.mysql import MySqlHook
import src.database_drivers as db_driver
from dataclasses import fields
from datetime import date
from src.model import Filling
import pytest

@pytest.fixture(scope='session')
def mysql_container():
    with MySqlContainer("mysql:8.0") as mysql:
        yield mysql

@pytest.fixture
def known_filling_cik_number():
    return "0001534254"

@pytest.fixture
def mysql_conn_id(mysql_container, monkeypatch):
    host = mysql_container.get_container_host_ip()
    if host == "localhost":
        host = "127.0.0.1"

    conn_uri = (
        f"mysql://{mysql_container.username}:{mysql_container.password}"
        f"@{host}:{mysql_container.get_exposed_port(3306)}"
        f"/{mysql_container.dbname}"
    )
    monkeypatch.setenv("AIRFLOW_CONN_TEST_MYSQL", conn_uri)
    return "test_mysql"

@pytest.fixture
def mysql_hook(mysql_conn_id):
    return MySqlHook(mysql_conn_id=mysql_conn_id)

def ensure_schema(hook):
    hook.run(
        """
        CREATE TABLE IF NOT EXISTS fillings (
            cik VARCHAR(20) PRIMARY KEY,
            title VARCHAR(255),
            form_type VARCHAR(20),
            company_name VARCHAR(255),
            link VARCHAR(500),
            filling_date DATE
        )
        """,
        autocommit=True,
    )

@pytest.fixture(autouse=True)
def clean_fillings_table(mysql_hook):
    ensure_schema(mysql_hook)
    yield
    mysql_hook.run("TRUNCATE TABLE fillings", autocommit=True)

@pytest.fixture
def known_filling(known_filling_cik_number):
    return Filling(
        title = "Known company s-8 filling",
        cik = known_filling_cik_number,
        form_type = "s-8",
        company_name = "Known company SA",
        link = f"https://known-company.com/{known_filling_cik_number}.zip",
        filling_date = date.today()
    )

def insert_in_table(hook, filling):

    columns = [f.name for f in fields(filling)]
    placeholders = ", ".join(["%s"] * len(columns))
    col_sql = ", ".join(columns)
    values = tuple(getattr(filling, name) for name in columns)
    hook.run(
        f"INSERT INTO fillings ({col_sql}) VALUES ({placeholders})",
        parameters=values,
        autocommit=True,
    )

@pytest.fixture
def driver(mysql_conn_id):
    return db_driver.MySqlDriver(mysql_conn_id=mysql_conn_id)

def test_database_driver_successful_insertion(driver, mysql_conn_id, known_filling):
    driver.insert(known_filling)

    # Verify independently — a fresh hook, raw SQL
    verifier = MySqlHook(mysql_conn_id=mysql_conn_id)
    row = verifier.get_first(
        "SELECT cik FROM fillings WHERE cik = %s",
        parameters=(known_filling.cik,),
    )
    assert row == (known_filling.cik,)

def test_insert_raises_on_duplicate(driver, mysql_hook, mysql_conn_id, known_filling):
    insert_in_table(mysql_hook, known_filling)


    with pytest.raises(Exception):
        driver.insert(known_filling_in_db)

def test_is_filling_known_returns_true_when_filling_is_known(driver, mysql_hook, known_filling):
    insert_in_table(mysql_hook, known_filling)

    assert driver.is_filling_known(known_filling) is True


def test_is_filling_known_returns_false_when_filling_unknown(driver, known_filling):

    unknown_filling = known_filling
    assert driver.is_filling_known(unknown_filling) is False
