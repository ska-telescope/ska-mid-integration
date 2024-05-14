"""
Test cases for recovery of subarray stuck in RESOURCING
ObsState for mid
"""
import json

import pytest
from ska_control_model import ObsState
from ska_tango_testing.mock.placeholders import Anything
from tango import DeviceProxy, EventType

from tests.conftest import LOGGER, TIMEOUT
from tests.resources.test_support.common_utils.common_helpers import (
    Resource,
    Waiter,
)
from tests.resources.test_support.common_utils.telescope_controls import (
    BaseTelescopeControl,
)
from tests.resources.test_support.common_utils.tmc_helpers import (
    TmcHelper,
    tear_down,
)
from tests.resources.test_support.constant import (
    DEVICE_LIST_FOR_CHECK_DEVICES,
    DEVICE_OBS_STATE_ABORT_IN_EMPTY_CSP,
    DEVICE_OBS_STATE_ABORT_IN_EMPTY_SDP,
    DEVICE_OBS_STATE_EMPTY_INFO,
    DEVICE_STATE_ON_INFO,
    DEVICE_STATE_STANDBY_INFO,
    INTERMEDIATE_STATE_DEFECT,
    ON_OFF_DEVICE_COMMAND_DICT,
    centralnode,
    csp_subarray1,
    sdp_subarray1,
    tmc_sdp_subarray_leaf_node,
    tmc_subarraynode1,
)


@pytest.mark.SKA_mid
def test_recover_subarray_stuck_in_resourcing(
    json_factory, change_event_callbacks
):
    """AssignResources and ReleaseResources is executed."""
    assign_json = json_factory("command_AssignResources")
    release_json = json_factory("command_ReleaseResources")
    try:
        telescope_control = BaseTelescopeControl()
        tmc_helper = TmcHelper(centralnode, tmc_subarraynode1)

        tmc_helper.check_devices(DEVICE_LIST_FOR_CHECK_DEVICES)

        # Verify Telescope is Off/Standby
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )
        LOGGER.info("Starting up the Telescope")

        # Invoke TelescopeOn() command on TMC
        tmc_helper.set_to_on(**ON_OFF_DEVICE_COMMAND_DICT)
        LOGGER.info("TelescopeOn command is invoked successfully")

        # Verify State transitions after TelescopeOn#
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_ON_INFO, "State"
        )

        the_waiter = Waiter()
        # Invoke AssignResources() Command on TMC
        LOGGER.info("Invoking AssignResources command on TMC CentralNode")
        sdp_subarray = DeviceProxy(sdp_subarray1)
        central_node = DeviceProxy(centralnode)
        central_node.subscribe_event(
            "longRunningCommandResult",
            EventType.CHANGE_EVENT,
            change_event_callbacks["longRunningCommandResult"],
        )
        sdp_subarray.SetDefective(json.dumps(INTERMEDIATE_STATE_DEFECT))

        # Added this check to ensure that devices are running to avoid
        # random test failures.
        tmc_helper.check_devices(DEVICE_LIST_FOR_CHECK_DEVICES)
        Resource(tmc_subarraynode1).assert_attribute("State").equals("ON")
        Resource(tmc_subarraynode1).assert_attribute("obsState").equals(
            "EMPTY"
        )
        the_waiter.set_wait_for_specific_obsstate(
            "RESOURCING", [tmc_subarraynode1]
        )
        the_waiter.set_wait_for_specific_obsstate("IDLE", [csp_subarray1])
        _, unique_id = central_node.AssignResources(assign_json)
        the_waiter.wait(TIMEOUT)

        sdp_subarray.SetDefective(json.dumps({"enabled": False}))

        assertion_data = change_event_callbacks[
            "longRunningCommandResult"
        ].assert_change_event(
            (unique_id[0], Anything),
            lookahead=7,
        )
        assert "AssignResources" in assertion_data["attribute_value"][0]
        assert (
            "Timeout has occurred, command failed"
            in assertion_data["attribute_value"][1]
        )
        assert (
            tmc_sdp_subarray_leaf_node in assertion_data["attribute_value"][1]
        )
        # as helper don't transition back themselves
        assert Resource(csp_subarray1).get("obsState") == "IDLE"
        assert Resource(sdp_subarray1).get("obsState") == "RESOURCING"
        sdp_subarray.SetDirectObsState(ObsState.EMPTY)
        assert Resource(sdp_subarray1).get("obsState") == "EMPTY"
        csp_subarray = DeviceProxy(csp_subarray1)
        csp_subarray.ReleaseAllResources()
        the_waiter.set_wait_for_specific_obsstate("EMPTY", [csp_subarray1])
        the_waiter.set_wait_for_specific_obsstate("EMPTY", [tmc_subarraynode1])
        the_waiter.wait(TIMEOUT)

        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
        )

        # Invoke TelescopeStandby() command on TMC#
        tmc_helper.set_to_standby(**ON_OFF_DEVICE_COMMAND_DICT)

        # Verify State transitions after TelescopeStandby#
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )
        LOGGER.info("Test complete.")

    except Exception as e:
        LOGGER.info(f"Exception occurred {e}")
        tear_down(release_json, **ON_OFF_DEVICE_COMMAND_DICT)


