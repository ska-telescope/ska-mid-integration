"""Test module to test the GPM functionality"""

import json
import time
import logging
import re

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_integration_test_harness.facades import DishesFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_integration_test_harness.inputs.json_input import DictJSONInput
from ska_integration_test_harness.inputs.test_harness_inputs import (
    TestHarnessInputs,
)
from ska_tango_testing.integration import TangoEventTracer, log_events
from ska_tango_testing.mock.placeholders import Anything

from tests.resources.test_support.constant import (  # RESET_DEFECT,
    ERROR_PROPAGATION_DEFECT,
)
from tests.tmc_csp_new_ITH.conftest import ASSERTIONS_TIMEOUT
from tests.tmc_csp_new_ITH.utils.my_file_json_input import MyFileJSONInput

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
    time.sleep(30)
    tmc.move_to_on(wait_termination=True, is_long_running_command=True)
    # Setup TMC before invoking SetGlobalPointingModel command on TMC
    assign_input = MyFileJSONInput("centralnode", "assign_resources_mid")
    assign_input = json.loads(assign_input.as_str())
    assign_input["dish"]["receptor_ids"] = ["SKA036"]
    assign_input["sdp"]["resources"]["receptors"] = ["SKA036"]
    tmc.force_change_of_obs_state(
        ObsState.IDLE,
        TestHarnessInputs(assign_input=DictJSONInput(assign_input)),
        wait_termination=True,
    )
    time.sleep(5)
    dish_63 = dishes.dish_master_dict["dish_063"]
    dish_63.SetDefective(ERROR_PROPAGATION_DEFECT)
    logger.info("<<< ASSIGN : %s TYPE: %s", assign_input, type(assign_input))


@given(
    parsers.re(
        r"the following GPM configurations are provided for version "
        r"(?P<version>[\d\.]+):\n"
        r"(?P<table>(?:\s*\|.*\|\s*\n?)+)",
        re.MULTILINE | re.DOTALL,
    ),
    target_fixture="gpm_config",
)
def given_a_gpm_json(version, table):
    """Build a GPM json from data provided in feature"""

    lines = [
        line.strip() for line in table.strip().split("\n") if line.strip()
    ]
    headers = [h.strip() for h in lines[0].split("|") if h.strip()]
    receptors = {}
    gpm_input_data = {}

    for row in lines[1:]:
        values = [v.strip() for v in row.split("|") if v.strip()]
        entry = dict(zip(headers, values))
        dish_id = entry["Dish_ID"].lower()
        bands = [b.strip() for b in entry["Bands"].split(",")]
        receptors[dish_id] = bands

    gpm_input_data = {"version": version, "receptors": receptors}

    logger.info(">>>> %s", gpm_input_data)
    return gpm_input_data


@when("the GPM configuration is applied via TMC")
def apply_gpm_to_dishes(tmc: TMCFacade, gpm_config):
    """Invoke SetGlobalPointingModel on dishes"""

    message, pytest.unique_id = tmc.central_node.SetGlobalPointingModel(
        json.dumps(gpm_config)
    )
    logger.info("Command ID: %s Message: %s", message, pytest.unique_id)


@then(
    parsers.re(
        r"TMC reports the status as below for the respective dish id:\n"
        r"(?P<table>.+)",
        re.MULTILINE | re.DOTALL,
    )
)
def tmc_reports_gpm_status_on_dish(
    tmc: TMCFacade, event_tracer: TangoEventTracer, table
):
    """Check the status of GPM on dish"""

    lines = [
        line.strip() for line in table.strip().split("\n") if line.strip()
    ]
    headers = [h.strip() for h in lines[0].split("|") if h.strip()]
    gpm_report = {}
    for row in lines[1:]:
        values = [v.strip() for v in row.split("|") if v.strip()]
        entry = dict(zip(headers, values))
        dish_id = entry["Dish_ID"].lower()
        status = entry["Status"]
        reason = entry["Reason"]
        gpm_report[dish_id] = {"status": status, "reason": reason}

    logger.info(" **** %s", gpm_report)
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
            tmc.central_node,
            "longRunningCommandResult",
            (pytest.unique_id[0], Anything),
        )
    )

    logger.info(">>>>>>> Assertion data: %s", assertion_data)
    assert 0
