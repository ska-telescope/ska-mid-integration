import pytest
from pytest_bdd import given, parsers, scenario, then, when
from tango import DeviceProxy, EventType

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
    DEVICE_OBS_STATE_ABORT_INFO,
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


@pytest.mark.skip(
    reason="Scan functionality is broken. It will fixed in SAH-1498"
)
@pytest.mark.SKA_mid
@scenario(
    "../features/check_command_not_allowed.feature",
    "Unexpected commands not allowed when TMC subarray is READY",
)
def test_command_not_valid_in_ready_obsState():
    """
    Test commands not allowed in SubarrayNode obsState.READY

    """


@given("the TMC is in ON state")
def given_tmc(json_factory):
    release_json = json_factory("command_ReleaseResources")
    try:
        # Verify Telescope is Off/Standby
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )
        LOGGER.info("Starting up the Telescope")

        # Invoke TelescopeOn() command on TMC
        tmc_helper.set_to_on(**ON_OFF_DEVICE_COMMAND_DICT)
        LOGGER.info("TelescopeOn command is invoked successfully")

        # Verify State transitions after TelescopeOn
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_ON_INFO, "State"
        )
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
        )
    except Exception:
        tear_down(release_json, **ON_OFF_DEVICE_COMMAND_DICT)
        LOGGER.info("Tear Down complete. Telescope is in Standby State")


@given("the subarray is in READY obsState")
def given_tmc_obsState(json_factory):
    assign_json = json_factory("command_AssignResources")
    configure_json = json_factory("command_Configure")
    release_json = json_factory("command_ReleaseResources")
    try:
        # Invoke AssignResources() Command on TMC
        tmc_helper.compose_sub(assign_json, **ON_OFF_DEVICE_COMMAND_DICT)
        LOGGER.info("AssignResources command is invoked successfully")

        # Verify ObsState is IDLE
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_IDLE_INFO, "obsState"
        )

        # Invoke Configure() Command on TMC
        tmc_helper.configure_subarray(
            configure_json, **ON_OFF_DEVICE_COMMAND_DICT
        )
        LOGGER.info("Configure command is invoked successfully")

        # Verify ObsState is READY
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_READY_INFO, "obsState"
        )
    except Exception:
        tear_down(release_json, **ON_OFF_DEVICE_COMMAND_DICT)
        LOGGER.info("Tear Down complete. Telescope is in Standby State")


@when(
    parsers.parse(
        "{unexpected_command} command is invoked, TMC raises exception"
    )
)
def send(json_factory, unexpected_command):
    assign_json = json_factory("command_AssignResources")
    release_json = json_factory("command_ReleaseResources")

    if unexpected_command == "AssignResources":
        with pytest.raises(Exception) as e:
            LOGGER.info("Invoking AssignResources command on TMC CentralNode")
            central_node = DeviceProxy(centralnode)
            tmc_helper.check_devices(DEVICE_LIST_FOR_CHECK_DEVICES)
            pytest.command_result = central_node.AssignResources(assign_json)
            LOGGER.info(f"pytest result: {pytest.command_result}")
        assert (
            "AssignResources command not permitted in observation state"
            in str(e.value)
        )
    elif unexpected_command == "ReleaseResources":
        with pytest.raises(Exception) as e:
            LOGGER.info("Invoking ReleaseResources command on TMC CentralNode")
            central_node = DeviceProxy(centralnode)
            tmc_helper.check_devices(DEVICE_LIST_FOR_CHECK_DEVICES)
            pytest.command_result = central_node.ReleaseResources(release_json)
            LOGGER.info(f"pytest result: {pytest.command_result}")
        assert (
            "ReleaseResources command not permitted in observation state"
            in str(e.value)
        )
    elif unexpected_command == "EndScan":
        with pytest.raises(Exception) as e:
            LOGGER.info("Invoking EndScan command on TMC SubarrayNode")
            tmc_helper.invoke_endscan_in_ready(**ON_OFF_DEVICE_COMMAND_DICT)
        LOGGER.info("EndScan command failed with exception %s", e)
        assert "EndScan command not permitted in observation state" in str(
            e.value
        )


@then("TMC subarray remains in READY obsState")
def tmc_status():
    # Verify SubarrayNode obsState
    assert telescope_control.is_in_valid_state(
        DEVICE_OBS_STATE_READY_INFO, "obsState"
    )


