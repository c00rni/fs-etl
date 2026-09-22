from typing import BinaryIO
from abc import ABC, abstractmethod
from pathlib import Path
import shutil

class AbstractStoragePort(ABC):

    @abstractmethod
    def exists(self, path: str) -> bool:
        pass

    @abstractmethod
    def write(self, stream: BinaryIO, destination: str):
        pass

class FillingWriteFailed(Exception):
    pass

class LocalStorageDriver(AbstractStoragePort):

    def __init__(self, base_path: str ):
        self.base_path = Path(base_path).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)

    def exists(self, path: str) -> bool:
        full_path = self._resolve_path(path)
        return full_path.exists()

    def write(self, stream: BinaryIO, destination: str):
        full_path = self._resolve_path(destination)

        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "wb") as f:
            shutil.copyfileobj(stream, f)

    def _resolve_path(self, relative_path: str) -> Path:
        """
        Safely joins the base path with the user-provided path,
        preventing path traversal attacks.
        """
        clean_path = relative_path.lstrip("/\\")

        full_path = (self.base_path / clean_path).resolve()

        if not str(full_path).startswith(str(self.base_path)):
            raise ValueError(f"Security Error: Path traversal detected in '{relative_path}'")

        return full_path
