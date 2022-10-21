"""
Docker Or Not
-------------

Contains information on whether to use docker or not.
"""

SHOULD_USE_DOCKER = not bool(
    distutils.util.strtobool(os.environ.get("NO_DOCKER", "false"))
)
