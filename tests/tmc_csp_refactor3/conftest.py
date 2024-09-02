"""Configurations needed for the tests using the new harness."""

from dataclasses import dataclass
from typing import Any

import pytest
from pytest_bdd import given, parsers
from ska_control_model import ObsState
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.dishes_facade import DishesFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_central_node_facade import (
    TMCCentralNodeFacade,
)
from ska_integration_test_harness.facades.tmc_subarray_node_facade import (
    TMCSubarrayNodeFacade,
)
from ska_integration_test_harness.init.test_harness_builder import (
    TestHarnessBuilder,
)
from ska_integration_test_harness.inputs.json_input import DictJSONInput
from ska_integration_test_harness.inputs.test_harness_inputs import (
    TestHarnessInputs,
)
from ska_integration_test_harness.structure.telescope_wrapper import (
    TelescopeWrapper,
)
from ska_tango_testing.integration import TangoEventTracer, log_events

from tests.tmc_csp_refactor3.utils.my_file_json_input import MyFileJSONInput

# ------------------------------------------------------------
# Test Harness fixtures

DEFAULT_VCC_CONFIG_INPUT = DictJSONInput(
    {
        "interface": "https://schema.skao.int/ska-mid-cbf-initsysparam/1.0",
        "tm_data_sources": [
            "car://gitlab.com/ska-telescope/ska-telmodel-data?"
            + "ska-sdp-tmlite-repository-1.0.0#tmdata"
        ],
        "tm_data_filepath": (
            "instrument/ska1_mid_psi/ska-mid-cbf-system-parameters.json",
        ),
    }
)


@pytest.fixture
def default_commands_inputs() -> TestHarnessInputs:
    """Default JSON inputs for TMC commands."""
    return TestHarnessInputs(
        assign_input=MyFileJSONInput("centralnode", "assign_resources_mid"),
        configure_input=MyFileJSONInput("subarray", "configure_mid"),
        scan_input=MyFileJSONInput("subarray", "scan_mid"),
        release_input=MyFileJSONInput("centralnode", "release_resources_mid"),
        default_vcc_config_input=DEFAULT_VCC_CONFIG_INPUT,
    )


@pytest.fixture
def telescope_wrapper(
    default_commands_inputs: TestHarnessInputs,
) -> TelescopeWrapper:
    """Create an unique test harness with proxies to all devices."""
    test_harness_builder = TestHarnessBuilder()

    # import from a configuration file device names and emulation directives
    # for TMC, CSP, SDP and the Dishes
    test_harness_builder.read_from_file(
        "tests/tmc_csp_refactor3/test_harness_config.yaml"
    )
    test_harness_builder.validate_configurations()

    # set the default inputs for the TMC commands,
    # which will be used for teardown procedures
    test_harness_builder.set_default_inputs(default_commands_inputs)
    test_harness_builder.validate_default_inputs()

    # build the wrapper of the telescope and it's sub-systems
    telescope = test_harness_builder.build()
    yield telescope

    # after a test is completed, reset the telescope to its initial state
    # (obsState=READY, telescopeState=OFF, no resources assigned)
    telescope.tear_down()

    # NOTE: As the code is organized now, I cannot anticipate the
    # teardown of the telescope structure. To run reset now I should
    # init subarray node (with SetSubarrayId), but to do that I need
    # to know subarray_id, which is a parameter of the Gherkin steps.


@pytest.fixture
def central_node_facade(telescope_wrapper: TelescopeWrapper):
    """Create a facade to TMC central node and all its operations."""
    central_node_facade = TMCCentralNodeFacade(telescope_wrapper)
    yield central_node_facade


@pytest.fixture
def subarray_node_facade(telescope_wrapper: TelescopeWrapper):
    """Create a facade to TMC subarray node and all its operations."""
    subarray_node = TMCSubarrayNodeFacade(telescope_wrapper)
    yield subarray_node


@pytest.fixture
def csp(telescope_wrapper: TelescopeWrapper):
    """Create a facade to CSP devices."""
    return CSPFacade(telescope_wrapper)


@pytest.fixture
def sdp(telescope_wrapper: TelescopeWrapper):
    """Create a facade to SDP devices."""
    return SDPFacade(telescope_wrapper)


