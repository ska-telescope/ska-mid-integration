"""Execute provided command on subarray Node."""

import logging

from tests.test_harness3.telescope_actions.telescope_action import (
    TelescopeAction,
)

LOGGER = logging.getLogger(__name__)


class SubarrayExecuteTransition(TelescopeAction):
    """Execute provided command on subarray Node."""

    def __init__(self, command_name: str, argin=None):
        super().__init__()
        self.command_name = command_name
        self.argin = argin

    def _action(self):
        if self.command_name is not None:
            result, message = self.telescope.tmc.subarray_node.command_inout(
                self.command_name, self.argin
            )
            LOGGER.info(f"Invoked {self.command_name} on SubarrayNode")
            return (
                result,
                message,
            )
        # pylint says inconsistent-return-statements,
        # what should be returned here?
        return None

    def termination_condition(self):
        return []
