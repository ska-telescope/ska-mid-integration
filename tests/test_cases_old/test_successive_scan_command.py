"""Test successive Scan Command"""
import pytest

from tests.conftest import LOGGER, update_configure_json, update_scan_json
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
    DEVICE_STATE_ON_INFO,
    DEVICE_STATE_STANDBY_INFO,
    ON_OFF_DEVICE_COMMAND_DICT,
    centralnode,
    tmc_subarraynode1,
)


@pytest.mark.skip(
    reason="2nd configure fails in READY aggregation.This test is older one "
    + "so it maybe removed."
)
@pytest.mark.SKA_mid
def test_successive_scan_with_different_configurations(json_factory):
    """Successive Scan command with different configurations."""
    telescope_control = BaseTelescopeControl()
    assign_json = json_factory("command_AssignResources")
    release_json = json_factory("command_ReleaseResources")
    configure_json = json_factory("command_Configure")
    scan_json = json_factory("command_Scan")
    tmc_helper = TmcHelper(centralnode, tmc_subarraynode1)

    try:
        tmc_helper.check_devices(DEVICE_LIST_FOR_CHECK_DEVICES)

        # Verify Telescope is Off/Standby#
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )
        LOGGER.info("Starting up the Telescope")

        # Invoke TelescopeOn() command on TMC#
        tmc_helper.set_to_on(**ON_OFF_DEVICE_COMMAND_DICT)
        LOGGER.info("TelescopeOn command is invoked successfully")

        # Verify State transitions after TelescopeOn#
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_ON_INFO, "State"
        )

        # Invoke AssignResources() Command on TMC#
        tmc_helper.compose_sub(assign_json, **ON_OFF_DEVICE_COMMAND_DICT)
        LOGGER.info("AssignResources command is invoked successfully")

        # Verify ObsState is IDLE#
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_IDLE_INFO, "obsState"
        )

        # Invoke Configure() Command on TMC#
        tmc_helper.configure_subarray(
            configure_json, **ON_OFF_DEVICE_COMMAND_DICT
        )

        # Verify ObsState is READY#
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_READY_INFO, "obsState"
        )

        # Invoke Scan() command on TMC#
        tmc_helper.scan(scan_json, **ON_OFF_DEVICE_COMMAND_DICT)

        # Verify ObsState is READY#
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_READY_INFO, "obsState"
        )

        configure_json_string = update_configure_json(
            configure_json,
            scan_duration=12.0,
            transaction_id="txn-....-00003",
            scan_type="calibration_b",
            config_id="sbi-mvp01-20200325-00001-calibration_b",
        )

        # Invoke Configure() Command on TMC#
        tmc_helper.configure_subarray(
            configure_json_string, **ON_OFF_DEVICE_COMMAND_DICT
        )

        # Verify ObsState is READY#
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_READY_INFO, "obsState"
        )

        scan_json_string = update_scan_json(
            scan_json, scan_id=2, transaction_id="txn-....-00002"
        )

        # Invoke Scan() command on TMC#
        tmc_helper.scan(scan_json_string, **ON_OFF_DEVICE_COMMAND_DICT)

        # Verify ObsState is READY#
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_READY_INFO, "obsState"
        )

        # Verify ObsState is READY#
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_READY_INFO, "obsState"
        )

        configure_json_string = update_configure_json(
            configure_json,
            scan_duration=20,
            transaction_id="txn-....-00003",
            scan_type="target:a",
            config_id="sbi-mvp01-20200325-00001-target:a",
        )

        # Invoke Configure() Command on TMC#
        tmc_helper.configure_subarray(
            configure_json_string, **ON_OFF_DEVICE_COMMAND_DICT
        )

        scan_json_string = update_scan_json(
            scan_json, scan_id=3, transaction_id="txn-....-00003"
        )

        # Invoke Scan() command on TMC#
        tmc_helper.scan(scan_json_string, **ON_OFF_DEVICE_COMMAND_DICT)

        # Verify ObsState is READY#
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_READY_INFO, "obsState"
        )

        # Invoke End() command on TMC#
        tmc_helper.end(**ON_OFF_DEVICE_COMMAND_DICT)

        # Verify ObsState is IDLE#
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_IDLE_INFO, "obsState"
        )

        # Invoke ReleaseResources() Command on TMC#
        tmc_helper.invoke_releaseResources(
            release_json, **ON_OFF_DEVICE_COMMAND_DICT
        )
        LOGGER.info("ReleaseResources command is invoked successfully")

        # Verify ObsState is EMPTY#
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
        )

        # Invoke TelescopeStandby() command on TMC#
        tmc_helper.set_to_standby(**ON_OFF_DEVICE_COMMAND_DICT)
        LOGGER.info("TelescopeStandby command is invoked successfully")

        # Verify State transitions after TelescopeStandby#
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )

        LOGGER.info("Test complete.")

    except Exception:
        tear_down(release_json, **ON_OFF_DEVICE_COMMAND_DICT)