@pytest.fixture
def dishes(telescope_wrapper: TelescopeWrapper):
    """Create a facade to dishes devices."""
    return DishesFacade(telescope_wrapper)


# ----------------------------------------------------------
# Tango event tracer


@pytest.fixture
def event_tracer() -> TangoEventTracer:
    """Create an event tracer."""
    return TangoEventTracer(
        event_enum_mapping={"obsState": ObsState},
    )


# ------------------------------------------------------------
# Other fixtures and common steps


@dataclass
class SubarrayTestContextData:
    """A class to store shared variables between steps."""

    starting_state: ObsState | None = None
    """The state of the system before the WHEN step."""

    expected_next_state: ObsState | None = None
    """The expected state to be reached if no WHEN step is executed.

    It is meaningful when the starting state is transient and so it will
    automatically change to another state (different both from the starting
    state and the expected next state).

    Leave empty if the starting state is not transient.
    """

    when_action_result: Any | None = None
    """The result of the WHEN step command."""

    when_action_name: str | None = None
    """The name of the Tango command executed in the WHEN step."""

    def is_starting_state_transient(self) -> bool:
        """Check if the starting state is transient."""
        return self.expected_next_state is not None


@pytest.fixture
def context_fixt() -> SubarrayTestContextData:
    """A collection of variables shared between steps.

    The shared variables are the following:

    - previous_state: the previous state of the subarray.
    - expected_next_state: the expected next state of the subarray (specified
        only if the previous st
    - trigger: the trigger that caused the state change.

    :return: the shared variables.
    """
    return SubarrayTestContextData()


