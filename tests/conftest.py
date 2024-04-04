"""Test configuration file for ska_tmc_integration"""
import json
import logging
import os
import time
from os.path import dirname, join

import pytest
import tango
from pytest_bdd import given, parsers, then, when
from ska_control_model import ObsState
from ska_ser_logging import configure_logging
from ska_tango_testing.mock.tango.event_callback import (
    MockTangoEventCallbackGroup,
)
from tango import DevState

from tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
from tests.resources.test_harness.constant import centralnode, csp_master
from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import (
    CSP_SIMULATION_ENABLED,
    check_subarray_instance,
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
    update_scan_id,
    wait_and_validate_device_attribute_value,
)
from tests.resources.test_harness.simulator_factory import SimulatorFactory
from tests.resources.test_harness.subarray_node import SubarrayNodeWrapper
from tests.resources.test_harness.tmc_mid import TMCMid
from tests.resources.test_harness.utils.common_utils import (
    JsonFactory,
    SharedContext,
)
from tests.resources.test_support.common_utils.common_helpers import Waiter
from tests.resources.test_support.common_utils.result_code import ResultCode

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


def pytest_sessionstart(session):
    """
    Pytest hook; prints info about tango version.
    :param session: a pytest Session object
    :type session: :py:class:`pytest.Session`
    """
    print(tango.utils.info())


def pytest_addoption(parser):
    """
    Pytest hook; implemented to add the `--true-context` option, used to
    indicate that a true Tango subsystem is available, so there is no
    need for a :py:class:`tango.test_context.MultiDeviceTestContext`.
    :param parser: the command line options parser
    :type parser: :py:class:`argparse.ArgumentParser`
    """
    parser.addoption(
        "--true-context",
        action="store_true",
        default=False,
        help=(
            "Tell pytest that you have a true Tango context and don't "
            "need to spin up a Tango test context"
        ),
    )


def get_input_str(path):
    """
    Returns input json string
    :rtype: String
    """
    with open(path, "r", encoding="UTF-8") as file:
        input_arg = file.read()
    return input_arg


@pytest.fixture()
def json_factory():
    """
    Json factory for getting json files
    """

    def _get_json(slug):
        return get_input_str(join(dirname(__file__), "data", f"{slug}.json"))

    return _get_json


TELESCOPE_ENV = os.getenv("TELESCOPE")

TIMEOUT = 1000


def update_configure_json(
    configure_json: str,
    scan_duration: float,
    transaction_id: str,
    scan_type: str,
    config_id: str,
) -> str:
    """
    Returns a json with updated values for the given keys
    """
    config_dict = json.loads(configure_json)

    config_dict["tmc"]["scan_duration"] = scan_duration
    config_dict["transaction_id"] = transaction_id
    config_dict["sdp"]["scan_type"] = scan_type
    config_dict["csp"]["common"]["config_id"] = config_id
    return json.dumps(config_dict)


def update_scan_json(scan_json: str, scan_id: int, transaction_id: str) -> str:
    """
    Returns a json with updated values for the given keys
    """
    scan_dict = json.loads(scan_json)

    scan_dict["scan_id"] = scan_id
    scan_dict["transaction_id"] = transaction_id
    return json.dumps(scan_dict)


@pytest.fixture()
def change_event_callbacks() -> MockTangoEventCallbackGroup:
    """subarray_node
    Return a dictionary of Tango device change event callbacks with
    asynchrony support.

    :return: a collections.defaultdict that returns change event
        callbacks by name.
    """
    return MockTangoEventCallbackGroup(
        "longRunningCommandResult",
        timeout=50.0,
    )


@pytest.fixture()
def central_node_mid() -> CentralNodeWrapperMid:
    """Return CentralNode for Mid Telescope and calls tear down"""
    central_node = CentralNodeWrapperMid()
    yield central_node
    # this will call after test complete
    central_node.tear_down()


@pytest.fixture()
def tmc_mid() -> TMCMid:
    """Return TMC Mid object"""
    tmc_mid = TMCMid()
    yield tmc_mid
    tmc_mid.tear_down()


