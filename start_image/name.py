"""
This module is responsible for assigning names to the Docker images for
START scenarios.
"""
from start_core.scenario import Scenario

BASE_IMAGE_NAME = "christimperley/start:base"


def name(scenario):  # type: (Scenario) -> str
    """
    Returns the fully qualified name of the Docker image for a scenario,
    given by its name.
    """
    # FIXME ensure name is legal
    return "christimperley/start:{}".format(scenario.name)
