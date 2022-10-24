"""
SPARQL Test Steps
-----------------

behave functionality to run sparql tests on RDF
"""
import os

from behave import step
import docker
import sys
from typing import Tuple, List
from tempfile import TemporaryDirectory
from pathlib import Path


from csvcubeddevtools.helpers.tar import dir_to_tar
from csvcubeddevtools.behaviour.temporarydirectory import get_context_temp_dir_path
from csvcubeddevtools.helpers.shell import run_command_in_dir
from .dockerornot import SHOULD_USE_DOCKER

if SHOULD_USE_DOCKER:
    client = docker.from_env()
    client.images.pull("gsscogs/gdp-sparql-tests")


def _run_sparql_tests(context, tests_to_run: List[str] = []) -> Tuple[int, str]:
    return _run_sparql_tests_for_ttl(tests_to_run, context.turtle)


def _run_sparql_tests_for_ttl(
    tests_to_run: List[str], ttl_content: str
) -> Tuple[int, str]:
    if "all" in tests_to_run:
        tests_to_run = ["skos", "pmd", "qb"]

    # Stick the ttl into a file for consumption by the test runner.
    with TemporaryDirectory() as tmp:
        temp_dir = Path(tmp)
        ttl_file = temp_dir / "content.ttl"
        with open(ttl_file, "w+") as f:
            f.write(ttl_content)

        if SHOULD_USE_DOCKER:
            test_dir_params = " ".join(
                [f"-t '/usr/local/tests/{t}'" for t in tests_to_run]
            )
            sparql_test_runner = client.containers.create(
                "gsscogs/gdp-sparql-tests",
                command=f"sparql-test-runner {test_dir_params} /tmp/content.ttl",
            )

            sparql_test_runner.put_archive("/tmp", dir_to_tar(temp_dir))

            sparql_test_runner.start()
            response: dict = sparql_test_runner.wait()
            exit_code = response["StatusCode"]
            sys.stdout.write(sparql_test_runner.logs().decode("utf-8"))

            return exit_code, sparql_test_runner.logs().decode("utf-8")
        else:
            # Shouldn't use docker.

            # If you're running SPARQL tests outside of the docker container, you need to provide an environment
            # variable informing us where the tests live - so these tests can work on both *nix and Windows.
            test_dir_base = Path(os.environ.get("SPARQL_TESTS_DIR", "/usr/local/tests"))

            test_folders = [(test_dir_base / t) for t in tests_to_run]
            test_dir_params = " ".join([f"-t '{f}'" for f in test_folders])

            return run_command_in_dir(
                f"sparql-test-runner {test_dir_params} '{ttl_file}'"
            )


@step('the RDF should pass "{test_types}" SPARQL tests')
def step_impl(context, test_types: str):
    exit_code, logs = _run_sparql_tests(context, test_types.split(", "))
    assert exit_code == 0, logs


@step('the RDF should fail "{test_types}" SPARQL tests with "{expected}"')
def step_impl(context, test_types: str, expected: str):
    exit_code, logs = _run_sparql_tests(context, test_types.split(", "))
    assert exit_code == 1, logs
    assert expected in logs