@pytest.fixture()
def subarray_node() -> SubarrayNodeWrapper:
    """Return SubarrayNode and calls tear down"""
    subarray = SubarrayNodeWrapper()
    yield subarray
    # this will call after test complete
    subarray.tear_down()


@pytest.fixture()
def command_input_factory() -> JsonFactory:
    """Return Json Factory"""
    return JsonFactory()


@pytest.fixture()
def simulator_factory() -> SimulatorFactory:
    """Return Simulator Factory for Mid Telescope"""
    return SimulatorFactory()


@pytest.fixture()
def event_recorder() -> EventRecorder:
    """Return EventRecorder and clear events"""
    event_rec = EventRecorder()
    yield event_rec
    event_rec.clear_events()


def wait_for_dish_mode_change(
    target_mode: int, dishfqdn: str, timeout_seconds: int
):
    """Returns True if the dishMode is changed to a expected value"""
    LOGGER.info("target_mode: %s", target_mode)
    start_time = time.time()

    while time.time() - start_time < timeout_seconds:
        if dishfqdn.dishMode == target_mode:
            return True
        time.sleep(1)

    return False


def wait_for_telescope_state_change(
    target_state: int, centralnode_fqdn: str, timeout_seconds: int
):
    """
    Waits for the telescopeState of a central node
    to change to the specified target_state.

    Parameters:
    - target_state (int): The expected telescopeState
                          to wait for.
    - centralnode_fqdn (str): Fully Qualified Domain
                              Name (FQDN) of the central node.
    - timeout_seconds (int): Maximum time (in seconds) to
                            wait for the state change.

    Returns:
    - bool: True if the telescopeState changes
      to the target_state within the specified timeout, False otherwise.
    """

    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        if centralnode_fqdn.telescopeState == target_state:
            return True
        time.sleep(1)

    return False


def wait_for_pointing_state_change(
    target_mode: int, dishfqdn: str, timeout_seconds: int
):
    """Returns True if the pointingState is changed to a expected value"""
    start_time = time.time()

    while time.time() - start_time < timeout_seconds:
        if dishfqdn.pointingState.value == target_mode:
            return True
        time.sleep(1)

    return False


def wait_for_obsstate_state_change(
    target_mode: int, device: str, timeout_seconds: int
):
    """Returns True if the pointingState is changed to a expected value"""
    start_time = time.time()

    while time.time() - start_time < timeout_seconds:
        if device.obsState.value == target_mode:
            return True
        time.sleep(1)

    return False


@pytest.fixture
def shared_context():
    """
    This is used for sharing data between BDD tests
    """
    return SharedContext()


@pytest.fixture(scope="session", autouse=True)
def is_dish_vcc_set():
    """
    Validate dish vcc config set to true
    """
    csp_master_device = tango.DeviceProxy(csp_master)
    if csp_master_device.adminMode != 0:
        csp_master_device.adminMode = 0
        csp_state = csp_master_device.state()
        if CSP_SIMULATION_ENABLED.lower() == "true" and csp_state in (
            tango.DevState.UNKNOWN,
            tango.DevState.DISABLE,
        ):
            csp_master_device.setdirectstate(tango.DevState.OFF)
    central_node = tango.DeviceProxy(centralnode)
    assert wait_and_validate_device_attribute_value(
        central_node,
        "isDishVccConfigSet",
        True,
    ), "Timeout while waiting for isDishVccConfigSet to true"


@given("Telescope is ON state")
def given_a_tmc(central_node_mid, event_recorder, subarray_node):
    """A method to define TMC and SDP and subscribe ."""
    assert central_node_mid.central_node.ping() > 0
    assert central_node_mid.subarray_devices["sdp_subarray"].ping() > 0
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(
        subarray_node.subarray_devices.get("sdp_subarray"), "obsState"
    )

    event_recorder.subscribe_event(
        subarray_node.subarray_devices.get("csp_subarray"), "obsState"
    )
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    event_recorder.subscribe_event(
        subarray_node.subarray_devices["sdp_subarray"], "scanID"
    )
    event_recorder.subscribe_event(
        subarray_node.subarray_devices["sdp_subarray"], "scanType"
    )

    event_recorder.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )
    central_node_mid.move_to_on()

    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )
    LOGGER.info("On step completed")


