import argparse
import subprocess
import os
import logging
from typing import Any
from check_airflow import AirflowHealthCheck, AirflowWebRepository


def main():
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(
        description="Check airflow health and restart the scheduler if required.")
    parser.add_argument("-u", "--url", type=str,
                        help="The airflow health endpoint url.", required=True)
    parser.add_argument("-c", "--command",
                        nargs="+",
                        help="The restart command for the scheduler service. "
                             'Example: -c "restart" "now"',
                        default=["sysctl", "restart", "airflow"])
    args = parser.parse_args()
    run_checker(args)


def run_checker(args: Any):
    checker = AirflowHealthCheck(AirflowWebRepository())
    logging.info(f"Checking health at {args.url}")
    results = checker.check_health(args.url)
    logging.info(f"Got results: {results}")
    if not results["scheduler"]:
        logging.info(f"Executing command: {args.command}")
        proc = subprocess.run(args.command, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              universal_newlines=True, env=os.environ.copy())
        if proc.returncode != 0:
            logging.error(f"Restarting scheduler failed with: {proc.stderr}")
            print(proc.stdout)
            exit(proc.returncode)
    exit(0)


if __name__ == "__main__":
    main()