@pytest.mark.SKA_mid
def test_recover_subarray_stuck_in_resourcing_with_sdp_empty_with_abort(
    json_factory, change_event_callbacks
):
    """AssignResources and ReleaseResources is executed."""
    assign_json = json_factory("command_AssignResources")
    release_json = json_factory("command_ReleaseResources")
    try:
        telescope_control = BaseTelescopeControl()
        tmc_helper = TmcHelper(centralnode, tmc_subarraynode1)

        tmc_helper.check_devices(DEVICE_LIST_FOR_CHECK_DEVICES)

        # Verify Telescope is Off/Standby
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )
        LOGGER.info("Starting up the Telescope")

        # Invoke TelescopeOn() command on TMC
        tmc_helper.set_to_on(**ON_OFF_DEVICE_COMMAND_DICT)
        LOGGER.info("TelescopeOn command is invoked successfully")

        # Verify State transitions after TelescopeOn#
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_ON_INFO, "State"
        )

        the_waiter = Waiter()
        # Invoke AssignResources() Command on TMC
        LOGGER.info("Invoking AssignResources command on TMC CentralNode")
        sdp_subarray = DeviceProxy(sdp_subarray1)
        central_node = DeviceProxy(centralnode)
        central_node.subscribe_event(
            "longRunningCommandResult",
            EventType.CHANGE_EVENT,
            change_event_callbacks["longRunningCommandResult"],
        )

        sdp_subarray.SetDefective(json.dumps(INTERMEDIATE_STATE_DEFECT))

        # Added this check to ensure that devices are running to avoid
        # random test failures.
        tmc_helper.check_devices(DEVICE_LIST_FOR_CHECK_DEVICES)
        Resource(tmc_subarraynode1).assert_attribute("State").equals("ON")
        Resource(tmc_subarraynode1).assert_attribute("obsState").equals(
            "EMPTY"
        )
        the_waiter.set_wait_for_specific_obsstate(
            "RESOURCING", [tmc_subarraynode1]
        )
        the_waiter.set_wait_for_specific_obsstate("IDLE", [csp_subarray1])
        _, unique_id = central_node.AssignResources(assign_json)
        the_waiter.wait(TIMEOUT)

        sdp_subarray.SetDefective(json.dumps({"enabled": False}))

        assertion_data = change_event_callbacks[
            "longRunningCommandResult"
        ].assert_change_event(
            (unique_id[0], Anything),
            lookahead=7,
        )
        assert "AssignResources" in assertion_data["attribute_value"][0]
        assert (
            "Exception occurred on the following devices: "
            "ska_mid/tm_leaf_node/sdp_subarray01"
            in assertion_data["attribute_value"][1]
        )

        assert Resource(csp_subarray1).get("obsState") == "IDLE"
        assert Resource(sdp_subarray1).get("obsState") == "RESOURCING"
        sdp_subarray.SetDirectObsState(ObsState.EMPTY)
        assert Resource(sdp_subarray1).get("obsState") == "EMPTY"

        subarray_node = DeviceProxy(tmc_subarraynode1)
        subarray_node.Abort()

        # Verify ObsState is Aborted
        the_waiter = Waiter()
        the_waiter.set_wait_for_specific_obsstate(
            "ABORTED", [tmc_subarraynode1]
        )
        the_waiter.wait(TIMEOUT)

        # Verify State transitions after Abort#
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_ABORT_IN_EMPTY_SDP, "obsState"
        )

        # Invoke Restart() command on TMC#

        subarray_node.Restart()

        the_waiter = Waiter()
        the_waiter.set_wait_for_specific_obsstate("EMPTY", [tmc_subarraynode1])
        the_waiter.wait(TIMEOUT)

        # Verify ObsState is EMPTY#
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
        )

        # Invoke TelescopeStandby() command on TMC#
        tmc_helper.set_to_standby(**ON_OFF_DEVICE_COMMAND_DICT)

        # Verify State transitions after TelescopeStandby#
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )

        LOGGER.info("Test complete.")

    except Exception:
        tear_down(release_json, **ON_OFF_DEVICE_COMMAND_DICT)


