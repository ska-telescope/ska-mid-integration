"""Invoke MoveToOff command on subarray Node."""

import logging

from tests.resources.test_support.common_utils.common_helpers import Resource
from tests.test_harness3.telescope_actions.telescope_action import (
    TelescopeAction,
)

LOGGER = logging.getLogger(__name__)


class SubarrayMoveToOff(TelescopeAction):
    """Invoke MoveToOff command on subarray Node."""

    def _action(self):
        Resource(self.telescope.tmc.subarray_node).assert_attribute(
            "State"
        ).equals("ON")
        result, message = self.telescope.tmc.subarray_node.Off()
        LOGGER.info("Invoked OFF on SubarrayNode")
        return (result, message)

    def termination_condition(self):
        return []
