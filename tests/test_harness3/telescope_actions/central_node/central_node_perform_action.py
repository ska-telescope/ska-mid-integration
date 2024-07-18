"""Execute provided command on CentralNode."""

from tests.test_harness3.telescope_actions.telescope_action import (
    TelescopeAction,
)
from tests.test_harness3.telescope_inputs.json_input import JSONInput


class CentralNodePerformAction(TelescopeAction):
    """A class for performing actions on the CentralNode."""

    def __init__(self, command_name: str, command_input: JSONInput):
        super().__init__()
        self.command_name = command_name
        self.command_input = command_input

    def _action(self):
        result, message = self.telescope.tmc.central_node.command_inout(
            self.command_name, self.command_input.get_json_string()
        )
        return result, message

    def termination_condition(self):
        return []