@pytest.mark.skip(
    reason="Abort command is not supported when CSP Subarray is EMPTY"
    + "test scenarios need rethinking"
)
@pytest.mark.SKA_mid
def test_recover_subarray_stuck_in_resourcing_with_csp_empty_with_abort(
    json_factory, change_event_callbacks
):
    """AssignResources and ReleaseResources is executed."""
    assign_json = json_factory("command_AssignResources")
    release_json = json_factory("command_ReleaseResources")
    try:
        telescope_control = BaseTelescopeControl()
        tmc_helper = TmcHelper(centralnode, tmc_subarraynode1)

        tmc_helper.check_devices(DEVICE_LIST_FOR_CHECK_DEVICES)

        # Verify Telescope is Off/Standby
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )
        LOGGER.info("Starting up the Telescope")

        # Invoke TelescopeOn() command on TMC
        tmc_helper.set_to_on(**ON_OFF_DEVICE_COMMAND_DICT)
        LOGGER.info("TelescopeOn command is invoked successfully")

        # Verify State transitions after TelescopeOn#
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_ON_INFO, "State"
        )

        the_waiter = Waiter()
        # Invoke AssignResources() Command on TMC
        LOGGER.info("Invoking AssignResources command on TMC CentralNode")
        csp_subarray = DeviceProxy(csp_subarray1)
        central_node = DeviceProxy(centralnode)
        central_node.subscribe_event(
            "longRunningCommandResult",
            EventType.CHANGE_EVENT,
            change_event_callbacks["longRunningCommandResult"],
        )

        csp_subarray.SetDefective(json.dumps(INTERMEDIATE_STATE_DEFECT))

        # Added this check to ensure that devices are running to avoid
        # random test failures.
        tmc_helper.check_devices(DEVICE_LIST_FOR_CHECK_DEVICES)
        Resource(tmc_subarraynode1).assert_attribute("State").equals("ON")
        Resource(tmc_subarraynode1).assert_attribute("obsState").equals(
            "EMPTY"
        )
        the_waiter.set_wait_for_specific_obsstate(
            "RESOURCING", [tmc_subarraynode1]
        )
        the_waiter.set_wait_for_specific_obsstate("IDLE", [sdp_subarray1])
        _, unique_id = central_node.AssignResources(assign_json)
        the_waiter.wait(TIMEOUT)

        csp_subarray.SetDefective(json.dumps({"enabled": False}))

        assertion_data = change_event_callbacks[
            "longRunningCommandResult"
        ].assert_change_event(
            (unique_id[0], Anything),
            lookahead=7,
        )
        assert "AssignResources" in assertion_data["attribute_value"][0]
        assert (
            "Exception occurred on the following devices: "
            "ska_mid/tm_leaf_node/csp_subarray01"
            in assertion_data["attribute_value"][1]
        )

        assert Resource(csp_subarray1).get("obsState") == "RESOURCING"
        assert Resource(sdp_subarray1).get("obsState") == "IDLE"
        csp_subarray.SetDirectObsState(ObsState.EMPTY)
        assert Resource(csp_subarray1).get("obsState") == "EMPTY"

        subarray_node = DeviceProxy(tmc_subarraynode1)
        subarray_node.Abort()

        # Verify ObsState is Aborted
        the_waiter = Waiter()
        the_waiter.set_wait_for_specific_obsstate(
            "ABORTED", [tmc_subarraynode1]
        )
        the_waiter.wait(TIMEOUT)

        # Verify State transitions after Abort#
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_ABORT_IN_EMPTY_CSP, "obsState"
        )

        # Invoke Restart() command on TMC#

        subarray_node.Restart()

        the_waiter = Waiter()
        the_waiter.set_wait_for_specific_obsstate("EMPTY", [tmc_subarraynode1])
        the_waiter.wait(TIMEOUT)

        # Verify ObsState is EMPTY#
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
        )

        # Invoke TelescopeStandby() command on TMC#
        tmc_helper.set_to_standby(**ON_OFF_DEVICE_COMMAND_DICT)

        # Verify State transitions after TelescopeStandby#
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )

        LOGGER.info("Test complete.")

    except Exception:
        tear_down(release_json, **ON_OFF_DEVICE_COMMAND_DICT)


