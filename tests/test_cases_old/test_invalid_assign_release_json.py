"""Test cases for AssignResources input json"""
import pytest
from tango import DeviceProxy

from tests.conftest import LOGGER
from tests.resources.test_support.common_utils.result_code import ResultCode
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
    DEVICE_STATE_ON_INFO,
    DEVICE_STATE_STANDBY_INFO,
    ON_OFF_DEVICE_COMMAND_DICT,
    centralnode,
    tmc_subarraynode1,
)

telescope_control = BaseTelescopeControl()
tmc_helper = TmcHelper(centralnode, tmc_subarraynode1)


@pytest.mark.SKA_mid
def test_assign_invalid_json(json_factory):
    """Test assign resources command with
    with invalid json"""
    try:
        # AssignResources and ReleaseResources is executed.
        assign_json = json_factory("command_invalid_assign_release")
        tmc_helper.check_devices(DEVICE_LIST_FOR_CHECK_DEVICES)
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )
        # Invoke TelescopeOn() command on TMC CentralNode
        tmc_helper.set_to_on(**ON_OFF_DEVICE_COMMAND_DICT)
        # Verify State transitions after TelescopeOn
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_ON_INFO, "State"
        )
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
        )
        #  Invoke AssignResources() Command on TMC
        central_node = DeviceProxy(centralnode)
        tmc_helper.check_devices(DEVICE_LIST_FOR_CHECK_DEVICES)
        ret_code, message = central_node.AssignResources(assign_json)

        # Assert with TaskStatus as REJECTED
        assert ret_code == ResultCode.REJECTED
        LOGGER.info(message)

        # Verify ObsState is EMPTY
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
        )

        # Invoke TelescopeStandby() command on TMC
        tmc_helper.set_to_standby(**ON_OFF_DEVICE_COMMAND_DICT)
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )

        LOGGER.info("Tests complete.")
    except Exception:
        tear_down(**ON_OFF_DEVICE_COMMAND_DICT)


@pytest.mark.SKA_mid
def test_release_invalid_json(json_factory):
    """Test release with invalid json"""
    assign_json = json_factory("command_AssignResources")
    release_json = json_factory("command_ReleaseResources")
    invalid_release_json = json_factory("command_invalid_assign_release")
    try:
        # AssignResources and ReleaseResources is executed.
        tmc_helper.check_devices(DEVICE_LIST_FOR_CHECK_DEVICES)
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )
        # Invoke TelescopeOn() command on TMC CentralNode
        tmc_helper.set_to_on(**ON_OFF_DEVICE_COMMAND_DICT)
        # Verify State transitions after TelescopeOn
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_ON_INFO, "State"
        )
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
        )

        # Invoke AssignResources() Command on TMC
        tmc_helper.compose_sub(assign_json, **ON_OFF_DEVICE_COMMAND_DICT)
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_IDLE_INFO, "obsState"
        )

        # Invoke ReleaseResources() command on TMC
        central_node = DeviceProxy(centralnode)
        ret_code, message = central_node.ReleaseResources(invalid_release_json)
        # Assert with TaskStatus as REJECTED
        assert ret_code == ResultCode.REJECTED
        LOGGER.info(message)

        # Check if telescope is in previous state
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_IDLE_INFO, "obsState"
        )

        # Invoke ReleaseResources() command on TMC
        tmc_helper.invoke_releaseResources(
            release_json, **ON_OFF_DEVICE_COMMAND_DICT
        )
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
        )

        # Check Telescope availability
        tmc_helper.check_telescope_availability()
        # Invoke Standby() command on TMC
        tmc_helper.set_to_standby(**ON_OFF_DEVICE_COMMAND_DICT)
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )
    except Exception as e:
        LOGGER.exception("The exception is: %s", e)
        tear_down(release_json, **ON_OFF_DEVICE_COMMAND_DICT)


@pytest.mark.SKA_mid
def test_invalid_receptor_ids(json_factory):
    """AssignResources and ReleaseResources is executed."""
    assign_json = json_factory("command_assign_resources_invalid_receptor_id")
    release_json = json_factory("command_ReleaseResources")
    try:
        # AssignResources and ReleaseResources is executed.
        tmc_helper.check_devices(DEVICE_LIST_FOR_CHECK_DEVICES)
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )
        # Invoke TelescopeOn() command on TMC CentralNode
        tmc_helper.set_to_on(**ON_OFF_DEVICE_COMMAND_DICT)
        # Verify State transitions after TelescopeOn
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_ON_INFO, "State"
        )
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
        )
        try:
            central_node = DeviceProxy(centralnode)
            pytest.command_result = central_node.AssignResources(assign_json)
        except Exception as e:
            LOGGER.exception("The Exception is %s", e)
            tear_down(release_json, **ON_OFF_DEVICE_COMMAND_DICT)
        assert (
            "The dish id 0001 is not of the correct length."
            in pytest.command_result[1][0]
        )
        assert pytest.command_result[0][0] == ResultCode.REJECTED

        # Invoke Standby() command on TMC
        tmc_helper.set_to_standby(**ON_OFF_DEVICE_COMMAND_DICT)
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )
    except Exception as e:
        LOGGER.exception("The exception is: %s", e)
        tear_down(release_json, **ON_OFF_DEVICE_COMMAND_DICT)
