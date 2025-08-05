"""Test case to verify skb_930"""


import logging

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_integration_test_harness.inputs.test_harness_inputs import (
    TestHarnessInputs,
)
from ska_tango_testing.integration import TangoEventTracer, log_events

from tests.resources.test_harness.helpers import (
    wait_and_validate_device_attribute_value,
)
from tests.tmc_csp_new_ITH.conftest import (
    ASSERTIONS_TIMEOUT,
    SubarrayTestContextData,
    _get_expected_long_run_command_result,
)
from tests.tmc_csp_new_ITH.utils.my_file_json_input import MyFileJSONInput
from tests.tmc_new_ITH.utils.utils import setup_event_subscriptions

LOGGER = logging.getLogger(__name__)


@pytest.mark.batch1
@pytest.mark.SKA_mid
@scenario(
    "../tmc_new_ITH/features/skb_930.feature",
    "TMC skb-930",
)
def test_verify_skb_930():
    """Test TMC can handle wrap_sector with any kind on main configure json"""


def _setup_event_subscriptions(
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """Subscribe TMC, CSP and SDP devices to track and log obsState events.

    :param tmc: the TMC facade.
    :param csp: the CSP facade.
    :param sdp: the SDP facade.
    :param event_tracer: the event tracer.
    """
    event_tracer.subscribe_event(tmc.subarray_node, "obsState")
    event_tracer.subscribe_event(csp.csp_subarray, "obsState")
    event_tracer.subscribe_event(sdp.sdp_subarray, "obsState")
    event_tracer.subscribe_event(sdp.sdp_subarray, "receiveAddresses")
    event_tracer.subscribe_event(sdp.sdp_subarray, "commandCallInfo")
    event_tracer.subscribe_event(tmc.central_node, "longRunningCommandResult")
    event_tracer.subscribe_event(tmc.subarray_node, "longRunningCommandResult")

    log_events(
        {
            tmc.subarray_node: [
                "obsState",
                "longRunningCommandResult",
            ],
            csp.csp_subarray: ["obsState"],
            sdp.sdp_subarray: [
                "obsState",
                "commandCallInfo",
                "receiveAddresses",
            ],
            tmc.central_node: ["longRunningCommandResult"],
        },
        event_enum_mapping={"obsState": ObsState},
    )


@given("a TMC")
def given_a_tmc(
    tmc: TMCFacade,
    sdp: SDPFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
):
    """Given a TMC"""
    setup_event_subscriptions(tmc, csp, sdp, event_tracer)


@when(parsers.parse("End2End observation is repeated {count} times on TMC"))
@when("the resources are assigned to TMC SubarrayNode")
def execute_e2e_observation(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
    default_commands_inputs: TestHarnessInputs,
    count: int,
):
    """
    Execute End 2 End observation
    """
    _setup_event_subscriptions(tmc, csp, sdp, event_tracer)

    def end_to_end_observation():
        """
        Repeats End 2 End observation
        """

        event_tracer.clear_events()
        _setup_event_subscriptions(tmc, csp, sdp, event_tracer)
        context_fixt.starting_state = ObsState.READY

        tmc.force_change_of_obs_state(
            ObsState.READY,
            default_commands_inputs,
            wait_termination=True,
        )

        LOGGER.info("Scan Command starting")
        json_input = MyFileJSONInput("subarray", "scan_mid")
        context_fixt.when_action_result = tmc.scan(
            json_input,
            wait_termination=False,
        )

        assert_that(event_tracer).described_as(
            f"Both TMC Subarray Node device ({tmc.subarray_node})"
            f", CSP Subarray device ({csp.csp_subarray}) "
            f"and SDP Subarray device ({sdp.sdp_subarray}) "
            "ObsState attribute values should move "
            f"from {str(context_fixt.starting_state)} to SCANNING."
        ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
            tmc.subarray_node,
            "obsState",
            ObsState.SCANNING,
            previous_value=context_fixt.starting_state,
        )

        context_fixt.starting_state = ObsState.SCANNING

        assert_that(event_tracer).described_as(
            f"Both TMC Subarray Node device ({tmc.subarray_node})"
            f", CSP Subarray device ({csp.csp_subarray}) "
            f"and SDP Subarray device ({sdp.sdp_subarray}) "
            "ObsState attribute values should move "
            f"from {str(context_fixt.starting_state)} to READY."
        ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
            tmc.subarray_node,
            "obsState",
            ObsState.READY,
            previous_value=context_fixt.starting_state,
        )

        assert_that(event_tracer).described_as(
            "TMC Subarray Node "
            f"({tmc.subarray_node}) "
            "is expected to report a"
            "longRunningCommand successful completion."
        ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
            tmc.subarray_node,
            "longRunningCommandResult",
            _get_expected_long_run_command_result(context_fixt),
        )
        LOGGER.info("Scan Command completed")
        LOGGER.info("End Command Starting")

        context_fixt.starting_state = ObsState.READY

        tmc.end_observation()

        assert_that(event_tracer).described_as(
            f"Both TMC Subarray Node device ({tmc.subarray_node})"
            f", CSP Subarray device ({csp.csp_subarray}) "
            f"and SDP Subarray device ({sdp.sdp_subarray}) "
            "ObsState attribute values should move "
            f"from {str(context_fixt.starting_state)} to IDLE."
        ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
            tmc.subarray_node,
            "obsState",
            ObsState.IDLE,
            previous_value=context_fixt.starting_state,
        )

        context_fixt.starting_state = ObsState.RESOURCING

        release_input = MyFileJSONInput("centralnode", "release_resources_mid")
        tmc.release_resources(release_input)

        assert_that(event_tracer).described_as(
            f"Both TMC Subarray Node device ({tmc.subarray_node})"
            f", CSP Subarray device ({csp.csp_subarray}) "
            f"and SDP Subarray device ({sdp.sdp_subarray}) "
            "ObsState attribute values should move "
            f"from {str(context_fixt.starting_state)} to EMPTY."
        ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
            tmc.subarray_node,
            "obsState",
            ObsState.EMPTY,
            previous_value=context_fixt.starting_state,
        )

    # Add few more steps

    for i in range(int(count)):
        end_to_end_observation()
        LOGGER.info(f"Observation cycle {i} complete")

    LOGGER.info("test case complete.")


@then("Final ObsState is successfully calculated as EMPTY")
def check_tmc_obsState(
    tmc: TMCFacade,
    event_tracer: TangoEventTracer,
):
    """
    Checks for TMC ObsState at the end of all cycles.
    It should be EMPTY
    """

    assert wait_and_validate_device_attribute_value(
        tmc.subarray_node, "obsState", ObsState.EMPTY
    )
    event_tracer.clear_events()
