"""This module implement common utils
"""
# pylint: skip-file
import time

from ska_control_model import ObsState

from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.test_harness3.utils.wait_helpers import Waiter


class SharedContext:
    def __init__(self):
        self.unique_id = None


def check_obsstate_sdp_in_first_configure(
    event_recorder, subarray_node
) -> None:
    """
    SDP does not go to CONFIGURING in each CONFIGURE command
    except very first CONFIGURE command after Assign .

    """
    # TODO
    # Currently SDP goes in configuring only in first configure
    # Command.This is however resolved in SDP 0.20.0.
    # When testing with same version is done ,we can check and remove
    # this logic of configure_cycle and perform check for
    # configuring after each of the configure command
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.CONFIGURING,
    )
    wait_for_device_status_ready(
        subarray_node.subarray_devices["sdp_subarray"]
    )

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.READY,
    )


def check_scan_successful(
    subarray_node, event_recorder, scan_id, unique_id
) -> None:
    """
    1)SDP , TMC sub-array  go to scanning
    2)scan_id attribute from SDP sub-array reflects exact scan_id
    sent by TMC .This makes sure we are checking some more attributes
    from SDP .In future this can be extended to include other attribute
    verification as well.
    3)After scan duration is completed , end scan will be triggered
    taking system to READY state. Related Obs-state checks are  added.
    """

    wait_for_device_status_scanning(subarray_node.subarray_node)

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.SCANNING,
        lookahead=20,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.SCANNING,
        lookahead=20,
    )

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["sdp_subarray"],
        "scanID",
        int(scan_id),
        lookahead=20,
    )

    wait_for_device_status_ready(
        subarray_node.subarray_devices["sdp_subarray"]
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.READY,
        lookahead=20,
    )

    wait_for_device_status_ready(subarray_node.subarray_node)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node, "obsState", ObsState.READY, lookahead=20
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (unique_id[0], str(int(ResultCode.OK))),
        lookahead=20,
    )


def check_configure_successful(
    subarray_node, event_recorder, unique_id, scan_type, processed_scan_type
) -> None:
    """
    Adds check to verify if configure command is successful
    """
    wait_for_device_status_ready(
        subarray_node.subarray_devices["sdp_subarray"]
    )

    wait_for_device_status_ready(subarray_node.subarray_node)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node, "obsState", ObsState.READY, lookahead=10
    )

    # For same configuration scantype no event is pushed
    # https://gitlab.com/ska-telescope/sdp/ska-sdp-lmc/-/blob/master/src/ska_sdp_lmc/subarray/device.py#L548

    if scan_type != processed_scan_type:
        assert event_recorder.has_change_event_occurred(
            subarray_node.subarray_devices["sdp_subarray"],
            "scanType",
            scan_type,
            lookahead=20,
        )

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (unique_id[0], str(int(ResultCode.OK))),
        lookahead=20,
    )


def wait_for_device_status_ready(device_name: str) -> None:
    """
    Checks if given device is in READY obs-state

     :param device_name: device name
     :type device_name: str
    """
    the_waiter = Waiter()
    the_waiter.set_wait_for_specific_obsstate("READY", [device_name])
    the_waiter.wait(500)


def wait_for_device_status_scanning(device_name: str) -> None:
    """
    Checks if given device is in SCANNING obs-state

    :param device_name: device name
    :type device_name: str
    """
    the_waiter = Waiter()
    the_waiter.set_wait_for_specific_obsstate("SCANNING", [device_name])
    the_waiter.wait(200)


def wait_added_for_skb372():
    """
    Waits for few seocnds
    """
    time.sleep(4)
