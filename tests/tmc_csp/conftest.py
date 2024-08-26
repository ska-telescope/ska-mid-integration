"""Pytest BDD step implementations specific to tmc integration
tests."""

import json
import logging

from pytest import fixture
from pytest_bdd import given, parsers, then, when
from ska_control_model import ObsState
from ska_ser_logging import configure_logging
from ska_tango_testing.integration import TangoEventTracer
from tango import DevState

from tests.resources.test_harness.constant import COMMAND_COMPLETED
from tests.resources.test_harness.helpers import (
    check_subarray_instance,
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
    update_scan_id,
)
from tests.resources.test_harness.utils.common_utils import (
    check_scan_successful_csp,
)
from tests.test_harness3.telescope_facades.csp_facade import CSPFacade
from tests.test_harness3.telescope_facades.dishes_facade import DishesFacade
from tests.test_harness3.telescope_facades.sdp_facade import SDPFacade
from tests.test_harness3.telescope_facades.tmc_central_node_facade import (
    TMCCentralNodeFacade,
)
from tests.test_harness3.telescope_facades.tmc_subarray_node_facade import (
    TMCSubarrayNodeFacade,
)
from tests.test_harness3.telescope_init.telescope_structure_factory import (
    TelescopeStructureFactory,
)
from tests.test_harness3.telescope_inputs.obs_state_commands_input import (
    ObsStateCommandsInput,
)
from tests.test_harness3.telescope_structure.telescope_wrapper import (
    TelescopeWrapper,
)
from tests.various_utils.default_json_inputs import (  # ASSIGN_SUBARRAY_INPUT,
    ASSING_CENTRAL_NODE_INPUT,
    CONFIGURE_SUBARRAY_INPUT,
    DEFAULT_VCC_CONFIG_INPUT,
    RELEASE_CENTRAL_NODE_INPUT,
    SCAN_SUBARRAY_INPUT,
)

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


@given("the telescope is in ON state")
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
    event_recorder.subscribe_event(
        central_node_mid.subarray_devices["csp_subarray"], "State"
    )
    event_recorder.subscribe_event(central_node_mid.csp_master, "State")
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    event_recorder.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )

    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )
    central_node_mid.move_to_on()
    assert event_recorder.has_change_event_occurred(
        central_node_mid.csp_master,
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_devices["csp_subarray"],
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )


@when(parsers.parse("I assign resources to TMC SubarrayNode {subarray_id}"))
def telescope_is_in_idle_state(
    central_node_mid,
    event_recorder,
    command_input_factory,
    subarray_id,
    subarray_node,
):
    """A method to move subarray into the IDLE ObsState."""

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid_multiple_scantype", command_input_factory
    )

    assign_str = json.loads(assign_input_json)
    _, unique_id = central_node_mid.store_resources(json.dumps(assign_str))

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

    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (unique_id[0], COMMAND_COMPLETED),
        lookahead=5,
    )


@when(
    parsers.parse(
        "I reassign with new resources to TMC SubarrayNode {subarray_id}"
    )
)
def reassign_resources(
    central_node_mid,
    event_recorder,
    command_input_factory,
    subarray_id,
    subarray_node,
):
    """A method to move subarray into the IDLE ObsState"""

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid_multiple_scantype_new_resources",
        command_input_factory,
    )

    assign_str = json.loads(assign_input_json)

    _, unique_id = central_node_mid.store_resources(json.dumps(assign_str))

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

    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (unique_id[0], COMMAND_COMPLETED),
        lookahead=10,
    )


@when(parsers.parse("end the configuration on TMC SubarrayNode {subarray_id}"))
def execute_end_command(
    subarray_node,
    command_input_factory,
    central_node_mid,
    event_recorder,
    subarray_id,
    scan_types,
):
    """ "A method to invoke end command"""

    central_node_mid.set_subarray_id(subarray_id)
    _, unique_id = subarray_node.end_observation()

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.IDLE,
        lookahead=20,
    )

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node, "obsState", ObsState.IDLE, lookahead=20
    )

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (unique_id[0], COMMAND_COMPLETED),
        lookahead=10,
    )


