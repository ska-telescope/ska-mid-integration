"""
This module defines a BDD (Behavior-Driven Development) test scenario
using pytest-bdd to verify the behavior of the Telescope Monitoring and
Control (TMC) system to verify the SKB-1158.
"""


import json
import logging

import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_tango_base.commands import ResultCode
from ska_tango_testing.integration import TangoEventTracer, log_events

from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_support.constant import TIMEOUT
from tests.tmc_csp_new_ITH.utils.my_file_json_input import MyFileJSONInput

LOGGER = logging.getLogger(__name__)


@pytest.mark.batch123
@pytest.mark.SKA_mid
@scenario(
    "../features/tmc/SKB_1158.feature",
    "Verify SKB-1158",
)
def test_verify_skb_1158():
    """BDD test scenario for verifying SKB-1158"""


@given("a TMC")
def given_a_tmc(tmc: TMCFacade, event_tracer: TangoEventTracer):
    """
    This method invokes On command from central node and verifies
    the state of telescope after the invocation.
    Args:
        central_node (CentralNodeWrapperLow): Object of Central node wrapper
        event_tracer(TangoEventTracer): object of TangoEventTracer used for
        managing the device events
    """
    event_tracer.clear_events()
    event_tracer.subscribe_event(tmc.central_node, "longRunningCommandResult")
    event_tracer.subscribe_event(tmc.subarray_node, "obsState")
    event_tracer.subscribe_event(tmc.subarray_node, "longRunningCommandResult")
    log_events(
        {
            tmc.central_node: [
                "longRunningCommandResult",
            ],
            tmc.subarray_node: [
                "obsState",
                "longRunningCommandResult",
            ],
        }
    )
    tmc.move_to_on(wait_termination=True, is_long_running_command=True)

    assert_that(event_tracer).described_as(
        "FAILED UNEXPECTED INITIAL OBSSTATE: "
        "Subarray Node device"
        f"({tmc.subarray_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@given("central node is busy assigning resources")
def central_node_assign_resources(
    tmc: TMCFacade, command_input_factory: JsonFactory
):
    """
    This method invokes AssignResources command on central node.

    Args:
        central_node (CentralNodeWrapperLow): Object of Central node wrapper
        command_input_factory (JsonFactory): Object of json factory
    """
    assign_input = MyFileJSONInput("centralnode", "assign_resources_mid")
    assign_input = json.loads(assign_input.as_str())
    LOGGER.info("Invoking AssignResources command: %s", assign_input)
    _, pytest.unique_id_assign = tmc.central_node.AssignResources(assign_input)
    LOGGER.info("AssignResources command id: %s", pytest.unique_id_assign)


@given("subarray node is in observation state RESOURCING")
def subarray_node_obs_state_resourcing(
    tmc: TMCFacade, event_tracer: TangoEventTracer
):
    """
    This method checks the subarray node observation state RESOURCING after
    AssignResources is invoked on central node.
    Args:
        central_node (CentralNodeWrapperLow): Object of Central node wrapper
        event_tracer(TangoEventTracer): Object of TangoEventTracer used for
        managing the device events
        command_input_factory (JsonFactory): Object of json factory
    """
    assert_that(event_tracer).described_as(
        "FAILED UNEXPECTED INITIAL OBSSTATE: "
        "Subarray Node device"
        f"({tmc.subarray_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )


@when("I invoke abort on subarray node")
def subarray_node_invoke_abort(tmc: TMCFacade):
    """This method invokes abort on subarray node

    Args:
        central_node (CentralNodeWrapperLow): Object of Central node wrapper
    """
    LOGGER.info("Invoking Abort command")
    _, pytest.unique_id_abort = tmc.subarray_node.Abort()
    LOGGER.info("Abort command id: %s", pytest.unique_id_abort)


@then("subarray Node is transitioned to observation state ABORTED")
def tmc_status(tmc: TMCFacade, event_tracer: TangoEventTracer):
    """
    Verifies that the Subarray transition to ObsState.ABORTED.
    """
    assert_that(event_tracer).described_as(
        "FAILED UNEXPECTED INITIAL OBSSTATE: "
        "Subarray Node device"
        f"({tmc.subarray_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ABORT COMMAND: "
        "Central Node device"
        f"({tmc.subarray_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Abort command completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "longRunningCommandResult",
        (
            pytest.unique_id_abort[0],
            json.dumps((int(ResultCode.OK), "Abort command completed")),
        ),
    )


@then(
    "central node receives AssignResources longrunningcommandresult with "
    + "message `Command has been aborted`"
)
def check_central_node_lrcr(tmc: TMCFacade, event_tracer: TangoEventTracer):
    """
    This method checks for central node long running command result
    attribute's desired event.

    Args:
        central_node (CentralNodeWrapperLow): Object of Central node wrapper
        event_tracer(TangoEventTracer): Object of TangoEventTracer used for
        managing the device events
    """
    exception_message = "Command has been aborted"
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ABORT: "
        "Central Node device"
        f"({tmc.central_node.dev_name()}) "
        "is expected have longRunningCommandResult"
        "(ResultCode.FAILED,exception)",
    ).within_timeout(TIMEOUT).has_desired_result_code_message_in_lrcr_event(
        tmc.central_node,
        [exception_message],
        pytest.unique_id_assign[0],
        ResultCode.FAILED,
    )