def _setup_event_subscriptions(
    central_node_facade: TMCCentralNodeFacade,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """Set up event subscriptions for the test.

    Args:
        subarray_node_facade: Facade for the TMC subarray node.
        csp: Facade for the CSP.
        event_tracer: Event tracer for capturing events.
    """
    event_tracer.subscribe_event(
        subarray_node_facade.subarray_node, "obsState"
    )
    event_tracer.subscribe_event(csp.csp_subarray, "obsState")
    event_tracer.subscribe_event(sdp.sdp_subarray, "obsState")
    event_tracer.subscribe_event(
        central_node_facade.central_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(
        subarray_node_facade.subarray_node, "longRunningCommandResult"
    )

    log_events(
        {
            subarray_node_facade.subarray_node: [
                "obsState",
                "longRunningCommandResult",
            ],
            csp.csp_subarray: ["obsState"],
            sdp.sdp_subarray: ["obsState", "commandCallInfo"],
            central_node_facade.central_node: ["longRunningCommandResult"],
        },
        event_enum_mapping={"obsState": ObsState},
    )


@given("the telescope is in ON state")
def given_the_telescope_is_in_on_state(
    central_node_facade: TMCCentralNodeFacade,
):
    """Ensure the telescope is in ON state."""
    central_node_facade.move_to_on(wait_termination=True)


@given(parsers.parse("the subarray {subarray_id} can be used"))
def subarray_can_be_used(
    subarray_id: str,
    central_node_facade: TMCCentralNodeFacade,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """Set up the subarray (and the subscriptions) to be used in the test."""
    subarray_node_facade.set_subarray_id(int(subarray_id))
    _setup_event_subscriptions(
        central_node_facade, subarray_node_facade, csp, sdp, event_tracer
    )


@given(parsers.parse("the subarray {subarray} is in the RESOURCING state"))
def subarray_in_resourcing_state(
    context_fixt: SubarrayTestContextData,
    # subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    default_commands_inputs: TestHarnessInputs,
):
    """Ensure the subarray is in the RESOURCING state."""
    context_fixt.starting_state = ObsState.RESOURCING
    context_fixt.expected_next_state = ObsState.IDLE

    subarray_node_facade.force_change_of_obs_state(
        ObsState.RESOURCING,
        default_commands_inputs,
        wait_termination=True,
    )


@given(parsers.parse("the subarray {subarray} is in the IDLE state"))
def subarray_in_idle_state(
    context_fixt: SubarrayTestContextData,
    # subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    central_node_facade: TMCCentralNodeFacade,
    default_commands_inputs: TestHarnessInputs,
):
    """Ensure the subarray is in the IDLE state."""
    context_fixt.starting_state = ObsState.IDLE

    subarray_node_facade.force_change_of_obs_state(
        ObsState.EMPTY,
        default_commands_inputs,
        wait_termination=True,
    )

    json_input = MyFileJSONInput(
        "centralnode", "assign_resources_mid"
    ).with_attribute("subarray_id", 1)

    context_fixt.when_action_result = central_node_facade.assign_resources(
        json_input,
        wait_termination=True,
    )

    # NOTE: Do not use force change of obs state here, because currently
    # for moving to IDLE it uses a wrong command, called on subarray node
    # instead of on central node.

    # TODO: fix the above issue and use the following line instead:
    # subarray_node_facade.force_change_of_obs_state(
    #     ObsState.IDLE,
    #     default_commands_inputs,
    #     wait_termination=True,
    # )

    # NOTE: we could consider foreach TelescopeAction that moves to
    # a transient state and then to a quiescent state, to permit to choose
    # if the termination condition should be the transient state or the
    # quiescent state.

    # NOTE: The following line makes a few more tests pass,
    # but it is not correct since a subarray that is in IDLE state
    # state should be able to receive the
    # Configure, AssignResources, ... commands.
    # (instead occasionally it fails for a sort of timeout error in the
    # Tango command reception)

    # time.sleep(5)

    # NOTE: it fails also if I verify this!
    # assert_that(subarray_node_facade.subarray_node.obsState).is_equal_to(
    #     ObsState.IDLE
    # )
    # assert_that(
    #     subarray_node_facade.csp_subarray_leaf_node.cspSubarrayObsState
    # ).is_equal_to(ObsState.IDLE)
    # assert_that(
    #     subarray_node_facade.sdp_subarray_leaf_node.sdpSubarrayObsState
    # ).is_equal_to(ObsState.IDLE)
    # assert_that(csp.csp_subarray.obsState).is_equal_to(ObsState.IDLE)
    # assert_that(sdp.sdp_subarray.obsState).is_equal_to(ObsState.IDLE)
    # assert_that(event_tracer).described_as(
    #     "Central Node "
    #     f"({central_node_facade.central_node}) "
    #     "longRunningCommand successful completion."
    # ).within_timeout(30).has_change_event_occurred(
    #     central_node_facade.central_node,
    #     "longRunningCommandResult",
    #     # _get_expected_long_run_command_result(context_fixt),
    #     (res[1][0], str(ResultCode.OK.value))
    # )


@given(parsers.parse("the subarray {subarray} is in the CONFIGURING state"))
def subarray_in_configuring_state(
    context_fixt: SubarrayTestContextData,
    # subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    default_commands_inputs: TestHarnessInputs,
):
    """Ensure the subarray is in the CONFIGURING state."""
    context_fixt.starting_state = ObsState.CONFIGURING
    context_fixt.expected_next_state = ObsState.READY

    subarray_node_facade.force_change_of_obs_state(
        ObsState.CONFIGURING,
        default_commands_inputs,
        wait_termination=True,
    )


@given(parsers.parse("the subarray {subarray} is in the READY state"))
def subarray_in_ready_state(
    context_fixt: SubarrayTestContextData,
    # subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    default_commands_inputs: TestHarnessInputs,
):
    """Ensure the subarray is in the READY state."""
    context_fixt.starting_state = ObsState.READY

    subarray_node_facade.force_change_of_obs_state(
        ObsState.READY,
        default_commands_inputs,
        wait_termination=True,
    )

    # NOTE: The following line makes a few more tests pass,
    # but it is not correct since a subarray that is in READY state
    # state should be able to receive the
    # Configure command
    # (instead occasionally it fails for a sort of timeout error in the
    # Tango command reception)

    # time.sleep(5)


@given(parsers.parse("the subarray {subarray} is in the SCANNING state"))
def subarray_in_scanning_state(
    context_fixt: SubarrayTestContextData,
    # subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    default_commands_inputs: TestHarnessInputs,
):
    """Ensure the subarray is in the SCANNING state."""
    context_fixt.starting_state = ObsState.SCANNING
    context_fixt.expected_next_state = ObsState.READY

    subarray_node_facade.force_change_of_obs_state(
        ObsState.SCANNING,
        default_commands_inputs,
        wait_termination=True,
    )
