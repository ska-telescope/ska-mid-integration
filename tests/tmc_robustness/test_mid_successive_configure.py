from datetime import datetime

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tango import DeviceProxy

from tests.conftest import LOGGER
from tests.resources.test_support.common_utils.telescope_controls import (
    BaseTelescopeControl,
)
from tests.resources.test_support.common_utils.tmc_helpers import (
    TmcHelper,
    tear_down,
)
from tests.resources.test_support.constant import (
    DEVICE_LIST_FOR_CHECK_DEVICES,
    DEVICE_OBS_STATE_EMPTY_INFO,
    DEVICE_OBS_STATE_IDLE_INFO,
    DEVICE_OBS_STATE_READY_INFO,
    DEVICE_STATE_OFF_INFO,
    DEVICE_STATE_ON_INFO,
    DEVICE_STATE_STANDBY_INFO,
    ON_OFF_DEVICE_COMMAND_DICT,
    centralnode,
    tmc_subarraynode1,
)

tmc_helper = TmcHelper(centralnode, tmc_subarraynode1)
telescope_control = BaseTelescopeControl()


@pytest.mark.SKA_mid
@scenario(
    "../features/successive_configure.feature",
    "TMC validates reconfigure functionality",
)
def test_multiple_configure_functionality():
    """
    Test TMC allows multiple configuration

    """


@given("the TMC is On")
def given_tmc(json_factory):
    release_json = json_factory("command_ReleaseResources")
    try:
        tmc_helper.check_devices(DEVICE_LIST_FOR_CHECK_DEVICES)
        # Verify Telescope is Off/Standby
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )

        dish_node = DeviceProxy("ska063/elt/master")
        LOGGER.info(dish_node.read_attribute("DishMode").value)

        tmc_helper.set_to_on(**ON_OFF_DEVICE_COMMAND_DICT)
        LOGGER.info("TelescopeOn command is invoked successfully")

        now = datetime.now()
        current_time = now.strftime("%d/%m/%Y %H:%M:%S:%f")
        LOGGER.info("current_time - %s ", current_time)

        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_ON_INFO, "State"
        )

        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
        )
    except Exception:
        tear_down(release_json, **ON_OFF_DEVICE_COMMAND_DICT)


@given("the subarray is in IDLE obsState")
def given_subarray_in_idle(json_factory):
    assign_json = json_factory("multiple_assign1")
    release_json = json_factory("command_ReleaseResources")
    try:
        # Invoke AssignResources() Command on TMC
        LOGGER.info("Invoking AssignResources command on TMC CentralNode")
        tmc_helper.compose_sub(assign_json, **ON_OFF_DEVICE_COMMAND_DICT)

        # Verify ObsState is IDLE
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_IDLE_INFO, "obsState"
        )
    except Exception:
        tear_down(release_json, **ON_OFF_DEVICE_COMMAND_DICT)


@when(parsers.parse("the command configure is issued with {input_json1}"))
def send_configure(json_factory, input_json1):
    configure_json1 = json_factory(input_json1)
    release_json = json_factory("command_ReleaseResources")
    try:
        LOGGER.info("Invoking Configure command with input_json1")
        # Invoke Configure() command
        tmc_helper.configure_subarray(
            configure_json1, **ON_OFF_DEVICE_COMMAND_DICT
        )
        LOGGER.info("Configure1 is invoked successfully")
    except Exception:
        tear_down(release_json, **ON_OFF_DEVICE_COMMAND_DICT)


@then("the subarray transitions to obsState READY")
def check_for_ready():
    # Verify ObsState is READY
    LOGGER.info("Verifying obsState READY after Configure1")
    assert telescope_control.is_in_valid_state(
        DEVICE_OBS_STATE_READY_INFO, "obsState"
    )


@when(
    parsers.parse(
        "the next successive configure command is issued with {input_json2}"
    )
)
def send_next_configure(json_factory, input_json2):
    configure_json2 = json_factory(input_json2)
    release_json = json_factory("command_ReleaseResources")
    try:
        LOGGER.info("Invoking Configure command with input_json2")
        # Invoke successive Configure() command
        tmc_helper.configure_subarray(
            configure_json2, **ON_OFF_DEVICE_COMMAND_DICT
        )
        LOGGER.info("Configure2 is invoked successfully")
    except Exception:
        tear_down(release_json, **ON_OFF_DEVICE_COMMAND_DICT)


@then("the subarray reconfigures changing its obsState to READY")
def check_for_reconfigure_ready(subarray_node, event_recorder):

    # Verify ObsState is READY
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    LOGGER.info("Verifying obsState READY after Configure2")
    # assert telescope_control.is_in_valid_state(
    #     DEVICE_OBS_STATE_READY_INFO, "obsState"
    # )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
    )


@then("test goes for the tear down")
def check_for_tear_down(json_factory):
    release_json = json_factory("command_ReleaseResources")
    try:
        # Invoke End() command
        LOGGER.info("Invoking End command on TMC SubarrayNode")
        tmc_helper.end(**ON_OFF_DEVICE_COMMAND_DICT)

        # Verify ObsState is IDLE
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_IDLE_INFO, "obsState"
        )
        # Invoke ReleaseResources() command
        tmc_helper.invoke_releaseResources(
            release_json, **ON_OFF_DEVICE_COMMAND_DICT
        )

        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
        )

        # Invoke TelescopeOff() command
        tmc_helper.set_to_off(**ON_OFF_DEVICE_COMMAND_DICT)

        # Verify State transitions after TelescopeOff
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_OFF_INFO, "State"
        )

    except Exception:
        tear_down(release_json, **ON_OFF_DEVICE_COMMAND_DICT)
