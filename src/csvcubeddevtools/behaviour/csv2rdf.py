"""
csv2rdf
-------

behave functionality to run csv2rdf on some output
"""
import os
import os.path
from behave import step
from pathlib import Path, PosixPath
import docker
import sys
from typing import Tuple, Optional
from tempfile import TemporaryDirectory
from dataclasses import dataclass


from csvcubeddevtools.helpers.tar import dir_to_tar, extract_tar
from csvcubeddevtools.behaviour.temporarydirectory import get_context_temp_dir_path
from .dockerornot import SHOULD_USE_DOCKER
from csvcubeddevtools.helpers.shell import run_command_in_dir

if SHOULD_USE_DOCKER:
    client = docker.from_env()
    client.images.pull("gsscogs/csv2rdf:native")


@dataclass
class Csv2RdfResult:
    status_code: int
    log: str
    ttl: Optional[str]
    rdf_input_directory: Path


def _run_csv2rdf(
    metadata_file_path: Path, tmp_dir: Optional[Path] = None
) -> Csv2RdfResult:
    def _run_csv2rdf_internal(tmp_dir: Path) -> Csv2RdfResult:
        if SHOULD_USE_DOCKER:
            csv2rdf = client.containers.create(
                "gsscogs/csv2rdf:native",
                command=f"csv2rdf -u /tmp/{metadata_file_path.name} -o /tmp/csv2rdf.ttl -m annotated",
            )
            csv2rdf.put_archive("/tmp", dir_to_tar(metadata_file_path.parent))

            csv2rdf.start()
            response: dict = csv2rdf.wait()
            exit_code = response["StatusCode"]
            sys.stdout.write(csv2rdf.logs().decode("utf-8"))

            output_stream, output_stat = csv2rdf.get_archive("/tmp/csv2rdf.ttl")
            extract_tar(output_stream, tmp_dir)
            maybe_output_file = tmp_dir / "csv2rdf.ttl"
            if maybe_output_file.exists():
                with open(maybe_output_file, "r") as f:
                    ttl_out = f.read()
            else:
                ttl_out = ""

            return Csv2RdfResult(
                status_code=exit_code,
                log=csv2rdf.logs().decode("utf-8"),
                ttl=ttl_out,
                rdf_input_directory=Path("/tmp"),
            )
        else:
            # Should not use docker
            ttl_out_file = tmp_dir / "csv2rdf.ttl"

            csv2rdf_command = os.environ.get("CSV2RDF", "csv2rdf")

            status_code, log = run_command_in_dir(
                f"{csv2rdf_command} -u '{metadata_file_path.resolve()}' -o '{ttl_out_file}' -m annotated",
                tmp_dir,
            )

            if ttl_out_file.exists():
                with open(ttl_out_file, "r") as f:
                    ttl_out = f.read()
            else:
                ttl_out = ""

            return Csv2RdfResult(
                status_code=status_code,
                log=log,
                ttl=ttl_out,
                rdf_input_directory=metadata_file_path.resolve().parent,
            )

    if tmp_dir is None:
        with TemporaryDirectory() as tmp_dir:
            tmp_dir = Path(tmp_dir)
            return _run_csv2rdf_internal(tmp_dir)
    else:
        return _run_csv2rdf_internal(tmp_dir)


@step('csv2rdf on "{file}" should succeed')
def step_impl(context, file: str):
    """csv2rdf on "{file}" should succeed"""
    temp_dir = get_context_temp_dir_path(context)
    csv2rdf_result = _run_csv2rdf(temp_dir / file)
    assert csv2rdf_result.status_code == 0, csv2rdf_result.log

    _update_context_for_csv2rdf_result(context, csv2rdf_result)


def _update_context_for_csv2rdf_result(context, csv2rdf_result: Csv2RdfResult):
    if hasattr(context, "turtle"):
        context.turtle += csv2rdf_result.ttl
    else:
        context.turtle = csv2rdf_result.ttl

    if not hasattr(context, "rdf_template_data"):
        context.rdf_template_data = {
            "rdf_input_directory": _path_to_file_uri_for_csv2rdf_outputs(
                csv2rdf_result.rdf_input_directory
            )
        }
    else:
        context.rdf_template_data[
            "rdf_input_directory"
        ] = _path_to_file_uri_for_csv2rdf_outputs(csv2rdf_result.rdf_input_directory)


def _path_to_file_uri_for_csv2rdf_outputs(file: Path) -> str:
    """
    Converts a `pathlib.Path` into a file:/.... URI as output by csv2rdf.
    """

    file_uri_prefix = "file:" if isinstance(file, PosixPath) else "file:/"

    return file_uri_prefix + os.path.normpath(str(file.absolute())).replace("\\", "/")


@step("csv2rdf on all CSV-Ws should succeed")
def step_impl(context):
    """csv2rdf on all CSV-Ws should succeed"""
    inputs_temp_dir = get_context_temp_dir_path(context)
    csvw_metadata_files = inputs_temp_dir.rglob("*.csv-metadata.json")
    context.turtle = ""

    with TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)

        for file in csvw_metadata_files:
            csv2rdf_result = _run_csv2rdf(inputs_temp_dir / file, tmp_dir=tmp_dir)
            assert csv2rdf_result.status_code == 0, csv2rdf_result.log

            _update_context_for_csv2rdf_result(context, csv2rdf_result)


@step('csv2rdf on "{file}" should fail with "{expected}"')
def step_impl(context, file: str, expected: str):
    """csv2rdf on \"{file}\" should fail with \"{expected}\" """
    temp_dir = get_context_temp_dir_path(context)
    csv2rdf_result = _run_csv2rdf(temp_dir / file)
    assert csv2rdf_result.status_code != 0
    assert expected in csv2rdf_result.log, csv2rdf_result.log

    _update_context_for_csv2rdf_result(context, csv2rdf_result)
