"""Test the csvlint behaviour step functionality"""
import sys
import os

import pytest

from csvcubeddevtools.helpers.file import get_test_cases_dir


_test_cases_dir = get_test_cases_dir()


@pytest.fixture(scope="module", autouse=True)
def set_csv2rdf_environmental_variable():
    os.environ["CSV2RDF"] = "/usr/local/bin/csv2rdf"

    yield []

    del os.environ["CSV2RDF"]


@pytest.fixture(scope="function", autouse=True)
def remove_sensitive_imports_before_test():
    """These two modules configure themselves differently depending on whether they've been tasked with running inside
    docker or outside. Clean up before every test so that everything is freshly configured."""

    if "csvcubeddevtools.behaviour.csv2rdf" in sys.modules:
        del sys.modules["csvcubeddevtools.behaviour.csv2rdf"]
    if "csvcubeddevtools.behaviour.dockerornot" in sys.modules:
        del sys.modules["csvcubeddevtools.behaviour.dockerornot"]


@pytest.mark.skip
def test_outside_docker_csv2rdf_succeeds():
    """
    Test that with the NO_DOCKER=True environmental variable set, csv2rdf is executed outside docker on the
    local system.
    """
    os.environ["NO_DOCKER"] = "true"
    try:
        from csvcubeddevtools.behaviour.csv2rdf import _run_csv2rdf

        csv2rdf_result = _run_csv2rdf(
            _test_cases_dir
            / "eurovision-csvw"
            / "sweden-at-eurovision-complete-dataset.csv-metadata.json"
        )
    finally:
        del os.environ["NO_DOCKER"]
        del sys.modules["csvcubeddevtools.behaviour.csv2rdf"]

    assert csv2rdf_result.status_code == 0, csv2rdf_result.log
    assert len(csv2rdf_result.ttl) > 0, csv2rdf_result.ttl


@pytest.mark.skip
def test_outside_docker_csv2rdf_fails_when_invalid():
    """
    Test that with the NO_DOCKER=True environmental variable set, csv2rdf is executed outside docker on the
    local system and fails when an invalid input is provided.
    """
    os.environ["NO_DOCKER"] = "true"
    try:
        from csvcubeddevtools.behaviour.csv2rdf import _run_csv2rdf

        csv2rdf_result = _run_csv2rdf(
            _test_cases_dir / "invalid-csvw" / "year.csv-metadata.json"
        )
    finally:
        del os.environ["NO_DOCKER"]
        del sys.modules["csvcubeddevtools.behaviour.csv2rdf"]

    assert csv2rdf_result.status_code != 0, csv2rdf_result.log
    assert len(csv2rdf_result.ttl) == 0, csv2rdf_result.ttl
    assert "csv2rdf.main" in csv2rdf_result.log


def test_inside_docker_csv2rdf_succeeds():
    """
    Test that with the NO_DOCKER=False environmental variable set, csv2rdf is executed outside docker on the
    local system.
    """
    from csvcubeddevtools.behaviour.csv2rdf import _run_csv2rdf
    from csvcubeddevtools.behaviour.dockerornot import SHOULD_USE_DOCKER

    assert "NO_DOCKER" not in os.environ
    assert SHOULD_USE_DOCKER
    csv2rdf_result = _run_csv2rdf(
        _test_cases_dir
        / "eurovision-csvw"
        / "sweden-at-eurovision-complete-dataset.csv-metadata.json"
    )

    assert csv2rdf_result.status_code == 0, csv2rdf_result.log
    assert len(csv2rdf_result.ttl) > 0, csv2rdf_result.ttl


def test_inside_docker_csv2rdf_fails_when_invalid():
    """
    Test that with using the docker environment, csv2rdf fails when an invalid input is provided.
    """
    from csvcubeddevtools.behaviour.csv2rdf import _run_csv2rdf
    from csvcubeddevtools.behaviour.dockerornot import SHOULD_USE_DOCKER

    assert "NO_DOCKER" not in os.environ
    assert SHOULD_USE_DOCKER
    csv2rdf_result = _run_csv2rdf(
        _test_cases_dir / "invalid-csvw" / "year.csv-metadata.json"
    )

    assert csv2rdf_result.status_code != 0, csv2rdf_result.log
    assert len(csv2rdf_result.ttl) == 0, csv2rdf_result.ttl
    assert "csv2rdf.main" in csv2rdf_result.log


if __name__ == "__main__":
    pytest.main()
