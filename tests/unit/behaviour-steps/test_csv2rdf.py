"""Test the csvlint behaviour step functionality"""
import os

import pytest

from csvcubeddevtools.helpers.file import get_test_cases_dir


_test_cases_dir = get_test_cases_dir()


def test_outside_docker_csv2rdf_succeeds():
    """
    Test that with the NO_DOCKER=True environmental variable set, csv2rdf is executed outside docker on the
    local system.
    """
    os.environ["NO_DOCKER"] = "true"
    try:
        from csvcubeddevtools.behaviour.csv2rdf import _run_csv2rdf

        exit_code, logs, ttl_out = _run_csv2rdf(
            _test_cases_dir
            / "eurovision-csvw"
            / "sweden-at-eurovision-complete-dataset.csv-metadata.json"
        )
    finally:
        del os.environ["NO_DOCKER"]

    assert exit_code == 0, logs
    assert len(ttl_out) > 0, ttl_out


def test_outside_docker_csv2rdf_fails_when_invalid():
    """
    Test that with the NO_DOCKER=True environmental variable set, csv2rdf is executed outside docker on the
    local system and fails when an invalid input is provided.
    """
    os.environ["NO_DOCKER"] = "true"
    try:
        from csvcubeddevtools.behaviour.csv2rdf import _run_csv2rdf

        exit_code, logs, ttl_out = _run_csv2rdf(
            _test_cases_dir / "invalid-csvw" / "year.csv-metadata.json"
        )
    finally:
        del os.environ["NO_DOCKER"]

    assert exit_code != 0, logs
    assert len(ttl_out) == 0, ttl_out
    assert "csv2rdf.main" in logs


def test_inside_docker_csv2rdf_succeeds():
    """
    Test that with the NO_DOCKER=False environmental variable set, csv2rdf is executed outside docker on the
    local system.
    """
    from csvcubeddevtools.behaviour.csv2rdf import _run_csv2rdf

    exit_code, logs, ttl_out = _run_csv2rdf(
        _test_cases_dir
        / "eurovision-csvw"
        / "sweden-at-eurovision-complete-dataset.csv-metadata.json"
    )

    assert exit_code == 0, logs
    assert len(ttl_out) > 0, ttl_out


def test_inside_docker_csv2rdf_fails_when_invalid():
    """
    Test that with using the docker environment, csv2rdf fails when an invalid input is provided.
    """
    from csvcubeddevtools.behaviour.csv2rdf import _run_csv2rdf

    exit_code, logs, ttl_out = _run_csv2rdf(
        _test_cases_dir / "invalid-csvw" / "year.csv-metadata.json"
    )

    assert exit_code != 0, logs
    assert len(ttl_out) == 0, ttl_out
    assert "csv2rdf.main" in logs


if __name__ == "__main__":
    pytest.main()
