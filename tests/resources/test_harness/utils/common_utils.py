"""This module implement common utils
"""
from os.path import dirname, join

from ska_control_model import ObsState

from tests.resources.test_harness.utils.wait_helpers import Waiter
from tests.resources.test_support.common_utils.result_code import ResultCode


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
        "..",
        "..",
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
        "..",
        "..",
        "data",
        "centralnode",
        f"{slug}.json",
    )
    with open(assign_json_file_path, "r", encoding="UTF-8") as f:
        assign_json = f.read()
    return assign_json


class JsonFactory(object):
    """Implement methods required for getting json"""

    def create_subarray_configuration(self, json_type):
        """Read and return configuration json file from
            tests/data/subarray folder
        Args:
            json_type (str): Base name of file which is stored in data folder
        Return:
            config_json (str): Return configure json based json type provided
        """
        return get_subarray_input_json(json_type)

    def create_assign_resources_configuration(self, json_type):
        """Read and return configuration json file from
            tests/data/subarray folder
        Args:
            json_type (str): Base name of file which is stored in data folder
        Return:
            config_json (str): Return configure json based json type provided
        """
        return get_subarray_input_json(json_type)

    def create_centralnode_configuration(self, json_type):
        """Read and return configuration json file from
            tests/data/centralnode folder
        Args:
            json_type (str): Base name of file which is stored in data folder
        Return:
            config_json (str): Return configure json based json type provided
        """
        return get_centralnode_input_json(json_type)


class SharedContext:
    def __init__(self):
        self.unique_id = None


def check_scan_successful(
    subarray_node, event_recorder, scan_id, unique_id
) -> None:
    """
    1)CSP , TMC subarray  go to scanning
    2)scan_id attribute from CSP sub-array reflects exact scan_id
    sent by TMC .This makes sure we are checking some more attributes
    from CSP .In future this can be extended to include other attribute
    verification as well.
    3)After scan duration is completed , end scan will be triggered
    taking system to READY state. Related Obs-state checks are  added.
    """
    # Faced a delay while testing , hence adding waiter here.

    # wait_for_device_status_scanning(subarray_node.subarray_node)
    the_waiter = Waiter()
    the_waiter.set_wait_for_specific_obsstate(
        "SCANNING", [subarray_node.subarray_node]
    )
    the_waiter.wait(200)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.SCANNING,
        lookahead=10,
    )
    the_waiter.wait(100)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.SCANNING,
        lookahead=50,
    )

    the_waiter.set_wait_for_specific_obsstate(
        "READY", [subarray_node.subarray_node]
    )
    the_waiter.wait(100)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.READY,
        lookahead=15,
    )

    the_waiter.set_wait_for_specific_obsstate(
        "READY", [subarray_node.subarray_node]
    )
    the_waiter.wait(100)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node, "obsState", ObsState.READY, lookahead=20
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (unique_id[0], str(int(ResultCode.OK))),
        lookahead=10,
    )


def check_configure_successful(
    subarray_node, event_recorder, unique_id, scan_type, processed_scan_type
) -> None:
    """
    Adds check to verify if configure command is successful
    """
    the_waiter = Waiter()
    the_waiter.set_wait_for_specific_obsstate(
        "READY", [subarray_node.subarray_devices["csp_subarray"]]
    )
    the_waiter.wait(100)
    the_waiter.set_wait_for_specific_obsstate(
        "READY", [subarray_node.subarray_node]
    )
    the_waiter.wait(100)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node, "obsState", ObsState.READY, lookahead=10
    )

    event_recorder.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (unique_id[0], str(int(ResultCode.OK))),
        lookahead=10,
    )
