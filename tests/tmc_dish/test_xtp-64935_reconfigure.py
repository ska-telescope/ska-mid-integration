import pytest
from pytest_bdd import parsers, scenario, when

from tests.conftest import LOGGER
from tests.resources.test_harness.helpers import prepare_json_args_for_commands
from tests.resources.test_support.common_utils.telescope_controls import (
    BaseTelescopeControl,
)

telescope_control = BaseTelescopeControl()


@pytest.mark.tmc_dish
@scenario(
    "../features/tmc_dish/xtp-64935.feature",
    "TMC validates reconfigure functionality with real dish",
)
def test_multiple_configure_functionality():
    """
    Test TMC allows reconfiguration

    """


@when(parsers.parse("the command configure is issued with {input_json1}"))
def send_configure(command_input_factory, input_json1, subarray_node):
    configure_json1 = prepare_json_args_for_commands(
        input_json1, command_input_factory
    )

    LOGGER.info("Invoking Configure command with input_json1")
    _, pytest.unique_id = subarray_node.execute_transition(
        "Configure", configure_json1
    )
    LOGGER.info("Configure-1 is invoked successfully")


@when(
    parsers.parse(
        "the next successive configure command is issued with {input_json2}"
    )
)
def send_next_configure(
    command_input_factory, input_json2, subarray_node, event_recorder
):
    configure_json = prepare_json_args_for_commands(
        input_json2, command_input_factory
    )

    LOGGER.info("Invoking Configure command with input_json1")
    _, pytest.unique_id = subarray_node.execute_transition(
        "Configure", configure_json
    )
    LOGGER.info("Configure-2 is invoked successfully")
