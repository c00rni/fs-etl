from airflow.providers.mysql.hooks.mysql import MySqlHook
from src.model import Filling
from dataclasses import fields

class MySqlDriver:
    def __init__(self, mysql_conn_id: str):
        self.hook = MySqlHook(mysql_conn_id=mysql_conn_id)
    ''' 
    def ensure_schema(self):
        self.hook.run(
            """
            CREATE TABLE IF NOT EXISTS fillings (
                cik          VARCHAR(20)    NOT NULL,
                title        VARCHAR(512)   NOT NULL,
                form_type    VARCHAR(20)    NOT NULL,
                company_name VARCHAR(255)   NOT NULL,
                link         VARCHAR(2048)  NOT NULL,
                filling_date DATE           NOT NULL,
                PRIMARY KEY (cik)
            )
            """,
            autocommit=True,
        )
    '''

    def insert(self, filling):
        columns = [field.name for field in fields(filling)]

        placeholders = ", ".join(["%s"] * len(columns))
        col_sql = ", ".join(columns)

        values = tuple(getattr(filling, name) for name in columns)

        self.hook.run(
            f"INSERT INTO fillings ({col_sql}) VALUES ({placeholders})",
            parameters=values,
            autocommit=True,
        )

    def is_filling_known(self, filling: Filling) -> bool:

        rows = self.hook.get_records(
            "SELECT 1 FROM fillings WHERE cik = %s",
            parameters=(filling.cik,),
        )

        return len(rows) > 0
