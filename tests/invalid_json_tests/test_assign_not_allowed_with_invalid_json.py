import json
from copy import deepcopy

import pytest
from pytest_bdd import given, parsers, scenario, then, when

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
    "AssignResource command with invalid JSON is rejected by the TMC",
)
def test_assign_resource_with_invalid_json():
    """
    Test AssignResource command with input as invalid json.

    """


@given("the TMC is in ON state")
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


@given("the subarray is in EMPTY obsState")
def given_subarray_obsstate():
    assert telescope_control.is_in_valid_state(
        DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
    )


@when(
    parsers.parse(
        "the command AssignResources is invoked with {invalid_json} input"
    )
)
def send(json_factory, invalid_json):
    device_params = deepcopy(ON_OFF_DEVICE_COMMAND_DICT)
    device_params["set_wait_for_obsstate"] = False
    assign_json = json_factory("command_AssignResources")
    release_json = json_factory("command_ReleaseResources")
    try:
        assign_json = json.loads(assign_json)
        if invalid_json == "missing_pb_id_key":
            del assign_json["sdp"]["processing_blocks"][0]["pb_id"]
            pytest.command_result = tmc_helper.compose_sub(
                json.dumps(assign_json), **device_params
            )
        elif invalid_json == "missing_scan_type_id_key":
            del assign_json["sdp"]["execution_block"]["scan_types"][0][
                "scan_type_id"
            ]
            pytest.command_result = tmc_helper.compose_sub(
                json.dumps(assign_json), **device_params
            )
        elif invalid_json == "missing_count_key":
            del assign_json["sdp"]["execution_block"]["channels"][0][
                "channels_id"
            ]
            pytest.command_result = tmc_helper.compose_sub(
                json.dumps(assign_json), **device_params
            )
        elif invalid_json == "missing_receptor_id_key":
            del assign_json["dish"]["receptor_ids"]
            pytest.command_result = tmc_helper.compose_sub(
                json.dumps(assign_json), **device_params
            )
    except Exception as e:
        LOGGER.exception(f"Exception occured: {e}")
        tear_down(release_json, **ON_OFF_DEVICE_COMMAND_DICT)


@then(parsers.parse("TMC should reject the AssignResources command"))
def invalid_command_rejection():
    assert (
        "JSON validation error: data is not compliant"
    ) in pytest.command_result[1][0]

    assert pytest.command_result[0][0] == ResultCode.REJECTED


@then("TMC subarray remains in EMPTY obsState")
def tmc_status():
    # Verify obsState transitions
    assert telescope_control.is_in_valid_state(
        DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
    )


@then(
    "TMC successfully executes AssignResources \
for subarray with a valid input json"
)
def tmc_accepts_command_with_valid_json(json_factory):
    try:
        assign_json = json_factory("command_AssignResources")
        release_json = json_factory("command_ReleaseResources")

        # Invoke AssignResources() Command on TMC
        LOGGER.info("Invoking AssignResources command on TMC CentralNode")
        tmc_helper.compose_sub(assign_json, **ON_OFF_DEVICE_COMMAND_DICT)
        LOGGER.info("AssignResources command is invoked successfully")

        # Verify obsState is IDLE
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_IDLE_INFO, "obsState"
        )

        # tear down
        tmc_helper.invoke_releaseResources(
            release_json, **ON_OFF_DEVICE_COMMAND_DICT
        )
        assert telescope_control.is_in_valid_state(
            DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
        )
        tmc_helper.set_to_standby(**ON_OFF_DEVICE_COMMAND_DICT)
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )
        LOGGER.info("Tests complete.")
    except Exception:
        tear_down(release_json, **ON_OFF_DEVICE_COMMAND_DICT)