@when(parsers.parse("I assign resources to TMC SubarrayNode {subarray_id}"))
def telescope_is_in_idle_state(
    central_node_mid,
    event_recorder,
    command_input_factory,
    subarray_id,
    subarray_node,
):
    """A method to move subarray into the IDLE ObsState."""

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid_multiple_scantype", command_input_factory
    )

    assign_str = json.loads(assign_input_json)
    # Here we are adding this to get an event of ObsState CONFIGURING from
    # SDP Subarray
    assign_str["sdp"]["processing_blocks"][0]["parameters"][
        "time-to-ready"
    ] = 2

    central_node_mid.store_resources(json.dumps(assign_str))

    check_subarray_instance(
        subarray_node.subarray_devices.get("sdp_subarray"), subarray_id
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.IDLE,
    )

    check_subarray_instance(subarray_node.subarray_node, subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    LOGGER.info("Assign resources  completed")


@when(parsers.parse("end the configuration on TMC SubarrayNode {subarray_id}"))
def execute_end_command(
    subarray_node,
    command_input_factory,
    central_node_mid,
    event_recorder,
    subarray_id,
    scan_types,
):
    """ "A method to invoke end command"""

    central_node_mid.set_subarray_id(subarray_id)
    _, unique_id = subarray_node.execute_transition("End")
    the_waiter = Waiter()
    the_waiter.set_wait_for_specific_obsstate(
        "IDLE", [subarray_node.subarray_node]
    )
    the_waiter.wait(100)

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.IDLE,
    )

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (unique_id[0], str(int(ResultCode.OK))),
        lookahead=5,
    )


@when(parsers.parse("release the resources on TMC SubarrayNode {subarray_id}"))
def execute_release_resources_command(
    command_input_factory,
    central_node_mid,
    event_recorder,
    subarray_id,
):
    """ "A method to invoke Release Resources command"""

    release_input_json = prepare_json_args_for_centralnode_commands(
        "release_resources_mid", command_input_factory
    )
    check_subarray_instance(central_node_mid.subarray_node, subarray_id)
    _, unique_id = central_node_mid.invoke_release_resources(
        release_input_json
    )

    """Method to check SDP is in EMPTY obsstate"""
    check_subarray_instance(
        central_node_mid.subarray_devices.get("sdp_subarray"), subarray_id
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.EMPTY,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (unique_id[0], str(int(ResultCode.OK))),
        lookahead=5,
    )


@then(
    parsers.parse(
        "TMC SubarrayNode {subarray_id} transitions to EMPTY ObsState"
    )
)
def check_tmc_is_in_empty_obsstate(
    central_node_mid, event_recorder, subarray_id
):
    """Method to check TMC is in EMPTY obsstate."""
    check_subarray_instance(central_node_mid.subarray_node, subarray_id)
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@when(
    parsers.parse(
        "reperform scan for different duration and same configuration"
    )
)
def reexecute_scan_command(
    command_input_factory,
    central_node_mid,
    event_recorder,
    subarray_id,
    subarray_node,
):
    """ "A method to invoke scan command followed by end scan
    with lesser duration"""

    scan_id = 10
    scan_json = prepare_json_args_for_commands(
        "scan_mid", command_input_factory
    )

    scan_json = update_scan_id(scan_json, scan_id)
    _, unique_id = subarray_node.execute_transition("Scan", argin=scan_json)

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.SCANNING,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.SCANNING,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["sdp_subarray"],
        "scanID",
        int(scan_id),
    )

    # Execute End Scan
    _, unique_id = subarray_node.remove_scan_data()
    #
    # check_device_status_ready(subarray_node.subarray_devices["sdp_subarray"])
    # assert event_recorder.has_change_event_occurred(
    #     subarray_node.subarray_devices["sdp_subarray"],
    #     "obsState",
    #     ObsState.READY,
    # )
    #
    # check_device_status_ready(subarray_node.subarray_node)
    # assert event_recorder.has_change_event_occurred(
    #     subarray_node.subarray_node,
    #     "obsState",
    #     ObsState.READY,
    # )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (unique_id[0], str(int(ResultCode.OK))),
        lookahead=5,
    )
