from typing import TypeVar, Generic, Type, Optional
from abc import ABC, abstractmethod
from dataclasses import fields
from airflow.providers.mysql.hooks.mysql import MySqlHook

T = TypeVar('T')
ID = TypeVar('ID')


class AbstractDatabasePort(ABC, Generic[T, ID]):

    @abstractmethod
    def save(self, item: T) -> None:
        pass

    @abstractmethod
    def find_by_id(self, primary_key_name: str, value: ID) -> Optional[T]:
        pass


class MySqlDriver(AbstractDatabasePort[T, ID]):

    def __init__(
        self, 
        mysql_conn_id: str, 
        model_class: Type[T],
    ):
        self.hook = MySqlHook(mysql_conn_id=mysql_conn_id)
        self.model_class = model_class
        self.table_name = self.model_class.__name__.lower()

    def save(self, item: T) -> None:

        columns = [field.name for field in fields(item)]

        placeholders = ", ".join(["%s"] * len(columns))
        col_sql = ", ".join(columns)
        values = tuple(getattr(item, name) for name in columns)

        query = f"INSERT INTO {self.table_name} ({col_sql}) VALUES ({placeholders})"
        
        self.hook.run(
            query,
            parameters=values,
            autocommit=True,
        )

    def find_by_id(self, primary_key_name: str, value: ID) -> Optional[T]:

        query = f"SELECT * FROM {self.table_name} WHERE {primary_key_name} = %s"
        
        rows = self.hook.get_records(
            query,
            parameters=(value,),
        )

        if not rows:
            return None

        field_names = [field.name for field in fields(self.model_class)]
        row_dict = dict(zip(field_names, rows[0]))

        return self.model_class(**row_dict)
