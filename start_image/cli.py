"""
This module provides a simple command-line interface for managing START's
Docker images.
"""
import argparse
import os
import logging

from start_core.scenario import Scenario
from start_core.exceptions import STARTException

from .build import build_base_image, build_scenario_image

logger = logging.getLogger(__name__)  # type: logging.Logger
logger.setLevel(logging.DEBUG)

DESCRIPTION = """
START [Image Manager]
""".strip()


def main():  # type: () -> None
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    subparsers = parser.add_subparsers()

    cmd = subparsers.add_parser(
        'build',
        help='builds the Docker image for a given scenario.')
    def build_image(args):
        logger.info("loading scenario from file [%s]", args.filename)
        scenario = Scenario.from_file(args.filename)
        logger.info("building image for scenario [%s]", scenario.name)
        build_scenario_image(scenario)
        logger.info("built image for scenario [%s]", scenario.name)
    cmd.set_defaults(func=build_image)
    cmd.add_argument('filename',
                     help="the path to the scenario's configuration file.")
    cmd.add_argument('debug',
                     help="prints debugging information to the stdout.",
                     action='store_true')

    log_to_stdout_formatter = logging.Formatter(
        '%(asctime)s:%(levelname)s: %(message)s',
        '%Y-%m-%d %H:%M:%S')
    log_to_stdout = logging.StreamHandler()
    log_to_stdout.setLevel(logging.INFO)
    log_to_stdout.setFormatter(log_to_stdout_formatter)
    logging.getLogger('start_image').addHandler(log_to_stdout)

    try:
        args = parser.parse_args()
        if args.debug:
            log_to_stdout.setLevel(logging.DEBUG)
        args.func(args)
    except STARTException as e:
        logger.exception("An error occurred during command execution: %s", e)
    except:
        logger.exception("An unexpected error occurred during command execution.")
        raise
