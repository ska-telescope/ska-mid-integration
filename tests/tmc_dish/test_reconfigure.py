import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tango import DevState

from tests.conftest import LOGGER
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
    DEVICE_STATE_OFF_INFO,
    ON_OFF_DEVICE_COMMAND_DICT,
    centralnode,
    tmc_subarraynode1,
)
from tests.resources.test_support.enum import DishMode

tmc_helper = TmcHelper(centralnode, tmc_subarraynode1)
telescope_control = BaseTelescopeControl()


@pytest.mark.SKA_mid33
@scenario(
    "../features/tmc_dish/successive_configure_dish.feature",
    "TMC validates reconfigure functionality with real dish",
)
def test_multiple_configure_functionality():
    """
    Test TMC allows multiple configuration

    """


@given("the TMC is On")
def given_tmc(central_node_mid, event_recorder):
    assert central_node_mid.csp_master.ping() > 0
    assert central_node_mid.sdp_master.ping() > 0
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        assert central_node_mid.dish_master_dict[dish_id].ping() > 0
        assert central_node_mid.dish_leaf_node_dict[dish_id].ping() > 0

    central_node_mid.move_to_on()
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "dishMode"
        )
        event_recorder.subscribe_event(
            central_node_mid.dish_leaf_node_dict[dish_id], "dishMode"
        )
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "pointingState"
        )
        event_recorder.subscribe_event(
            central_node_mid.dish_leaf_node_dict[dish_id], "pointingState"
        )
    event_recorder.subscribe_event(central_node_mid.csp_master, "State")
    event_recorder.subscribe_event(central_node_mid.sdp_master, "State")

    assert event_recorder.has_change_event_occurred(
        central_node_mid.csp_master,
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.sdp_master,
        "State",
        DevState.ON,
    )

    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "dishMode",
            DishMode.STANDBY_FP,
        )
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "dishMode",
            DishMode.STANDBY_FP,
            lookahead=15,
        )

    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )

    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )


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
def send_configure(json_factory, input_json1, subarray_node):
    configure_json1 = json_factory(input_json1)
    release_json = json_factory("command_ReleaseResources")
    try:
        LOGGER.info("Invoking Configure command with input_json1")
        # Invoke Configure() command
        # tmc_helper.configure_subarray(
        #     configure_json1, **ON_OFF_DEVICE_COMMAND_DICT
        # )

        _, pytest.unique_id = subarray_node.execute_transition(
            "Configure", configure_json1
        )
        LOGGER.info("Configure1 is invoked successfully")

    except Exception as e:
        LOGGER.info("Exception raised %s ", e)
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
def send_next_configure(json_factory, input_json2, subarray_node):
    configure_json2 = json_factory(input_json2)
    release_json = json_factory("command_ReleaseResources")
    try:
        LOGGER.info("Invoking Configure command with input_json2")
        # Invoke successive Configure() command
        tmc_helper.configure_subarray(
            configure_json2, **ON_OFF_DEVICE_COMMAND_DICT
        )

        _, pytest.unique_id = subarray_node.execute_transition(
            "Configure", configure_json2
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
