"""Pytest BDD step implementations specific to TMC DISH-LMC integration
tests."""

import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, then
from ska_control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevState

from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
)
from tests.resources.test_harness.utils.common_utils import setup_dish_events
from tests.resources.test_support.constant import COMMAND_COMPLETED, TIMEOUT
from tests.resources.test_support.enum import DishMode, PointingState


@given(
    parsers.parse(
        "a Telescope consisting of TMC, DISH {dish_ids},"
        + " simulated CSP and simulated SDP"
    )
)
def given_a_telescope(central_node_mid, dish_ids):
    """
    Given a TMC

    Args:
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        dish_ids (str): Comma-separated IDs of DISH components.
    """
    assert central_node_mid.csp_master.ping() > 0
    assert central_node_mid.sdp_master.ping() > 0
    for dish_id in dish_ids.split(","):
        assert central_node_mid.dish_master_dict[dish_id].ping() > 0
        assert central_node_mid.dish_leaf_node_dict[dish_id].ping() > 0


@given("the Telescope is in ON state")
def turn_on_telescope(central_node_mid, event_recorder):
    """
    A method to put Telescope ON

    Args:
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        event_recorder: Fixture for EventRecorder class
    """
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
def given_subarray_in_idle(
    central_node_mid,
    subarray_node,
    event_tracer: TangoEventTracer,
    command_input_factory,
):
    event_tracer.subscribe_event(
        subarray_node.subarray_devices["sdp_subarray"], "obsState"
    )
    event_tracer.subscribe_event(
        subarray_node.subarray_devices["csp_subarray"], "obsState"
    )
    event_tracer.subscribe_event(subarray_node.subarray_node, "obsState")
    event_tracer.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "multiple_assign1", command_input_factory
    )
    _, pytest.unique_id = central_node_mid.store_resources(assign_input_json)

    csp = subarray_node.subarray_devices.get("csp_subarray")
    sdp = subarray_node.subarray_devices.get("sdp_subarray")

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray must be in the IDLE obsState'"
        "SDP Subarray device"
        f"({sdp.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.IDLE,
    )

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "Given" STEP: '
        "'the subarray must be in the IDLE obsState'"
        "CSP Subarray device"
        f"({csp.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.IDLE,
    )

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

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray is in IDLE obsState'"
        "TMC Central Node device"
        f"({central_node_mid.central_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (pytest.unique_id[0], COMMAND_COMPLETED),
    )

    event_tracer.clear_events()


@then(
    parsers.parse(
        "the subarray reconfigures changing its obsState to READY for"
        " {dish_ids}"
    )
)
@then(
    parsers.parse(
        "the subarray transitions to obsState READY for" " {dish_ids}"
    )
)
def check_for_ready(central_node_mid, subarray_node, event_tracer, dish_ids):
    # Verify ObsState is READY

    event_tracer.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(subarray_node.subarray_node, "obsState")

    for dish_id in dish_ids.split(","):
        log_events(
            {
                central_node_mid.dish_master_dict.get(dish_id): ["dishMode"],
                central_node_mid.dish_master_dict.get(dish_id): [
                    "pointingState"
                ],
            }
        )

    setup_dish_events(central_node_mid, event_tracer, dish_ids)

    for dish_id in dish_ids.split(","):
        assert_that(event_tracer).described_as(
            'FAILED ASSUMPTION IN "WHEN" STEP: '
            "'the dish must be in the OPERATE dishMode'"
            "dish device"
            f"({central_node_mid.dish_master_dict[dish_id].dev_name()}) "
            "is expected to be in OPERATE dishMode",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "dishMode",
            DishMode.OPERATE,
        )

        assert_that(event_tracer).described_as(
            'FAILED ASSUMPTION IN "WHEN" STEP: '
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
            'FAILED ASSUMPTION IN "WHEN" STEP: '
            "'the dish must be in the TRACK pointingState'"
            "dish device"
            f"({central_node_mid.dish_master_dict[dish_id].dev_name()}) "
            "is expected to be in TRACK pointingState",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "pointingState",
            PointingState.TRACK,
        )

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "WHEN" STEP: '
        "'the subarray must be in the READY obsState'"
        "TMC Subarray device"
        f"({subarray_node.subarray_node.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "WHEN" STEP: '
        "'the subarray is in READY obsState'"
        "TMC Subarray Node device"
        f"({subarray_node.subarray_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (pytest.unique_id[0], COMMAND_COMPLETED),
    )

    event_tracer.clear_events()


@then(
    "with command ReleaseResources TMC subarray transitions to obsState EMPTY"
)
@given(
    "with command ReleaseResources TMC subarray transitions to obsState EMPTY"
)
def given_subarray_in_empty(
    central_node_mid,
    subarray_node,
    event_tracer: TangoEventTracer,
    command_input_factory,
):
    event_tracer.subscribe_event(
        subarray_node.subarray_devices["sdp_subarray"], "obsState"
    )
    event_tracer.subscribe_event(
        subarray_node.subarray_devices["csp_subarray"], "obsState"
    )
    event_tracer.subscribe_event(subarray_node.subarray_node, "obsState")
    event_tracer.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )

    release_input_json = prepare_json_args_for_centralnode_commands(
        "release_resources_mid", command_input_factory
    )
    release_input = json.loads(release_input_json)
    _, pytest.unique_id = central_node_mid.invoke_release_resources(
        json.dumps(release_input)
    )
    csp = subarray_node.subarray_devices.get("csp_subarray")
    sdp = subarray_node.subarray_devices.get("sdp_subarray")

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray must be in the EMPTY obsState'"
        "SDP Subarray device"
        f"({sdp.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.EMPTY,
    )

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "Given" STEP: '
        "'the subarray must be in the EMPTY obsState'"
        "CSP Subarray device"
        f"({csp.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.EMPTY,
    )

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray must be in the EMPTY obsState'"
        "TMC Subarray device"
        f"({subarray_node.subarray_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray is in EMPTY obsState'"
        "TMC Central Node device"
        f"({central_node_mid.central_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (pytest.unique_id[0], COMMAND_COMPLETED),
    )

    event_tracer.clear_events()
