import json
from copy import deepcopy

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


@pytest.mark.SKA_mid
@scenario(
    "../features/check_invalid_json_not_allowed.feature",
    "Invalid json rejected by TMC for Configure command",
)
def test_invalid_json_in_configure_obsState():
    """
    Test SubarrayNode Mid Configure command with invalid json data.
    """


@given("the TMC is On")
def given_tmc(json_factory):
    release_json = json_factory("command_ReleaseResources")
    try:
        # Verify Telescope is Off/Standby
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )

        # Invoke TelescopeOn() command on TMC CentralNode
        LOGGER.info("Invoking TelescopeOn command on TMC CentralNode")
        tmc_helper.set_to_on(**ON_OFF_DEVICE_COMMAND_DICT)

        # Verify State transitions after TelescopeOn
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_ON_INFO, "State"
        )

    except Exception:
        tear_down(release_json, **ON_OFF_DEVICE_COMMAND_DICT)


@given("the subarray is in IDLE obsState")
def tmc_check_status(json_factory):
    assert telescope_control.is_in_valid_state(
        DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
    )
    assign_json = json_factory("command_AssignResources")
    LOGGER.info("Invoking AssignResources command on TMC CentralNode")
    tmc_helper.compose_sub(assign_json, **ON_OFF_DEVICE_COMMAND_DICT)

    # Verify ObsState is IDLE
    assert telescope_control.is_in_valid_state(
        DEVICE_OBS_STATE_IDLE_INFO, "obsState"
    )


@when(
    parsers.parse("the command Configure is invoked with {invalid_json} input")
)
def send(json_factory, invalid_json):
    release_json = json_factory("command_ReleaseResources")
    device_params = deepcopy(ON_OFF_DEVICE_COMMAND_DICT)
    device_params["set_wait_for_obsstate"] = False
    try:
        configure_json = json_factory("command_Configure")
        invalid_configure_json = json.loads(configure_json)
        if invalid_json == "config_id_key_missing":
            del invalid_configure_json["csp"]["common"]["config_id"]
            pytest.command_result = tmc_helper.configure_subarray(
                json.dumps(invalid_configure_json), **device_params
            )
        elif invalid_json == "fsp_id_key_missing":
            del invalid_configure_json["csp"]["cbf"]["fsp"][0]["fsp_id"]
            pytest.command_result = tmc_helper.configure_subarray(
                json.dumps(invalid_configure_json), **device_params
            )
        # skip reason: takes more time to complete configure command
        # elif invalid_json == "frequency_slice_id_key_missing":
        #     del invalid_configure_json["csp"]["cbf"]["fsp"][0][
        #         "frequency_slice_id"
        #     ]
        #     pytest.command_result = tmc_helper.configure_subarray(
        #         json.dumps(invalid_configure_json), **device_params
        #     )
        elif invalid_json == "integration_factor_key_missing":
            del invalid_configure_json["csp"]["cbf"]["fsp"][0][
                "integration_factor"
            ]
            pytest.command_result = tmc_helper.configure_subarray(
                json.dumps(invalid_configure_json), **device_params
            )
        elif invalid_json == "zoom_factor_key_missing":
            del invalid_configure_json["csp"]["cbf"]["fsp"][0]["zoom_factor"]
            pytest.command_result = tmc_helper.configure_subarray(
                json.dumps(invalid_configure_json), **device_params
            )
        elif invalid_json == "incorrect_fsp_id":
            invalid_configure_json["csp"]["cbf"]["fsp"][0]["fsp_id"] = 30
            pytest.command_result = tmc_helper.configure_subarray(
                json.dumps(invalid_configure_json), **device_params
            )
    except Exception as e:
        LOGGER.exception(f"Exception occurred: {e}")
        tear_down(release_json, **ON_OFF_DEVICE_COMMAND_DICT)


@then(
    parsers.parse(
        "the TMC should reject the {invalid_json} with ResultCode.Rejected"
    )
)
def invalid_command_rejection(invalid_json):
    # asserting validation resultcode
    assert pytest.command_result[0][0] == ResultCode.REJECTED
    # asserting validations message as per invalid json
    if invalid_json == "config_id_key_missing":
        assert (
            "'config_id': ['Missing data for required field.']"
            in pytest.command_result[1][0]
        )
    elif invalid_json == "incorrect_fsp_id":
        assert (
            "FSP ID must be in range 1..27. Got 30"
            in pytest.command_result[1][0]
        )
    elif invalid_json in [
        "fsp_id_key_missing",
        # "frequency_slice_id_key_missing",
        "zoom_factor_key_missing",
        "integration_factor_key_missing",
    ]:
        assert "Malformed input string" in pytest.command_result[1][0]


@then("TMC subarray remains in IDLE obsState")
def tmc_status():
    # Verify obsState transitions
    assert telescope_control.is_in_valid_state(
        DEVICE_OBS_STATE_IDLE_INFO, "obsState"
    )


@then(
    "TMC successfully executes the Configure \
command for the subarray with a valid json"
)
def tmc_accepts_next_commands(json_factory, change_event_callbacks):
    release_json = json_factory("command_ReleaseResources")
    try:
        configure_json = json_factory("command_Configure")
        LOGGER.info("Invoking Configure command on TMC SubarrayNode")
        pytest.command_result = tmc_helper.configure_subarray(
            configure_json, **ON_OFF_DEVICE_COMMAND_DICT
        )
        subarray_node_proxy = DeviceProxy(tmc_subarraynode1)
        subarray_node_proxy.subscribe_event(
            "longRunningCommandResult",
            EventType.CHANGE_EVENT,
            change_event_callbacks["longRunningCommandResult"],
        )
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_READY_INFO, "obsState"
        )
        change_event_callbacks["longRunningCommandResult"].assert_change_event(
            (pytest.command_result[1][0], str(ResultCode.OK.value)),
            lookahead=4,
        )
        # teardown
        LOGGER.info("Invoking END on TMC")
        tmc_helper.end(**ON_OFF_DEVICE_COMMAND_DICT)

        #  Verify obsState is IDLE
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_IDLE_INFO, "obsState"
        )

        LOGGER.info("Invoking ReleaseResources on TMC")
        tmc_helper.invoke_releaseResources(
            release_json, **ON_OFF_DEVICE_COMMAND_DICT
        )

        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
        )

        LOGGER.info("Invoking Telescope Standby on TMC")
        tmc_helper.set_to_standby(**ON_OFF_DEVICE_COMMAND_DICT)

        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )
        LOGGER.info("Tear Down complete. Telescope is in Standby State")
    except Exception:
        tear_down(release_json, **ON_OFF_DEVICE_COMMAND_DICT)
