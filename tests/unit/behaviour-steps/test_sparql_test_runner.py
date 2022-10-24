"""Test the sparql-test-runner behaviour step functionality"""
import os

import pytest

from csvcubeddevtools.helpers.file import get_test_cases_dir


_test_cases_dir = get_test_cases_dir()


@pytest.mark.skip
def test_outside_docker_sparql_test_runner_succeeds():
    """
    Test that with the NO_DOCKER=True environmental variable set, sparql_test_runner is executed outside docker on the
    local system.
    """
    os.environ["NO_DOCKER"] = "true"
    try:
        from csvcubeddevtools.behaviour.sparqltests import _run_sparql_tests_for_ttl

        with open(_test_cases_dir / "eurovision-csvw" / "all.ttl", "r") as f:
            exit_code, logs = _run_sparql_tests_for_ttl(["skos", "qb"], f.read())
    finally:
        del os.environ["NO_DOCKER"]

    assert exit_code == 0, logs


@pytest.mark.skip
def test_outside_docker_sparql_test_runner_fails_when_invalid():
    """
    Test that with the NO_DOCKER=True environmental variable set, sparql_test_runner is executed outside docker on the
    local system and fails when an invalid input is provided.
    """
    os.environ["NO_DOCKER"] = "true"
    try:
        from csvcubeddevtools.behaviour.sparqltests import _run_sparql_tests_for_ttl

        with open(_test_cases_dir / "eurovision-csvw" / "incomplete.ttl", "r") as f:
            exit_code, logs = _run_sparql_tests_for_ttl(["all"], f.read())
    finally:
        del os.environ["NO_DOCKER"]

    assert exit_code != 0, logs
    assert "Testcase Dimensions Must Have Concepts In Code List" in logs


def test_inside_docker_sparql_test_runner_succeeds():
    """
    Test that with the NO_DOCKER environmental variable unset, sparql_test_runner is executed inside docker on the
    local system.
    """
    from csvcubeddevtools.behaviour.sparqltests import _run_sparql_tests_for_ttl

    with open(_test_cases_dir / "eurovision-csvw" / "all.ttl", "r") as f:
        exit_code, logs = _run_sparql_tests_for_ttl(["skos", "qb"], f.read())

    assert exit_code == 0, logs


def test_inside_docker_sparql_test_runner_fails_when_invalid():
    """
    Test that with the NO_DOCKER environmental variable unset, sparql_test_runner is executed inside docker on the
    local system and fails when an invalid input is provided.
    """
    from csvcubeddevtools.behaviour.sparqltests import _run_sparql_tests_for_ttl

    with open(_test_cases_dir / "eurovision-csvw" / "incomplete.ttl", "r") as f:
        exit_code, logs = _run_sparql_tests_for_ttl(["all"], f.read())

    assert exit_code != 0, logs
    assert "Testcase Dimensions Must Have Concepts In Code List" in logs


if __name__ == "__main__":
    pytest.main()
