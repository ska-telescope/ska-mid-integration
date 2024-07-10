"""Invoke Scan command on subarray Node."""

import logging

from tests.test_harness3.telescope_actions.telescope_action import (
    TelescopeAction,
)

LOGGER = logging.getLogger(__name__)


class SubarrayStoreScanData(TelescopeAction):
    """Invoke Scan command on subarray Node."""

    def __init__(self, input_string: str):
        super().__init__()
        self.input_string = input_string

    def _action(self):
        result, message = self.telescope.tmc.subarray_node.Scan(
            self.input_string
        )
        LOGGER.info("Invoked Scan on SubarrayNode")
        return result, message

    def expected_outcome(self):
        """No expected outcome for this action."""
        return []