@then(
    parsers.parse("TMC executes the {permitted_command} command successfully")
)
def tmc_accepts_next_commands(
    json_factory, permitted_command, change_event_callbacks
):
    configure_json = json_factory("command_Configure_2")
    scan_file = json_factory("command_Scan")
    release_json = json_factory("command_ReleaseResources")
    try:
        if permitted_command == "Configure":
            pytest.command_result = tmc_helper.configure_subarray(
                configure_json, **ON_OFF_DEVICE_COMMAND_DICT
            )
            LOGGER.info("Invoking Configure command on TMC SubarrayNode")
            subarray_node_proxy = DeviceProxy(tmc_subarraynode1)
            subarray_node_proxy.subscribe_event(
                "longRunningCommandResult",
                EventType.CHANGE_EVENT,
                change_event_callbacks["longRunningCommandResult"],
            )
            assert telescope_control.is_in_valid_state(
                DEVICE_OBS_STATE_READY_INFO, "obsState"
            )
            change_event_callbacks[
                "longRunningCommandResult"
            ].assert_change_event(
                (pytest.command_result[1][0], str(ResultCode.OK.value)),
                lookahead=4,
            )
            LOGGER.info("Tear down")
            tmc_helper.end(**ON_OFF_DEVICE_COMMAND_DICT)
            LOGGER.info("Invoking End command on TMC SubarrayNode")
            assert telescope_control.is_in_valid_state(
                DEVICE_OBS_STATE_IDLE_INFO, "obsState"
            )
            tmc_helper.invoke_releaseResources(
                release_json, **ON_OFF_DEVICE_COMMAND_DICT
            )
            LOGGER.info(
                "Invoking ReleaseResources command on TMC \
            SubarrayNode"
            )
            assert telescope_control.is_in_valid_state(
                DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
            )
            tmc_helper.set_to_standby(**ON_OFF_DEVICE_COMMAND_DICT)
            LOGGER.info("Invoking Standby command on TMC SubarrayNode")
            assert telescope_control.is_in_valid_state(
                DEVICE_STATE_STANDBY_INFO, "State"
            )

        if permitted_command == "Scan":
            tmc_helper.scan(scan_file, **ON_OFF_DEVICE_COMMAND_DICT)
            LOGGER.info("Invoking Scan command on TMC SubarrayNode")
            assert telescope_control.is_in_valid_state(
                DEVICE_OBS_STATE_READY_INFO, "obsState"
            )
            tmc_helper.end(**ON_OFF_DEVICE_COMMAND_DICT)
            LOGGER.info("Invoking End command on TMC SubarrayNode")
            assert telescope_control.is_in_valid_state(
                DEVICE_OBS_STATE_IDLE_INFO, "obsState"
            )
            tmc_helper.invoke_releaseResources(
                release_json, **ON_OFF_DEVICE_COMMAND_DICT
            )
            LOGGER.info(
                "Invoking ReleaseResources command on TMC SubarrayNode"
            )
            assert telescope_control.is_in_valid_state(
                DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
            )
            tmc_helper.set_to_standby(**ON_OFF_DEVICE_COMMAND_DICT)
            LOGGER.info("Invoking Standby command on TMC SubarrayNode")
            assert telescope_control.is_in_valid_state(
                DEVICE_STATE_STANDBY_INFO, "State"
            )

        if permitted_command == "End":
            tmc_helper.end(**ON_OFF_DEVICE_COMMAND_DICT)
            LOGGER.info("Invoking End command on TMC SubarrayNode")
            assert telescope_control.is_in_valid_state(
                DEVICE_OBS_STATE_IDLE_INFO, "obsState"
            )
            tmc_helper.invoke_releaseResources(
                release_json, **ON_OFF_DEVICE_COMMAND_DICT
            )
            LOGGER.info(
                "Invoking ReleaseResources command on TMC SubarrayNode"
            )
            assert telescope_control.is_in_valid_state(
                DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
            )
            tmc_helper.set_to_standby(**ON_OFF_DEVICE_COMMAND_DICT)
            LOGGER.info("Invoking Standby command on TMC SubarrayNode")
            assert telescope_control.is_in_valid_state(
                DEVICE_STATE_STANDBY_INFO, "State"
            )

        if permitted_command == "Abort":
            tmc_helper.invoke_abort(**ON_OFF_DEVICE_COMMAND_DICT)
            LOGGER.info("Invoking Abort command on TMC SubarrayNode")
            assert telescope_control.is_in_valid_state(
                DEVICE_OBS_STATE_ABORT_INFO, "obsState"
            )
            tmc_helper.invoke_restart(**ON_OFF_DEVICE_COMMAND_DICT)
            LOGGER.info("Invoking Restart command on TMC SubarrayNode")
            assert telescope_control.is_in_valid_state(
                DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
            )
            tmc_helper.set_to_standby(**ON_OFF_DEVICE_COMMAND_DICT)
            LOGGER.info("Invoking Standby command on TMC SubarrayNode")
            assert telescope_control.is_in_valid_state(
                DEVICE_STATE_STANDBY_INFO, "State"
            )

    except Exception:
        tear_down(release_json, **ON_OFF_DEVICE_COMMAND_DICT)
        LOGGER.info("Tear Down complete. Telescope is in Standby State")
