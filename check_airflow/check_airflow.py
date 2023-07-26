import logging
from abc import ABC
from abc import abstractmethod
from json import JSONDecodeError
from typing import Tuple, Mapping
import requests
import json


class AirflowRepository(ABC):

    @abstractmethod
    def do_health_check(self, url: str) -> Tuple[int, str]:
        """ This method must be implemented """


class AirflowWebRepository(AirflowRepository):

    def do_health_check(self, url: str) -> Tuple[int, str]:
        try:
            response = requests.get(url, verify=False)
            if response:
                logging.debug(f"Raw response: {response.text}")
                return response.status_code, response.json()
            else:
                return 0, ""
        except ConnectionError:
            return 0, ""


class AirflowHealthCheck:

    def __init__(self, repository: AirflowRepository) -> None:
        self.repository = repository

    def check_health(self, url: str) -> Mapping[str, bool]:
        try:
            (code, json_text) = self.repository.do_health_check(url)
            if code == 200:
                health = json.loads(json_text)
                meta_database_health = health["metadatabase"]["status"] == "healthy"
                scheduler_health = health["scheduler"]["status"] == "healthy"
                return {
                    "metadatabase": meta_database_health,
                    "scheduler": scheduler_health
                }
            else:
                return {
                    "metadatabase": False,
                    "scheduler": False
                }
        except JSONDecodeError:
            logging.error("Invalid JSON response. Maybe the wrong URL?")
            return {
                "metadatabase": False,
                "scheduler": False
            }
