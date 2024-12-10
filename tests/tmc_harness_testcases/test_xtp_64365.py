"""Test module for verification """

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer

from tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
from tests.resources.test_harness.constant import COMMAND_COMPLETED
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_harness.subarray_node import SubarrayNodeWrapper
from tests.resources.test_harness.utils.common_utils import (
    JsonFactory,
    turn_on_telescope,
)
from tests.resources.test_support.enum import DishMode, PointingState

TIMEOUT = 60


@pytest.mark.skip(reason="Test scenario needs to be updated")
@pytest.mark.SKA_mid
@scenario(
    "../features/xtp-64365.feature",
    "TMC mid executes Abort command on DISH with pointingState READY",
)
def test_tmc_dish_abort():
    """
    Test case to verify TMC-DISH Abort functionality
    """


@given(
    parsers.parse(
        "TMC subarray {subarray_id} with {dish_ids} is in obsState CONFIGURING"
    )
)
def move_subarray_obsState_to_ready(
    subarray_node: SubarrayNodeWrapper,
    command_input_factory: JsonFactory,
    event_tracer: TangoEventTracer,
    central_node_mid: CentralNodeWrapperMid,
    subarray_id: str,
    dish_ids: str,
):
    """
    Method to move subarray in Ready obsState

    Args:
        subarray_node: Fixture for a Subarray Node wrapper class
        command_input_factory: fixture for creating input required
        for command
        event_recorder: Fixture for EventRecorder class
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        subarray_id (str): Subarray ID
    """

    turn_on_telescope(central_node_mid, event_tracer, dish_ids)
    central_node_mid.set_subarray_id(subarray_id)
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )

    _, pytest.unique_id = central_node_mid.store_resources(assign_input_json)
    event_tracer.subscribe_event(subarray_node.subarray_node, "obsState")
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray must be in the IDLE obsState'"
        "TMC Subarray device"
        f"({subarray_node.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    event_tracer.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray is in IDLE obsState'"
        "TMC Central Node device"
        f"({central_node_mid.central_node.dev_name()}) "
        "is expected have longRunningCommand as"
        f"(unique_id,{COMMAND_COMPLETED})",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (pytest.unique_id[0], COMMAND_COMPLETED),
    )

    event_tracer.subscribe_event(
        subarray_node.csp_subarray_leaf_node, "cspSubarrayObsState"
    )
    event_tracer.subscribe_event(
        subarray_node.sdp_subarray_leaf_node, "sdpSubarrayObsState"
    )
    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    subarray_node.execute_transition("Configure", configure_input_json)
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the CSP Subarray Leaf Node must be in the CONFIGURING obsState'"
        "TMC CSP Subarray Leaf Node device"
        f"({subarray_node.csp_subarray_leaf_node.dev_name()}) "
        "is expected to be in CONFIGURING obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node.csp_subarray_leaf_node,
        "cspSubarrayObsState",
        ObsState.CONFIGURING,
    )

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the CDP Subarray Leaf Node must be in the CONFIGURING obsState'"
        "TMC CSP Subarray Leaf Node device"
        f"({subarray_node.sdp_subarray_leaf_node.dev_name()}) "
        "is expected to be in CONFIGURING obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node.sdp_subarray_leaf_node,
        "sdpSubarrayObsState",
        ObsState.CONFIGURING,
    )

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray must be in the CONFIGURING obsState'"
        "TMC Subarray device"
        f"({subarray_node.subarray_node.dev_name()}) "
        "is expected to be in CONFIGURING obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.CONFIGURING,
    )


@given(
    parsers.parse(
        "DishMaster {dish_ids} is in dishMode OPERATE with pointingState READY"
    )
)
def check_dish_mode_and_pointing_state_after_configure(
    central_node_mid: CentralNodeWrapperMid,
    dish_ids: str,
    event_tracer: TangoEventTracer,
):
    """
    Method to check dishMode and pointingState of DISH after Configure command

    Args:
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        dish_ids (str): Comma-separated IDs of DISH components.
    """
    for dish_id in dish_ids.split(","):
        event_tracer.subscribe_event(
            central_node_mid.dish_leaf_node_dict[dish_id], "dishMode"
        )
        event_tracer.subscribe_event(
            central_node_mid.dish_leaf_node_dict[dish_id], "pointingState"
        )

    for dish_id in dish_ids.split(","):
        # central_node_mid.dish_master_dict[dish_id].SetDirectDishMode(
        #     DishMode.OPERATE
        # )
        central_node_mid.dish_master_dict[dish_id].SetDirectPointingState(
            PointingState.READY
        )

    for dish_id in dish_ids.split(","):
        assert_that(event_tracer).described_as(
            'FAILED ASSUMPTION IN "GIVEN" STEP: '
            "'the DishLeafNode must be in the OPERATE dishMode'"
            "dish device"
            f"({central_node_mid.dish_leaf_node_dict[dish_id].dev_name()}) "
            "is expected to be in OPERATE dishMode",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "dishMode",
            DishMode.OPERATE,
        )

        assert_that(event_tracer).described_as(
            'FAILED ASSUMPTION IN "GIVEN" STEP: '
            "'the DishLeafNode must be in the TRACK pointingState'"
            "dish device"
            f"({central_node_mid.dish_leaf_node_dict[dish_id].dev_name()}) "
            "is expected to be in READY pointingState",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "pointingState",
            PointingState.READY,
        )


@when(
    parsers.parse(
        "I issue the Abort command to the TMC subarray {subarray_id}"
    )
)
def invoke_abort(subarray_node: SubarrayNodeWrapper, subarray_id: str):
    """
    A method to invoke Abort command

    Args:
        subarray_node: Fixture for a Subarray Node wrapper class
        subarray_id (str): Subarray ID
    """

    subarray_node.set_subarray_id(subarray_id)
    subarray_node.abort_subarray()


@then(
    parsers.parse(
        "the Dish {dish_ids} transitions "
        + "to dishMode STANDBY_FP and pointingState READY"
    )
)
def check_dish_mode_and_pointing_state_after_abort(
    central_node_mid: CentralNodeWrapperMid,
    dish_ids: str,
    event_tracer: TangoEventTracer,
):
    """
    Method to check dishMode and pointingState of DISH after Abort command.

    Args:
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        dish_ids (str): Comma-separated IDs of DISH components.
    """

    for dish_id in dish_ids.split(","):
        assert_that(event_tracer).described_as(
            'FAILED ASSUMPTION IN "THEN" STEP: '
            "'the DishLeafNode must be in the STANDBY_FP dishMode'"
            "dish device"
            f"({central_node_mid.dish_leaf_node_dict[dish_id].dev_name()}) "
            "is expected to be in STANDBY_FP dishMode",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "dishMode",
            DishMode.STANDBY_FP,
        )


@then("TMC SubarrayNode transitions to obsState ABORTED")
def check_subarray_obsstate_aborted(
    subarray_node: SubarrayNodeWrapper,
    event_tracer: TangoEventTracer,
    subarray_id: str,
):
    """
    Checks if SubarrayNode's obsState attribute value is ABORTED

    Args:
        subarray_node: Fixture for a Subarray Node wrapper class
        event_recorder: Fixture for EventRecorder class
        subarray_id (str): Subarray ID
    """
    subarray_node.set_subarray_id(subarray_id)
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the subarray must be in the READY obsState'"
        "TMC Subarray device"
        f"({subarray_node.subarray_node.dev_name()}) "
        "is expected to be in ABORTED obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )

    event_tracer.clear_events()
