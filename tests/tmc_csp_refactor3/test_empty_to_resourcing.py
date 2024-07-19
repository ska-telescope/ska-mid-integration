# Define a fixture to store things, like the starting state
import pytest
from ska_control_model import ObsState
from ska_tango_testing.integration import log_events, TangoEventTracer

from tests.test_harness3.telescope_facades.csp_facade import CSPFacade
from tests.test_harness3.telescope_facades.dishes_facade import DishesFacade
from tests.test_harness3.telescope_facades.sdp_facade import SDPFacade
from tests.test_harness3.telescope_facades.tmc_central_node_facade import TMCCentralNodeFacade
from tests.test_harness3.telescope_facades.tmc_subarray_node_facade import TMCSubarrayNodeFacade
from tests.test_harness3.telescope_init.telescope_structure_factory import TelescopeStructureFactory
from tests.test_harness3.telescope_inputs.obs_state_commands_input import ObsStateCommandsInput
from tests.test_harness3.telescope_structure.telescope_wrapper import TelescopeWrapper
from tests.various_utils.default_json_inputs import ASSING_CENTRAL_NODE_INPUT, CONFIGURE_SUBARRAY_INPUT, DEFAULT_VCC_CONFIG_INPUT, RELEASE_CENTRAL_NODE_INPUT, SCAN_SUBARRAY_INPUT


# ------------------------------------------------------------
# Test Harness fixtures

# ----------------------------------------------------------
# New fixtures (refactor 3)


@pytest.fixture
def default_commands_inputs() -> ObsStateCommandsInput:
    """Default JSON inputs for TMC commands."""
    return ObsStateCommandsInput(
        assign_input=ASSING_CENTRAL_NODE_INPUT,
        configure_input=CONFIGURE_SUBARRAY_INPUT,
        scan_input=SCAN_SUBARRAY_INPUT,
        release_input=RELEASE_CENTRAL_NODE_INPUT,
    )


@pytest.fixture
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
    return TangoEventTracer()



# ------------------------------------------------------------
# Other fixtures and common steps

@pytest.fixture
def context_fixt():
    return {'starting_state':None,
            'trigger':None,}

TRANSIENT_STATES=[ObsState.ABORTING, ObsState.RESTARTING,
                  ObsState.RESOURCING, ObsState.CONFIGURING,
                  ObsState.SCANNING, ObsState.RESETTING,]

def _setup_event_subscriptions(
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
):
    """Set up event subscriptions for the test.

    Args:
        subarray_node_facade: Facade for the TMC subarray node.
        csp: Facade for the CSP.
        event_tracer: Event tracer for capturing events.
    """
    event_tracer.subscribe_event(csp.csp_subarray, "obsState")
    event_tracer.subscribe_event(
        subarray_node_facade.subarray_node, "obsState"
    )
    log_events(
        {
            csp.csp_subarray: ["obsState"],
            subarray_node_facade.subarray_node: ["obsState"],
        }
    )

@given("the telescope is in ON state")
def given_the_telescope_is_in_on_state(central_node_facade: TMCCentralNodeFacade):
    """Ensure the telescope is in ON state."""



