import logging

from start_core.scenario import Scenario

from .name import name as image_name
from .build import _docker_client

logger = logging.getLogger(__name__)   # type: logging.Logger
logger.setLevel(logging.DEBUG)


def save_to_archive(scenario, fn_archive):
    # type: (Scenario, str) -> None
    name_image = image_name(scenario)
    logger.debug("saving Docker image [%s] for scenario [%s] to archive: %s",
                 name_image, scenario.name, fn_archive)
    dkr = _docker_client()
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


def install_from_archive(scenario, fn_archive):
    # type: (Scenario, str) -> None
    logger.debug("installing Docker image for scenario [%s] from archive: %s",
                 scenario.name, fn_archive)
    dkr = _docker_client()
    try:
        with open(fn_archive, 'rb') as f:
            dkr.images.build(fileobj=f,
                             tag=image_name(scenario),
                             rm=True)
    except IOError:
        logger.debug("failed to open archive: %s", fn)
        raise
    logger.debug("installed Docker image from archive: %s", fn)
