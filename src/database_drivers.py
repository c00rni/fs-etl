from abc import ABC, abstractmethod
from dataclasses import fields
from typing import TypeVar, Generic, Type, Optional, Protocol
from airflow.providers.mysql.hooks.mysql import MySqlHook
from src.model import Filling


# 1. Define the Protocol that matches what a dataclass looks like
class DataclassInstance(Protocol):
    __dataclass_fields__: dict


# 2. Bind T to that Protocol
T = TypeVar('T', bound=DataclassInstance)
ID = TypeVar('ID')


class AbstractDatabasePort(ABC, Generic[T, ID]):
    @abstractmethod
    def save(self, item: T) -> None:
        pass

    @abstractmethod
    def find_by_id(self, primary_key_name: str, value: ID) -> bool:
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
        self._allowed_columns = {field.name for field in fields(model_class)}

    def save(self, item: T) -> None:
        columns = [field.name for field in fields(item)]
        placeholders = ", ".join(["%s"] * len(columns))
        col_sql = ", ".join(columns)
        values = tuple(getattr(item, name) for name in columns)

        query = f"INSERT INTO {self.table_name} ({col_sql}) VALUES ({placeholders})"

        with self.hook.get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, values)
                conn.commit()

    def find_by_id(self, primary_key_name: str, value: ID) -> bool:
        if primary_key_name not in self._allowed_columns:
            raise ValueError(f"Invalid column name: {primary_key_name}")

        query = f"SELECT 1 FROM {self.table_name} WHERE {primary_key_name} = %s LIMIT 1"
        row = self.hook.get_first(query, parameters=(value,))
        return row is not None
