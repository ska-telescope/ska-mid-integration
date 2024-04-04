import pytest
from pytest_bdd import given, parsers, scenario, then, when
from tango import DeviceProxy, EventType

from tests.conftest import LOGGER, TIMEOUT
from tests.resources.test_support.common_utils.common_helpers import (
    Resource,
    Waiter,
)
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.common_utils.telescope_controls import (
    BaseTelescopeControl,
)
from tests.resources.test_support.common_utils.tmc_helpers import TmcHelper
from tests.resources.test_support.constant import (
    DEVICE_LIST_FOR_CHECK_DEVICES,
    DEVICE_OBS_STATE_EMPTY_INFO,
    DEVICE_OBS_STATE_IDLE_INFO,
    DEVICE_OBS_STATE_READY_INFO,
    DEVICE_STATE_ON_INFO,
    DEVICE_STATE_STANDBY_INFO,
    ON_OFF_DEVICE_COMMAND_DICT,
    centralnode,
    tmc_subarraynode1,
)

tmc_helper = TmcHelper(centralnode, tmc_subarraynode1)
telescope_control = BaseTelescopeControl()
result, message = "", ""
the_waiter = Waiter()


@pytest.mark.SKA_mid
@scenario(
    "../features/check_command_not_allowed.feature",
    "Unexpected commands not allowed when TMC subarray is in Resourcing",
)
def test_command_not_allowed():
    """Assigning the resources in RESOURCING obsState"""


@given("TMC is in ON state")
def given_tmc():
    tmc_helper.check_devices(DEVICE_LIST_FOR_CHECK_DEVICES)
    assert telescope_control.is_in_valid_state(
        DEVICE_STATE_STANDBY_INFO, "State"
    )
    LOGGER.info("Starting up the Telescope")
    tmc_helper.set_to_on(**ON_OFF_DEVICE_COMMAND_DICT)
    assert telescope_control.is_in_valid_state(DEVICE_STATE_ON_INFO, "State")
    assert telescope_control.is_in_valid_state(
        DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
    )


@given("the subarray is busy in assigning the resources")
def given_tmc_obsState(json_factory):
    assign_json = json_factory("command_AssignResources")
    central_node = DeviceProxy(centralnode)
    tmc_helper.check_devices(DEVICE_LIST_FOR_CHECK_DEVICES)
    pytest.command_result = central_node.AssignResources(assign_json)
    LOGGER.info("Checking for Subarray node obsState")

    the_waiter = Waiter()
    the_waiter.set_wait_for_specific_obsstate(
        "RESOURCING", [tmc_subarraynode1]
    )
    the_waiter.wait(TIMEOUT)
    Resource(tmc_subarraynode1).assert_attribute("obsState").equals(
        "RESOURCING"
    )


@when("AssignResources command is invoked, TMC raises exception")
def send_command(json_factory):
    LOGGER.info("Invoked AssignResources2 from CentralNode")
    with pytest.raises(Exception) as e:
        assign_json2 = json_factory("command_AssignResources_2")
        central_node = DeviceProxy(centralnode)
        LOGGER.info("Invoked AssignResources2 from CentralNode")
        central_node.AssignResources(assign_json2)
    assert "AssignResources command not permitted in observation state" in str(
        e.value
    )
    subarrray = DeviceProxy(tmc_subarraynode1)
    LOGGER.info(f"SubarrayNode Obsstae: {subarrray.obsState}")


@when("previous AssignResources executed succesfully")
def check_asignresources_completed(change_event_callbacks):
    central_node = DeviceProxy(centralnode)
    central_node.subscribe_event(
        "longRunningCommandResult",
        EventType.CHANGE_EVENT,
        change_event_callbacks["longRunningCommandResult"],
    )
    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        (pytest.command_result[1][0], str(ResultCode.OK.value)),
        lookahead=4,
    )
    assert telescope_control.is_in_valid_state(
        DEVICE_OBS_STATE_IDLE_INFO, "obsState"
    )


@then(parsers.parse("TMC executes the Configure command successfully"))
def tmc_accepts_permitted_commands(json_factory):
    configure_json = json_factory("command_Configure")
    release_json = json_factory("command_ReleaseResources")
    LOGGER.info("Invoking Configure command on TMC SubarrayNode")

    tmc_helper.configure_sub(configure_json, **ON_OFF_DEVICE_COMMAND_DICT)
    LOGGER.info("Configure command on TMC SubarrayNode is successful")
    assert telescope_control.is_in_valid_state(
        DEVICE_OBS_STATE_READY_INFO, "obsState"
    )
    LOGGER.info("Invoking End command on TMC SubarrayNode")
    tmc_helper.end(**ON_OFF_DEVICE_COMMAND_DICT)
    LOGGER.info("End command on TMC SubarrayNode is successful")
    # tear down
    tmc_helper.invoke_releaseResources(
        release_json, **ON_OFF_DEVICE_COMMAND_DICT
    )
    LOGGER.info("ReleaseResources command on TMC SubarrayNode is successful")
    assert telescope_control.is_in_valid_state(
        DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
    )
    tmc_helper.set_to_standby(**ON_OFF_DEVICE_COMMAND_DICT)
    LOGGER.info("ReleaseResources command on TMC SubarrayNode is successful")
    assert telescope_control.is_in_valid_state(
        DEVICE_STATE_STANDBY_INFO, "State"
    )
    LOGGER.info("Tear Down complete. Telescope is in Standby State")
