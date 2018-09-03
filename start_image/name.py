"""
This module is responsible for assigning names to the Docker images for
START scenarios.
"""
from typing import Tuple

from start_core.scenario import Scenario

BASE_IMAGE_NAME = "christimperley/start:base"


def repo_and_tag(scenario):  # type: (Scenario) -> Tuple[str, str]
    # FIXME ensure tag is legal!
    repo = "christimperley/start"
    tag = scenario.name
    return (repo, tag)


def name(scenario):  # type: (Scenario) -> str
    """
    Returns the fully qualified name of the Docker image for a scenario,
    given by its name.
    """
    return ':'.join(repo_and_tag(scenario))
