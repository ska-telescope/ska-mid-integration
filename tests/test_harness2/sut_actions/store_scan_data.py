"""Invoke Scan command on subarray Node."""

import logging

from tests.test_harness2.sut_structure.sut_action import SUTAction

LOGGER = logging.getLogger(__name__)


class StoreScanData(SUTAction):
    """Invoke Scan command on subarray Node."""

    def __init__(self, input_string: str):
        super().__init__()
        self.input_string = input_string

    def _action(self):
        result, message = self.tmc.subarray_node.Scan(self.input_string)
        LOGGER.info("Invoked Scan on SubarrayNode")
        return result, message

    def expected_outcome(self):
        """No expected outcome for this action."""
        return []