@when(parsers.parse("release the resources on TMC SubarrayNode {subarray_id}"))
def execute_release_resources_command(
    command_input_factory,
    central_node_mid,
    event_recorder,
    subarray_id,
):
    """ "A method to invoke Release Resources command"""

    release_input_json = prepare_json_args_for_centralnode_commands(
        "release_resources_mid", command_input_factory
    )
    check_subarray_instance(central_node_mid.subarray_node, subarray_id)
    _, unique_id = central_node_mid.invoke_release_resources(
        release_input_json
    )

    check_subarray_instance(
        central_node_mid.subarray_devices.get("csp_subarray"), subarray_id
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_devices.get("csp_subarray"),
        "obsState",
        ObsState.EMPTY,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (unique_id[0], COMMAND_COMPLETED),
        lookahead=5,
    )


@then(
    parsers.parse(
        "TMC SubarrayNode {subarray_id} transitions to EMPTY ObsState"
    )
)
def check_tmc_is_in_empty_obsstate(
    central_node_mid, event_recorder, subarray_id
):
    """Method to check TMC is in EMPTY obsstate."""
    check_subarray_instance(central_node_mid.subarray_node, subarray_id)
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@when(
    parsers.parse(
        "reperform scan with same configuration and new scan id {new_scan_id}"
    )
)
def reexecute_scan_command(
    command_input_factory, event_recorder, subarray_node, new_scan_id
):
    """A method to invoke scan command with new scan_id"""

    scan_json = prepare_json_args_for_commands(
        "scan_mid", command_input_factory
    )

    scan_json = update_scan_id(scan_json, new_scan_id)
    _, unique_id = subarray_node.execute_transition("Scan", argin=scan_json)

    check_scan_successful_csp(
        subarray_node, event_recorder, new_scan_id, unique_id
    )


# ----------------------------------------------------------
# New fixtures (refactor 3)


@fixture
def default_commands_inputs() -> ObsStateCommandsInput:
    """Default JSON inputs for TMC commands."""
    return ObsStateCommandsInput(
        assign_input=ASSING_CENTRAL_NODE_INPUT,
        configure_input=CONFIGURE_SUBARRAY_INPUT,
        scan_input=SCAN_SUBARRAY_INPUT,
        release_input=RELEASE_CENTRAL_NODE_INPUT,
    )


@fixture
def telescope_wrapper(
    default_commands_inputs: ObsStateCommandsInput,
) -> TelescopeWrapper:
    """Create an unique test harness with proxies to all devices."""
    components_factory = TelescopeStructureFactory(
        default_commands_inputs, DEFAULT_VCC_CONFIG_INPUT
    )
    telescope = components_factory.init_telescope_test_structure()
    yield telescope
    telescope.tear_down()

    # NOTE: As the code is organized now, I cannot anticipate the
    # teardown of the telescope structure. To run reset now I should
    # init subarray node (with SetSubarrayId), but to do that I need
    # to know subarray_id, which is a parameter of the Gherkin steps.


@fixture
def central_node_facade(telescope_wrapper: TelescopeWrapper):
    """Create a facade to TMC central node and all its operations."""
    central_node_facade = TMCCentralNodeFacade(telescope_wrapper)
    yield central_node_facade


@fixture
def subarray_node_facade(telescope_wrapper: TelescopeWrapper):
    """Create a facade to TMC subarray node and all its operations."""
    subarray_node = TMCSubarrayNodeFacade(telescope_wrapper)
    yield subarray_node


@fixture
def csp(telescope_wrapper: TelescopeWrapper):
    """Create a facade to CSP devices."""
    return CSPFacade(telescope_wrapper)


@fixture
def sdp(telescope_wrapper: TelescopeWrapper):
    """Create a facade to SDP devices."""
    return SDPFacade(telescope_wrapper)


@fixture
def dishes(telescope_wrapper: TelescopeWrapper):
    """Create a facade to dishes devices."""
    return DishesFacade(telescope_wrapper)


# ----------------------------------------------------------
# Tango event tracer


@fixture
def event_tracer() -> TangoEventTracer:
    """Create an event tracer."""
    return TangoEventTracer()
