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
    DEVICE_STATE_ON_INFO,
    DEVICE_STATE_STANDBY_INFO,
    ON_OFF_DEVICE_COMMAND_DICT,
    centralnode,
    tmc_subarraynode1,
)

configure_resources_file = "command_Configure.json"
assign_resources_file = "command_AssignResources.json"


tmc_helper = TmcHelper(centralnode, tmc_subarraynode1)
telescope_control = BaseTelescopeControl()
result, message = "", ""


@pytest.mark.SKA_mid
@scenario(
    "../features/check_command_not_allowed.feature",
    "Unexpected commands not allowed when TMC subarray is empty",
)
def test_command_not_valid_in_empty_obsState():
    """
    Test commands not allowed in SubarrayNode obsState.EMPTY

    """


@given("the TMC is in ON state")
def given_tmc(json_factory):
    try:
        # Verify Telescope is Off/Standby
        tmc_helper.check_devices(DEVICE_LIST_FOR_CHECK_DEVICES)
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )
        LOGGER.info("Starting up the Telescope")

        # Invoke TelescopeOn() command on TMC CentralNode
        LOGGER.info("Invoking TelescopeOn command on TMC CentralNode")
        tmc_helper.set_to_on(**ON_OFF_DEVICE_COMMAND_DICT)
        LOGGER.info("TelescopeOn command is invoked successfully")

        # Verify State transitions after TelescopeOn
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_ON_INFO, "State"
        )
    except Exception:
        release_json = json_factory("command_ReleaseResources")
        tear_down(release_json, **ON_OFF_DEVICE_COMMAND_DICT)
        LOGGER.info("Tear Down complete. Telescope is in Standby State")


@given("the subarray is in EMPTY obsstate")
def given_tmc_obsState():
    # Verify ObsState is IDLE
    assert telescope_control.is_in_valid_state(
        DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
    )


@when(
    parsers.parse(
        "{unexpected_command} command is invoked, TMC raises exception"
    )
)
def send(json_factory, unexpected_command):
    scan_json = json_factory("command_Scan")
    configure_json = json_factory("command_Configure")
    try:
        if unexpected_command == "Configure":
            with pytest.raises(Exception) as e:
                LOGGER.info("Invoking Configure command on TMC SubarrayNode")
                pytest.command_result = tmc_helper.configure_subarray(
                    configure_json, **ON_OFF_DEVICE_COMMAND_DICT
                )
            assert (
                "Configure command not permitted in observation state"
                in str(e.value)
            )
        elif unexpected_command == "Scan":
            with pytest.raises(Exception) as e:
                LOGGER.info("Invoking Scan command on TMC SubarrayNode")
                pytest.command_result = tmc_helper.scan(
                    scan_json, **ON_OFF_DEVICE_COMMAND_DICT
                )
            assert "Scan command not permitted in observation state" in str(
                e.value
            )
        elif unexpected_command == "End":
            with pytest.raises(Exception) as e:
                LOGGER.info("Invoking End command on TMC SubarrayNode")
                pytest.command_result = tmc_helper.end(
                    **ON_OFF_DEVICE_COMMAND_DICT
                )
            assert "End command not permitted in observation state" in str(
                e.value
            )
        elif unexpected_command == "Abort":
            with pytest.raises(Exception) as e:
                LOGGER.info("Invoking Abort command on TMC SubarrayNode")
                pytest.command_result = tmc_helper.invoke_abort(
                    **ON_OFF_DEVICE_COMMAND_DICT
                )
            assert "Abort command not permitted in observation state" in str(
                e.value
            )
    except Exception as e:
        LOGGER.info(f"Exception occured: {e}")


@then("TMC subarray remains in EMPTY obsstate")
def tmc_status():
    # Verify obsState transitions
    assert telescope_control.is_in_valid_state(
        DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
    )


@then("TMC executes the AssignResources command successfully")
def tmc_accepts_next_commands(json_factory):
    assign_json = json_factory("command_AssignResources")
    release_json = json_factory("command_ReleaseResources")
    try:
        # Invoke AssignResources() Command on TMC
        LOGGER.info("Invoking AssignResources command on TMC CentralNode")
        tmc_helper.compose_sub(assign_json, **ON_OFF_DEVICE_COMMAND_DICT)
        LOGGER.info("AssignResources command is invoked successfully")

        # Verify obsState is IDLE
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_IDLE_INFO, "obsState"
        )
        LOGGER.info("Invoking ReleaseResources command on TMC SubarrayNode")
        tmc_helper.invoke_releaseResources(
            release_json, **ON_OFF_DEVICE_COMMAND_DICT
        )
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_ON_INFO, "State"
        )
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
        )

        LOGGER.info("Invoking Standby command on TMC SubarrayNode")
        tmc_helper.set_to_standby(**ON_OFF_DEVICE_COMMAND_DICT)
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )

        LOGGER.info("Tear Down complete. Telescope is in Standby State")
    except Exception:
        tear_down(release_json, **ON_OFF_DEVICE_COMMAND_DICT)
        LOGGER.info("Tear Down complete. Telescope is in Standby State")
