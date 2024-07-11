"""Invoke MoveToOn command on subarray Node."""

import logging

from tests.resources.test_support.common_utils.common_helpers import Resource
from tests.test_harness3.telescope_actions.telescope_action import (
    TelescopeAction,
)

# TODO: logging should not belong here
LOGGER = logging.getLogger(__name__)


class SubarrayMoveToOn(TelescopeAction):
    """Invoke MoveToOn command on subarray Node."""

    def _action(self):
        # TODO: why are we using strings instead of state enums?
        # which is the point where it's done a mapping between the two?
        if self.telescope.tmc.subarray_state != "ON":
            Resource(self.telescope.tmc.subarray_node).assert_attribute(
                "State"
            ).equals("OFF")
            result, message = self.telescope.tmc.subarray_node.On()
            LOGGER.info("Invoked ON on SubarrayNode")
            return (result, message)
        # pylint says inconsistent-return-statements,
        # what should be returned here?
        return None

    def termination_condition(self):
        return []
