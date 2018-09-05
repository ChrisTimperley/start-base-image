import logging

from start_core.scenario import Scenario
from docker import DockerClient

from .name import name as image_name, repo_and_tag

logger = logging.getLogger(__name__)   # type: logging.Logger
logger.setLevel(logging.DEBUG)


def save_to_archive(dkr, scenario, fn_archive):
    # type: (DockerClient, Scenario, str) -> None
    name_image = image_name(scenario)
    logger.debug("saving Docker image [%s] for scenario [%s] to archive: %s",
                 name_image, scenario.name, fn_archive)
    image = dkr.images.get(name_image)
    try:
        with open(fn_archive, 'wb') as f:
            for chunk in image.save():
                f.write(chunk)
    except Exception:
        logger.debug("failed to save Docker image to disk: %s", fn_archive)
        raise
    logger.debug("saved Docker image [%s] for scenario [%s] to archive: %s",
                 name_image, scenario.name, fn_archive)


def install_from_archive(dkr, scenario, fn_archive):
    # type: (DockerClient, Scenario, str) -> None
    logger.debug("installing Docker image for scenario [%s] from archive: %s",
                 scenario.name, fn_archive)
    repo, tag = repo_and_tag(scenario)
    try:
        with open(fn_archive, 'rb') as f:
            images = dkr.images.load(f)
            # image.tag(repo, tag, force=True)
    except IOError:
        logger.debug("failed to open archive: %s", fn_archive)
        raise
    logger.debug("installed Docker image from archive: %s", fn_archive)
