import unittest
from typing import Tuple

from check_airflow.check_airflow import AirflowRepository, AirflowHealthCheck


class NetworkDeadRepos(AirflowRepository):

    def do_health_check(self, url: str) -> Tuple[int, str]:
        return 0, ""


class BadResponseRepos(AirflowRepository):

    def do_health_check(self, url: str) -> Tuple[int, str]:
        return 500, ""


class MalformedJsonRepos(AirflowRepository):

    def do_health_check(self, url: str) -> Tuple[int, str]:
        return 200, "{7s"


class SchedulerDownRepos(AirflowRepository):

    def do_health_check(self, url: str) -> Tuple[int, str]:
        return 200, """{
    "metadatabase": {
        "status": "healthy"
    },
    "scheduler": {
        "status": "unhealthy",
        "latest_scheduler_heartbeat": "2023-07-25T03:50:05.304982+00:00"
    }
}"""


class MetaDataDownRepos(AirflowRepository):

    def do_health_check(self, url: str) -> Tuple[int, str]:
        return 200, """{
    "metadatabase": {
        "status": "unhealthy"
    },
    "scheduler": {
        "status": "healthy",
        "latest_scheduler_heartbeat": "2023-07-25T03:50:05.304982+00:00"
    }
}"""


class BothDownRepos(AirflowRepository):

    def do_health_check(self, url: str) -> Tuple[int, str]:
        return 200, """{
    "metadatabase": {
        "status": "unhealthy"
    },
    "scheduler": {
        "status": "unhealthy",
        "latest_scheduler_heartbeat": "2023-07-25T03:50:05.304982+00:00"
    }
}"""


class CheckAirflowTests(unittest.TestCase):

    def test_dead_network_path(self):
        hc = AirflowHealthCheck(NetworkDeadRepos())
        health = hc.check_health("url")
        expected = {
            "metadatabase": False,
            "scheduler": False
        }
        self.assertDictEqual(health, expected)

    def test_bad_response(self):
        hc = AirflowHealthCheck(BadResponseRepos())
        health = hc.check_health("url")
        expected = {
            "metadatabase": False,
            "scheduler": False
        }
        self.assertDictEqual(health, expected)

    def test_metadata_down(self):
        hc = AirflowHealthCheck(MetaDataDownRepos())
        health = hc.check_health("url")
        expected = {
            "metadatabase": False,
            "scheduler": True
        }
        self.assertDictEqual(health, expected)

    def test_scheduler_down(self):
        hc = AirflowHealthCheck(SchedulerDownRepos())
        health = hc.check_health("url")
        expected = {
            "metadatabase": True,
            "scheduler": False
        }
        self.assertDictEqual(health, expected)

    def test_both_down(self):
        hc = AirflowHealthCheck(BothDownRepos())
        health = hc.check_health("url")
        expected = {
            "metadatabase": False,
            "scheduler": False
        }
        self.assertDictEqual(health, expected)

    def test_malformed_json(self):
        hc = AirflowHealthCheck(MalformedJsonRepos())
        health = hc.check_health("url")
        expected = {
            "metadatabase": False,
            "scheduler": False
        }
        self.assertDictEqual(health, expected)
