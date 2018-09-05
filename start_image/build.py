"""
This module is responsible for managing the Docker images used by START.
"""
__all__ = ['build_base_image', 'build_scenario_image']

import os
import logging
import tempfile
import shutil

import docker
from docker import DockerClient

from start_core.scenario import Scenario

from .name import BASE_IMAGE_NAME
from .name import name as image_name

logger = logging.getLogger(__name__)   # type: logging.Logger
logger.setLevel(logging.DEBUG)

DIR_DOCKER = os.path.dirname(__file__)
DOCKERFILE_SCENARIO = os.path.join(DIR_DOCKER, 'Dockerfile.scenario')


def build_base_image(dkr):  # type: (DockerClient) -> None
    logger.debug("building base image")
    try:
        dkr.images.build(path=DIR_DOCKER,
                         tag=BASE_IMAGE_NAME,
                         rm=True)
    except:
        logger.exception("unexpected error when building base image")
        raise
    dkr.images.prune()
    logger.debug("built base image")


def build_scenario_image(dkr, scenario):
    # type: (DockerClient, Scenario) -> None
    logger.debug("building image for scenario: %s", scenario.name)
    build_base_image()

    # create a temporary directory for the scenario
    dir_build = tempfile.mkdtemp('.start')
    try:
        dockerfile = os.path.join(dir_build, 'Dockerfile')
        diff_fn = os.path.join(dir_build, 'vulnerability.diff')
        cfg_fn = os.path.join(dir_build, 'scenario.config')
        mission_fn = os.path.join(dir_build, 'mission.txt')
        attack_fn = os.path.join(dir_build, 'attack.py')
        shutil.copyfile(DOCKERFILE_SCENARIO, dockerfile)
        shutil.copyfile(scenario.diff_fn, diff_fn)
        shutil.copyfile(scenario.filename, cfg_fn)
        shutil.copyfile(scenario.attack.script, attack_fn)
        # FIXME scenario config assumes mission is stored in mission.txt
        shutil.copyfile(scenario.mission.filename, mission_fn)
        dkr.images.prune()
        dkr.images.build(path=dir_build,
                         tag=image_name(scenario),
                         rm=True,
                         buildargs={'REVISION': scenario.revision})
    except:
        logger.exception("unexpected error when building scenario image")
        raise
    finally:
        shutil.rmtree(dir_build, ignore_errors=True)

    logger.debug("built image for scenario")
