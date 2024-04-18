"""Test TMC-CSP succesive functionality"""

import json

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_harness.helpers import (
    check_subarray_instance,
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)


@pytest.mark.tmc_csp
@scenario(
    "../features/tmc_csp/incremental_configure.feature",
    "TMC-CSP succesive configure functionality",
)
def test_tmc_csp_succesive_configure_functionality():
    """
    Test case to verify TMC-CSP succesive configure functionality
    """


@given("a TMC and CSP")
def given_a_tmc(central_node_mid, event_recorder, subarray_node):
    """A method to define TMC and CSP and subscribe ."""
    assert central_node_mid.central_node.ping() > 0
    assert central_node_mid.subarray_devices["csp_subarray"].ping() > 0
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(
        subarray_node.subarray_devices.get("csp_subarray"), "obsState"
    )
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")


@given(parsers.parse("a subarray {subarray_id} in the IDLE obsState"))
def telescope_is_in_idle_state(
    central_node_mid,
    event_recorder,
    command_input_factory,
    subarray_id,
    subarray_node,
):
    """A method to move subarray into the IDLE ObsState."""
    central_node_mid.move_to_on()

    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid_multiple_scantype", command_input_factory
    )

    assign_str = json.loads(assign_input_json)
    # Here we are adding this to get an event of ObsState CONFIGURING from SDP
    # Subarray
    assign_str["sdp"]["processing_blocks"][0]["parameters"][
        "time-to-ready"
    ] = 2

    central_node_mid.store_resources(json.dumps(assign_str))

    check_subarray_instance(
        subarray_node.subarray_devices.get("csp_subarray"), subarray_id
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices.get("csp_subarray"),
        "obsState",
        ObsState.IDLE,
    )

    check_subarray_instance(subarray_node.subarray_node, subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )


@when(
    parsers.parse(
        "I invoke First Configure command on TMC subarray {subarray_id} "
        + "with {input_json1}"
    )
)
def execute_first_configure_command(
    subarray_node,
    command_input_factory,
    input_json1,
    event_recorder,
    subarray_id,
):
    """ "A method to invoke first configure command"""

    check_subarray_instance(subarray_node.subarray_node, subarray_id)
    configure_json = prepare_json_args_for_commands(
        input_json1, command_input_factory
    )
    subarray_node.store_configuration_data(configure_json)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.CONFIGURING,
    )


@when(
    parsers.parse("the subarray {subarray_id} transitions to obsState READY")
)
def check_subarray_in_ready(subarray_node, event_recorder, subarray_id):
    """A method to check SDP subarray obsstate"""

    check_subarray_instance(subarray_node.subarray_node, subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.READY,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
    )


@when(
    parsers.parse(
        "I invoke Second Configure command on TMC subarray {subarray_id} "
        + "with {input_json2}"
    )
)
def execute_second_configure_command(
    subarray_node,
    command_input_factory,
    input_json2,
    event_recorder,
    subarray_id,
):
    """ "A method to invoke second configure command"""

    check_subarray_instance(subarray_node.subarray_node, subarray_id)
    configure_json = prepare_json_args_for_commands(
        input_json2, command_input_factory
    )
    subarray_node.store_configuration_data(configure_json)

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.CONFIGURING,
    )


@then(
    parsers.parse(
        "the subarray {subarray_id} reconfigures changing its "
        + "obsState to READY"
    )
)
def check_subarray_in_ready_in_reconfigure(
    central_node_mid, subarray_node, event_recorder, subarray_id
):
    """A method to check SDP subarray obsstate"""

    check_subarray_instance(subarray_node.subarray_node, subarray_id)

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.READY,
    )

    check_subarray_instance(central_node_mid.subarray_node, subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
    )
