"""
csvlint
-------

behave functionality to run csv-lint on some output
"""
from behave import *
from pathlib import Path
import docker
import sys
from typing import Tuple

from csvcubeddevtools.helpers.tar import dir_to_tar
from csvcubeddevtools.behaviour.temporarydirectory import get_context_temp_dir_path
from csvcubeddevtools.helpers.shell import run_command_in_dir
from .dockerornot import SHOULD_USE_DOCKER

if SHOULD_USE_DOCKER:
    client = docker.from_env()
    client.images.pull("gsscogs/csvlint")
    csvwcheckclient = docker.from_env()
    csvwcheckclient.images.pull("gsscogs/csvw-check:latest")


def _run_csvlint(metadata_file_path: Path) -> Tuple[int, str]:
    if SHOULD_USE_DOCKER:
        csvlint = client.containers.create(
            "gsscogs/csvlint", command=f"csvlint -s '/tmp/{metadata_file_path.name}'"
        )
        csvlint.put_archive("/tmp", dir_to_tar(metadata_file_path.parent))
        csvlint.start()
        response: dict = csvlint.wait()
        exit_code = response["StatusCode"]
        sys.stdout.write(csvlint.logs().decode("utf-8"))
        return exit_code, csvlint.logs().decode("utf-8")
    else:
        return run_command_in_dir(
            f'csvlint -s "{metadata_file_path.resolve()}"', metadata_file_path.parent
        )

def _run_csvwcheck(metadata_file_path: Path) -> Tuple[int, str]:
    if SHOULD_USE_DOCKER:
        csvwcheck = csvwcheckclient.containers.create(
            "gsscogs/csvw-check:latest", command=f"bin/csvw-check -s '/tmp/{metadata_file_path.name}'"
        )
        csvwcheck.put_archive("/tmp", dir_to_tar(metadata_file_path.parent))
        csvwcheck.start()
        response: dict = csvwcheck.wait()
        exit_code = response["StatusCode"]
        sys.stdout.write(csvwcheck.logs().decode("utf-8"))
        return exit_code, csvwcheck.logs().decode("utf-8")
    else:
        # If SHOULD_USE_DOCKER is false then we assume we are in the windows environment. Windows tests will be done as part of next ticket
        return run_command_in_dir(
            f'csvlint -s "{metadata_file_path.resolve()}"', metadata_file_path.parent
        )

@step("csvlint validation of all CSV-Ws should succeed")
def step_impl(context):
    temp_dir = get_context_temp_dir_path(context)
    for file in temp_dir.rglob("*.csv-metadata.json"):
        exit_code, logs = _run_csvlint(temp_dir / file)
        assert exit_code == 0, logs


@step('csvlint validation of "{file}" should succeed')
def step_impl(context, file: str):
    temp_dir = get_context_temp_dir_path(context)
    exit_code, logs = _run_csvlint(temp_dir / file)
    assert exit_code == 0, logs


@step('csvlint validation of "{file}" should fail with "{expected}"')
def step_impl(context, file: str, expected: str):
    temp_dir = get_context_temp_dir_path(context)
    exit_code, logs = _run_csvlint(temp_dir / file)
    assert exit_code == 1, logs
    assert expected in logs, logs


@step("csvwcheck validation of all CSV-Ws should succeed")
def step_impl(context):
    temp_dir = get_context_temp_dir_path(context)
    for file in temp_dir.rglob("*.csv-metadata.json"):
        exit_code, logs = _run_csvwcheck(temp_dir / file)
        assert exit_code == 0, logs


@step('csvwcheck validation of "{file}" should succeed')
def step_impl(context, file: str):
    temp_dir = get_context_temp_dir_path(context)
    exit_code, logs = _run_csvwcheck(temp_dir / file)
    assert exit_code == 0, logs


@step('csvwcheck validation of "{file}" should fail with "{expected}"')
def step_impl(context, file: str, expected: str):
    temp_dir = get_context_temp_dir_path(context)
    exit_code, logs = _run_csvwcheck(temp_dir / file)
    assert exit_code == 1, logs
    assert expected in logs, logs