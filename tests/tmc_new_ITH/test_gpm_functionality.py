"""Test module to test the GPM functionality"""

import json
import logging

import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_integration_test_harness.facades import DishesFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_tango_testing.integration import TangoEventTracer, log_events
from ska_tango_testing.mock.placeholders import Anything

from tests.resources.test_support.constant import (  # RESET_DEFECT,
    ERROR_PROPAGATION_DEFECT,
)
from tests.tmc_csp_new_ITH.conftest import ASSERTIONS_TIMEOUT
from tests.tmc_csp_new_ITH.utils.my_file_json_input import MyFileJSONInput
from ska_integration_test_harness.inputs.json_input import DictJSONInput


logger = logging.getLogger(__name__)


@pytest.mark.batch1
@pytest.mark.SKA_mid
@pytest.mark.test_gpm_functionality
@scenario(
    "../tmc_new_ITH/features/tmc_gpm.feature",
    "TMC processes GPM JSON and reports status per dish",
)
def test_verify_gpm_functionality():
    """Test TMC can apply and report GPM for specified bands
    for given dishes"""


@given("a TMC Mid telescope is operational")
def given_a_tmc(
    tmc: TMCFacade,
    dishes: DishesFacade,
    event_tracer: TangoEventTracer,
):
    """Given a TMC"""
    event_tracer.subscribe_event(tmc.central_node, "longRunningCommandResult")
    event_tracer.subscribe_event(tmc.central_node, "GlobalPointingModelStatus")
    log_events(
        {
            tmc.central_node: [
                "longRunningCommandResult",
                "GlobalPointingModelStatus",
            ],
        }
    )
    tmc.move_to_on(wait_termination=True, is_long_running_command=True)
    # Setup TMC before invoking SetGlobalPointingModel command on TMC
    assign_input = MyFileJSONInput("centralnode", "assign_resources_mid")
    assign_input = json.loads(assign_input.as_str())
    assign_input["dish"]["receptor_ids"] = ["SKA036"]
    assign_input["sdp"]["resources"]["receptors"] = ["SKA036"]
    tmc.assign_resources(DictJSONInput(assign_input), wait_termination=True)
    dish_63 = dishes.dish_master_dict["dish_063"]
    dish_63.SetDefective(ERROR_PROPAGATION_DEFECT)
    logger.info("<<< ASSIGN : %s TYPE: %s", assign_input, type(assign_input))


@given("a GPM JSON is provided with version <Version>")
def given_a_gpm_json(context, version):
    """Build a GPM json from data provided in feature examples"""

    receptors = {}

    for row in context.table:
        dish_id = row["Dish ID"].lower()
        bands = row["Bands"].split(", ")
        receptors[dish_id] = bands

    context.gpm_json = {"version": version, "receptors": receptors}

    context.reporting_status = {}

    for row in context.table:
        dish_id = row["Dish ID"].lower()
        context.reporting_status[dish_id] = {
            "status": row["Status"],
            "Reason": row["Reason"],
        }
    logger.info(
        "GPM_JSON: %s Reporting_Status: %s",
        context.gpm_json,
        context.reporting_status,
    )


@when("the GPM configuration is applied via TMC")
def apply_gpm_to_dishes(context, tmc: TMCFacade):
    """Invoke SetGlobalPointingModel on dishes"""
    message, pytest.unique_id = tmc.central_node.SetGlobalPointingModel(
        json.dumps(context.gpm_json)
    )
    logger.info("Command ID: %s Message: %s", message, pytest.unique_id)


@then("TMC should report the following status per dish")
def tmc_reports_gpm_status_on_dish(
    tmc: TMCFacade, event_tracer: TangoEventTracer
):
    """Check the status of GPM on dish"""

    assertion_data = (
        assert_that(event_tracer)
        .described_as(
            'FAILED ASSUMPTION IN "THEN" STEP: '
            "TMC Central Node device "
            f"({tmc.central_node.dev_name()}) "
            "is expected have longRunningCommandResult as "
            "(unique_id, COMMAND_RESULT)",
        )
        .within_timeout(ASSERTIONS_TIMEOUT)
        .has_change_event_occurred(
            tmc.subarray_node,
            "longRunningCommandResult",
            (pytest.unique_id[0], Anything),
        )
    )

    logger.info("Assertion data: %s", assertion_data["attribute_value"][1])
