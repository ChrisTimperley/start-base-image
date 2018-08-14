"""
This module is responsible for managing the Docker images used by START.
"""
import os

DIR_DOCKER = os.path.join(os.path.dirname(__file__), '../docker')
DOCKERFILE_BASE = os.path.join(DIR_DOCKER, 'Dockerfile')
DOCKERFILE_SCENARIO = os.path.join(DIR_DOCKER, 'Dockerfile.scenario')


def build_base_image():  # type: () -> None
    raise NotImplementedError


def build_scenario_image():  # type: () -> None
    raise NotImplementedError
