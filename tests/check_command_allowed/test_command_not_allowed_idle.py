import pytest
from pytest_bdd import given, parsers, scenario, then, when

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
    DEVICE_STATE_ON_INFO,
    DEVICE_STATE_STANDBY_INFO,
    ON_OFF_DEVICE_COMMAND_DICT,
    centralnode,
    tmc_subarraynode1,
)

tmc_helper = TmcHelper(centralnode, tmc_subarraynode1)
telescope_control = BaseTelescopeControl()
result, message = "", ""


@pytest.mark.SKA_mid
@scenario(
    "../features/check_command_not_allowed.feature",
    "Unexpected commands not allowed when TMC subarray is idle",
)
def test_command_not_valid_in_idle_obsState():
    """
    Test commands not allowed in SubarrayNode obsState.IDLE

    """


@given("the TMC is in ON state")
def given_tmc(json_factory):
    # Verify Telescope is Off/Standby
    try:
        tmc_helper.check_devices(DEVICE_LIST_FOR_CHECK_DEVICES)
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )
        LOGGER.info("Starting up the Telescope")

        # Invoke TelescopeOn() command on TMC
        LOGGER.info("Invoking TelescopeOn command on TMC CentralNode")
        tmc_helper.set_to_on(**ON_OFF_DEVICE_COMMAND_DICT)
        LOGGER.info("TelescopeOn command is invoked successfully")

        # Verify State transitions after TelescopeOn
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_ON_INFO, "State"
        )
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
        )

        assign_json = json_factory("command_AssignResources")
        LOGGER.info("Invoking AssignResources command on TMC CentralNode")
        tmc_helper.compose_sub(assign_json, **ON_OFF_DEVICE_COMMAND_DICT)
        LOGGER.info("AssignResources command is invoked successfully")
    except Exception:
        release_json = json_factory("command_ReleaseResources")
        tear_down(release_json, **ON_OFF_DEVICE_COMMAND_DICT)
        LOGGER.info("Tear Down complete. Telescope is in Standby State")


@given("the subarray is in IDLE")
def given_tmc_obsState():
    # Verify ObsState is IDLE
    assert telescope_control.is_in_valid_state(
        DEVICE_OBS_STATE_IDLE_INFO, "obsState"
    )


@when(
    parsers.parse(
        "{unexpected_command} command is invoked, TMC raises exception"
    )
)
def send(json_factory, unexpected_command):
    scan_json = json_factory("command_Scan")
    try:
        with pytest.raises(Exception) as e:
            LOGGER.info("Invoking Scan command on TMC SubarrayNode")
            tmc_helper.scan(scan_json, **ON_OFF_DEVICE_COMMAND_DICT)
        assert (
            f"{unexpected_command} command not permitted in observation state"
            in str(e.value)
        )
    except Exception as e:
        LOGGER.info(f"Exception occured : {e}")


@then("TMC subarray remains in IDLE obsState")
def tmc_status():
    # Verify SubarrayNode obsState
    assert telescope_control.is_in_valid_state(
        DEVICE_OBS_STATE_IDLE_INFO, "obsState"
    )


@then(
    parsers.parse("TMC executes the {permitted_command} command successfully")
)
def tmc_accepts_next_commands(json_factory, permitted_command):
    configure_json = json_factory("command_Configure")
    release_json = json_factory("command_ReleaseResources")
    try:
        if permitted_command == "Configure":
            LOGGER.info(f"permitted command is: {permitted_command}")
            LOGGER.info("Invoking Configure command on TMC CentralNode")
            tmc_helper.configure_sub(
                configure_json, **ON_OFF_DEVICE_COMMAND_DICT
            )
            assert telescope_control.is_in_valid_state(
                DEVICE_OBS_STATE_READY_INFO, "obsState"
            )
            LOGGER.info("Invoking End command on TMC SubarrayNode")
            tmc_helper.end(**ON_OFF_DEVICE_COMMAND_DICT)
            LOGGER.info("End command on TMC SubarrayNode is successful")
            assert telescope_control.is_in_valid_state(
                DEVICE_OBS_STATE_IDLE_INFO, "obsState"
            )
            tmc_helper.invoke_releaseResources(
                release_json, **ON_OFF_DEVICE_COMMAND_DICT
            )
            LOGGER.info(
                "ReleaseResources command on TMC SubarrayNode is successful"
            )
            tmc_helper.set_to_standby(**ON_OFF_DEVICE_COMMAND_DICT)
            LOGGER.info(
                "ReleaseResources command on TMC SubarrayNode is successful"
            )
            assert telescope_control.is_in_valid_state(
                DEVICE_STATE_STANDBY_INFO, "State"
            )
        elif permitted_command == "ReleaseResources":
            LOGGER.info(f"permitted command is: {permitted_command}")
            LOGGER.info(
                "Invoking ReleaseResources command on TMC SubarrayNode"
            )
            tmc_helper.invoke_releaseResources(
                release_json, **ON_OFF_DEVICE_COMMAND_DICT
            )
            assert telescope_control.is_in_valid_state(
                DEVICE_STATE_ON_INFO, "State"
            )
            assert telescope_control.is_in_valid_state(
                DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
            )
            tmc_helper.set_to_standby(**ON_OFF_DEVICE_COMMAND_DICT)
            LOGGER.info(
                "ReleaseResources command on TMC SubarrayNode is successful"
            )
            assert telescope_control.is_in_valid_state(
                DEVICE_STATE_STANDBY_INFO, "State"
            )
    except Exception:
        tear_down(release_json, **ON_OFF_DEVICE_COMMAND_DICT)
        LOGGER.info("Tear Down complete. Telescope is in Standby State")
