from abc import ABC, abstractmethod
from typing import BinaryIO
from typing import List
from src.model import Filling
import requests

class AbstractFillingSourcePort(ABC):

    @abstractmethod
    def get_fillings(self) -> List[Filling]:
        """
        Retrieves a list of Filling objects from the source.
        """
        pass

class AbstractHttpClientPort(ABC):

    @abstractmethod
    def download(self, url) -> BinaryIO:
        pass

class RequestAdapter(AbstractHttpClientPort):

    def __init__(self, user_agent: str):
        self._user_agent = user_agent

    def download(self, url) -> BinaryIO:
        headers = {'User-Agent': self._user_agent}
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()

        return response.raw

