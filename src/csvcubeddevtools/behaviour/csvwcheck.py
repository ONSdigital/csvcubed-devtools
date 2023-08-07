"""
csvwcheck
-------

behave functionality to run csvw-check on some output
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
    csvwcheckclient = docker.from_env()
    csvwcheckclient.images.pull("gsscogs/csvw-check:latest")

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
        return run_command_in_dir(
            f'csvw-check -s "{metadata_file_path.resolve()}"', metadata_file_path.parent
        )


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
