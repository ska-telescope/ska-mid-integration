"""Implementation of the TMC MID JSON factory."""

import json
from os.path import dirname, join

from tests.test_harness3.common_utils.i_json_factory import IJsonFactory


def get_subarray_input_json(slug):
    """
    Args:
        slug (str): base name of file
    Return:
        Read and return content of file
    """
    assign_json_file_path = join(
        dirname(__file__),
        "..",
        # "..",
        # "..",
        "data",
        "subarray",
        f"{slug}.json",
    )
    with open(assign_json_file_path, "r", encoding="UTF-8") as f:
        assign_json = f.read()
    return assign_json


def get_centralnode_input_json(slug):
    """
    Args:
        slug (str): base name of file
    Return:
        Read and return content of file
    """
    assign_json_file_path = join(
        dirname(__file__),
        "..",
        # "..",
        # "..",
        "data",
        "centralnode",
        f"{slug}.json",
    )
    with open(assign_json_file_path, "r", encoding="UTF-8") as f:
        assign_json = f.read()
    return assign_json


class TMCMidJsonFactory(IJsonFactory):
    """Implement methods required for getting json."""

    # Implemented starting form usage of old
    # create_subarray_configuration
    # (sometimes called as prepare_json_args_for_commands)

    def create_subarray_configure_command_input(self) -> str:
        return get_subarray_input_json("configure_mid")

    def create_subarray_scan_command_input(self) -> str:
        return get_subarray_input_json("scan_mid")

    # Implemented starting form usage of old
    # create_assign_resources_configuration

    def create_subarray_assign_resources_command_input(self) -> str:
        return get_subarray_input_json("assign_resources_mid")

    # Implemented starting form usage of old
    # create_centralnode_configuration
    # (sometimes called also as prepare_json_args_for_centralnode_commands)

    def create_central_node_assign_resources_command_input(self) -> str:
        return get_centralnode_input_json("assign_resources_mid")

    def create_central_node_release_resources_command_input(self) -> str:
        return get_centralnode_input_json("release_resources_mid")

    # Others

    def create_default_vcc_config_command_input(self) -> str:
        return json.dumps(
            {
                "interface": "https://schema.skao.int/ska-mid-cbf-initsysparam/1.0",  # pylint: disable=line-too-long # noqa: E501
                "tm_data_sources": [
                    "car://gitlab.com/ska-telescope/ska-telmodel-data?"
                    + "ska-sdp-tmlite-repository-1.0.0#tmdata"
                ],
                "tm_data_filepath": (
                    "instrument/ska1_mid_psi/ska-mid-cbf-system-parameters.json"  # pylint: disable=line-too-long # noqa: E501
                ),
            }
        )
