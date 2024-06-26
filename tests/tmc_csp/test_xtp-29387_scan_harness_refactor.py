"""Test module for TMC-CSP Scan functionality"""
import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tango import DevState

from tests.test_harness2.central_node_mid import CentralNodeWrapperMid
from tests.test_harness2.event_recorder import EventRecorder
from tests.test_harness2.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.test_harness2.subarray_node import SubarrayNodeWrapper
from tests.test_harness2.utils.common_utils import JsonFactory


@pytest.mark.tmc_csp
@scenario(
    "../features/tmc_csp/xtp_29387_scan.feature",
    "TMC executes a Scan command on CSP subarray.",
)
def test_scan_command_harness_refactor():
    """BDD test scenario for verifying successful execution of
    the Scan command with TMC and CSP devices for pairwise
    testing."""


@given("the telescope is in ON state")
def given_a_telescope_in_on_state(
    central_node_facade, subarray_node_facade, event_recorder
):
    """Checks if CentralNode's telescopeState attribute value is on."""
    event_recorder.subscribe_event(
        central_node_facade.central_node, "telescopeState"
    )
    # central_node_facade.csp_master.adminMode = 0
    # wait_csp_master_off()
    central_node_facade.move_to_on()

    event_recorder.subscribe_event(central_node_facade.csp_master, "State")
    event_recorder.subscribe_event(
        central_node_facade.subarray_devices["csp_subarray"], "State"
    )

    assert event_recorder.has_change_event_occurred(
        central_node_facade.csp_master,
        "State",
        DevState.ON,
    )

    assert event_recorder.has_change_event_occurred(
        subarray_node_facade.subarray_devices["csp_subarray"],
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_facade.central_node,
        "telescopeState",
        DevState.ON,
    )


@given(parsers.parse("TMC subarray {subarray_id} is in READY ObsState"))
def subarray_in_ready_obsstate(
    central_node_facade: CentralNodeWrapperMid,
    event_recorder: EventRecorder,
    command_input_factory: JsonFactory,
    subarray_node_facade: SubarrayNodeWrapper,
    subarray_id: str,
) -> None:
    """Move TMC Subarray to READY obsstate."""
    central_node_facade.set_subarray_id(subarray_id)
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    event_recorder.subscribe_event(
        central_node_facade.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(
        subarray_node_facade.subarray_devices["csp_subarray"], "obsState"
    )
    event_recorder.subscribe_event(
        subarray_node_facade.subarray_node, "obsState"
    )

    subarray_node_facade.force_change_of_obs_state(
        "READY",
        assign_input_json=assign_input_json,
        configure_input_json=configure_input_json,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_facade.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.READY,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_facade.subarray_node,
        "obsState",
        ObsState.READY,
        lookahead=20,
    )


@when(
    parsers.parse("I issue the scan command to the TMC subarray {subarray_id}")
)
def invoke_scan(subarray_node_facade, command_input_factory):
    """Invokes Scan command on TMC"""
    scan_input_json = prepare_json_args_for_commands(
        "scan_mid", command_input_factory
    )
    subarray_node_facade.store_scan_data(scan_input_json)


@then(parsers.parse("the CSP subarray transitions to ObsState SCANNING"))
def csp_subarray_scanning(subarray_node_facade, event_recorder):
    """Checks if Csp Subarray's obsState attribute value is SCANNING"""
    event_recorder.subscribe_event(
        subarray_node_facade.subarray_devices["csp_subarray"], "obsState"
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_facade.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.SCANNING,
    )


@then(
    parsers.parse(
        "the TMC subarray {subarray_id} transitions to ObsState SCANNING"
    )
)
def tmc_subarray_scanning(
    central_node_facade, subarray_node_facade, event_recorder, subarray_id
):
    """Checks if SubarrayNode's obsState attribute value is SCANNING"""
    central_node_facade.set_subarray_id(int(subarray_id))
    assert event_recorder.has_change_event_occurred(
        subarray_node_facade.subarray_node,
        "obsState",
        ObsState.SCANNING,
        lookahead=15,
    )


@then(
    parsers.parse(
        "the CSP subarray ObsState transitions to READY after the"
        + " scan duration elapsed"
    )
)
def csp_subarray_ObsState(
    central_node_facade, subarray_node_facade, event_recorder, subarray_id
):
    """Checks if SubarrayNode's obsState attribute value is READY"""
    central_node_facade.set_subarray_id(int(subarray_id))
    assert event_recorder.has_change_event_occurred(
        subarray_node_facade.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.READY,
    )


@then(
    parsers.parse(
        "the TMC subarray {subarray_id} ObsState transitions back to READY"
    )
)
def tmc_subarray_ready(
    central_node_facade, subarray_node_facade, event_recorder, subarray_id
):
    """Checks if SubarrayNode's obsState attribute value is EMPTY"""
    central_node_facade.set_subarray_id(int(subarray_id))
    assert event_recorder.has_change_event_occurred(
        subarray_node_facade.subarray_node, "obsState", ObsState.READY
    )
