"""
This module is responsible for managing the Docker images used by START.
"""
__all__ = ['build_base_image', 'build_scenario_image']

import os
import logging
import tempfile
import shutil

import docker

from start_core.scenario import Scenario

from .name import BASE_IMAGE_NAME
from .name import name as image_name

logger = logging.getLogger(__name__)   # type: logging.Logger
logger.setLevel(logging.DEBUG)

DIR_DOCKER = os.path.join(os.path.dirname(__file__), '../docker')
DOCKERFILE_SCENARIO = os.path.join(DIR_DOCKER, 'Dockerfile.scenario')


__DOCKER_CLIENT = None  # type: Optional[docker.DockerClient]
def __docker_client():  # type: () -> docker.DockerClient
    global __DOCKER_CLIENT
    if __DOCKER_CLIENT:
        return __DOCKER_CLIENT
    try:
        __DOCKER_CLIENT = docker.from_env()
    except:
        logger.exception("failed to start Docker client")
        raise
    return __DOCKER_CLIENT


def build_base_image():  # type: () -> None
    logger.debug("building base image")
    dkr = __docker_client()
    print(DIR_DOCKER)
    try:
        dkr.images.build(path=DIR_DOCKER,
                         tag=BASE_IMAGE_NAME,
                         rm=True)
    except:
        logger.exception("unexpected error when building base image")
        raise
    dkr.images.prune()
    logger.debug("built base image")


def build_scenario_image(scenario):  # type: (Scenario) -> None
    logger.debug("building image for scenario: %s", scenario.name)
    dkr = __docker_client()
    build_base_image()

    # FIXME temporary values
    scenario.diff_fn = "TODO"
    scenario.revision = "TODO"

    # create a temporary directory for the scenario
    dir_build = tempfile.mkdtemp('.start')
    try:
        dockerfile = os.path.join(dir_build, 'Dockerfile')
        diff_fn = os.path.join(dir_build, 'bug.diff')
        shutil.copyfile(DOCKERFILE_SCENARIO, dockerfile)
        shutil.copyfile(scenario.diff_fn, diff_fn)  # FIXME scenario.diff_fn
        dkr.images.prune()
        dkr.images.build(path=dir_build,
                         tag=image_name(scenario),
                         rm=True,
                         buildargs={'REVISION': scenario.revision})  # FIXME scenario.revision
    except:
        logger.exception("unexpected error when building scenario image")
        raise
    finally:
        shutil.rmtree(dir_build, ignore_errors=True)

    logger.debug("built image for scenario")
