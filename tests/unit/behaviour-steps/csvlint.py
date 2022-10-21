"""Test the csvlint behaviour step functionality"""
import os

import pytest

from csvcubeddevtools.helpers.file import get_test_cases_dir


_test_cases_dir = get_test_cases_dir()


def test_outside_docker_csvlint_succeeds():
    """
    Test that with the NO_DOCKER=True environmental variable set, csvlint is executed outside docker on the
    local system.
    """
    os.environ["NO_DOCKER"] = "true"
    try:
        from csvcubeddevtools.behaviour.csvlint import _run_csvlint

        exit_code, logs = _run_csvlint(
            _test_cases_dir
            / "eurovision-csvw"
            / "sweden-at-eurovision-complete-dataset.csv-metadata.json"
        )
    finally:
        del os.environ["NO_DOCKER"]

    assert exit_code == 0, logs


def test_outside_docker_csvlint_fails_when_invalid():
    """
    Test that with the NO_DOCKER=True environmental variable set, csvlint is executed outside docker on the
    local system and fails when an invalid input is provided.
    """
    os.environ["NO_DOCKER"] = "true"
    try:
        from csvcubeddevtools.behaviour.csvlint import _run_csvlint

        exit_code, logs = _run_csvlint(
            _test_cases_dir / "invalid-csvw" / "year.csv-metadata.json"
        )
    finally:
        del os.environ["NO_DOCKER"]

    assert exit_code != 0, logs
    assert "invalid metadata: common property with @language lacks a @value" in logs


def test_inside_docker_csvlint_succeeds():
    """
    Test that with the NO_DOCKER=False environmental variable set, csvlint is executed outside docker on the
    local system.
    """
    from csvcubeddevtools.behaviour.csvlint import _run_csvlint

    exit_code, logs = _run_csvlint(
        _test_cases_dir
        / "eurovision-csvw"
        / "sweden-at-eurovision-complete-dataset.csv-metadata.json"
    )

    assert exit_code == 0, logs


def test_inside_docker_csvlint_fails_when_invalid():
    """
    Test that with using the docker environment, csvlint fails when an invalid input is provided.
    """
    from csvcubeddevtools.behaviour.csvlint import _run_csvlint

    exit_code, logs = _run_csvlint(
        _test_cases_dir / "invalid-csvw" / "year.csv-metadata.json"
    )

    assert exit_code != 0, logs
    assert "invalid metadata: common property with @language lacks a @value" in logs


if __name__ == "__main__":
    pytest.main()
