"""Execute provided command on CentralNode."""

from tests.test_harness3.telescope_actions.telescope_action import (
    TelescopeAction,
)


class CentralNodePerformAction(TelescopeAction):
    """A class for performing actions on the CentralNode."""

    def __init__(self, telescope, command_name: str, input_json: str):
        super().__init__(telescope)
        self.command_name = command_name
        self.input_json = input_json

    def _action(self):
        result, message = self.telescope.tmc.central_node.command_inout(
            self.command_name, self.input_json
        )
        return result, message

    def expected_outcome(self):
        return []