@pytest.mark.SKA_mid
def test_recover_subarray_stuck_in_resourcing_with_abort(
    json_factory, change_event_callbacks
):
    """AssignResources and ReleaseResources is executed."""
    assign_json = json_factory("command_AssignResources")
    release_json = json_factory("command_ReleaseResources")
    try:
        telescope_control = BaseTelescopeControl()
        tmc_helper = TmcHelper(centralnode, tmc_subarraynode1)

        tmc_helper.check_devices(DEVICE_LIST_FOR_CHECK_DEVICES)

        # Verify Telescope is Off/Standby
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )
        LOGGER.info("Starting up the Telescope")

        # Invoke TelescopeOn() command on TMC
        tmc_helper.set_to_on(**ON_OFF_DEVICE_COMMAND_DICT)
        LOGGER.info("TelescopeOn command is invoked successfully")

        # Verify State transitions after TelescopeOn#
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_ON_INFO, "State"
        )

        the_waiter = Waiter()
        # Invoke AssignResources() Command on TMC
        LOGGER.info("Invoking AssignResources command on TMC CentralNode")
        sdp_subarray = DeviceProxy(sdp_subarray1)
        central_node = DeviceProxy(centralnode)
        central_node.subscribe_event(
            "longRunningCommandResult",
            EventType.CHANGE_EVENT,
            change_event_callbacks["longRunningCommandResult"],
        )
        sdp_subarray.SetDefective(json.dumps(INTERMEDIATE_STATE_DEFECT))

        # Added this check to ensure that devices are running to avoid
        # random test failures.
        tmc_helper.check_devices(DEVICE_LIST_FOR_CHECK_DEVICES)
        Resource(tmc_subarraynode1).assert_attribute("State").equals("ON")
        Resource(tmc_subarraynode1).assert_attribute("obsState").equals(
            "EMPTY"
        )
        the_waiter.set_wait_for_specific_obsstate(
            "RESOURCING", [tmc_subarraynode1]
        )
        the_waiter.set_wait_for_specific_obsstate("IDLE", [csp_subarray1])
        _, unique_id = central_node.AssignResources(assign_json)
        the_waiter.wait(TIMEOUT)

        sdp_subarray.SetDefective(json.dumps({"enabled": False}))

        assertion_data = change_event_callbacks[
            "longRunningCommandResult"
        ].assert_change_event(
            (unique_id[0], Anything),
            lookahead=7,
        )
        assert "AssignResources" in assertion_data["attribute_value"][0]
        assert (
            "Timeout has occurred, command failed"
            in assertion_data["attribute_value"][1]
        )
        assert (
            tmc_sdp_subarray_leaf_node in assertion_data["attribute_value"][1]
        )
        # as helper don't transition back themselves
        assert Resource(csp_subarray1).get("obsState") == "IDLE"
        assert Resource(sdp_subarray1).get("obsState") == "RESOURCING"

        subarray_node = DeviceProxy(tmc_subarraynode1)
        subarray_node.Abort()

        # Verify ObsState is Aborted
        the_waiter = Waiter()
        the_waiter.set_wait_for_specific_obsstate(
            "ABORTED", [tmc_subarraynode1]
        )
        the_waiter.wait(TIMEOUT)

        # Verify State transitions after Abort#
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_ABORT_IN_EMPTY_CSP, "obsState"
        )

        # Invoke Restart() command on TMC#

        subarray_node.Restart()

        the_waiter = Waiter()
        the_waiter.set_wait_for_specific_obsstate("EMPTY", [tmc_subarraynode1])
        the_waiter.wait(TIMEOUT)

        # Verify ObsState is EMPTY#
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
        )

        # Invoke TelescopeStandby() command on TMC#
        tmc_helper.set_to_standby(**ON_OFF_DEVICE_COMMAND_DICT)

        # Verify State transitions after TelescopeStandby#
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )

        LOGGER.info("Test complete.")

    except Exception as e:
        LOGGER.info(f"Exception occurred {e}")
        tear_down(release_json, **ON_OFF_DEVICE_COMMAND_DICT)