@pytest.mark.skip(
    reason="Scan functionality is broken. It will fixed in SAH-1498"
)
@pytest.mark.SKA_mid
def test_successive_scan_with_same_configurations(json_factory):
    """Successive Scan command with same configurations."""
    telescope_control = BaseTelescopeControl()
    assign_json = json_factory("command_AssignResources")
    release_json = json_factory("command_ReleaseResources")
    configure_json = json_factory("command_Configure")
    scan_json = json_factory("command_Scan")
    tmc_helper = TmcHelper(centralnode, tmc_subarraynode1)

    try:
        tmc_helper.check_devices(DEVICE_LIST_FOR_CHECK_DEVICES)

        # Verify Telescope is Off/Standby#
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )
        LOGGER.info("Starting up the Telescope")

        # Invoke TelescopeOn() command on TMC#
        tmc_helper.set_to_on(**ON_OFF_DEVICE_COMMAND_DICT)

        # Verify State transitions after TelescopeOn#
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_ON_INFO, "State"
        )

        # Invoke AssignResources() Command on TMC#
        tmc_helper.compose_sub(assign_json, **ON_OFF_DEVICE_COMMAND_DICT)

        # Verify ObsState is IDLE#
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_IDLE_INFO, "obsState"
        )

        # Invoke Configure() Command on TMC#
        tmc_helper.configure_subarray(
            configure_json, **ON_OFF_DEVICE_COMMAND_DICT
        )

        # Verify ObsState is READY#
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_READY_INFO, "obsState"
        )

        # Invoke Scan() command on TMC#
        tmc_helper.scan(scan_json, **ON_OFF_DEVICE_COMMAND_DICT)

        # Verify ObsState is READY#
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_READY_INFO, "obsState"
        )

        scan_json_string = update_scan_json(
            scan_json, scan_id=2, transaction_id="txn-....-00002"
        )
        # Invoke Scan() command on TMC#
        tmc_helper.scan(scan_json_string, **ON_OFF_DEVICE_COMMAND_DICT)

        # Verify ObsState is READY#
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_READY_INFO, "obsState"
        )

        scan_json_string = update_scan_json(
            scan_json, scan_id=3, transaction_id="txn-....-00003"
        )

        # Invoke Scan() command on TMC#
        tmc_helper.scan(scan_json_string, **ON_OFF_DEVICE_COMMAND_DICT)

        # Verify ObsState is READY#
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_READY_INFO, "obsState"
        )

        # Invoke End() command on TMC#
        tmc_helper.end(**ON_OFF_DEVICE_COMMAND_DICT)

        # Verify ObsState is IDLE#
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_IDLE_INFO, "obsState"
        )

        # Invoke ReleaseResources() Command on TMC#
        tmc_helper.invoke_releaseResources(
            release_json, **ON_OFF_DEVICE_COMMAND_DICT
        )

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
