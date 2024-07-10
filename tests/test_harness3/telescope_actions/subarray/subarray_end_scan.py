"""Invoke EndScan command on subarray Node."""


import logging

from ska_control_model import ObsState

from tests.test_harness3.telescope_actions.telescope_action import (
    TelescopeAction,
)
from tests.test_harness3.utils.state_change_waiter import ExpectedStateChange

LOGGER = logging.getLogger(__name__)


class SubarrayEndScan(TelescopeAction):
    """Invoke EndScan command on subarray Node."""

    def _action(self):
        result, message = self.telescope.tmc.subarray_node.EndScan()
        LOGGER.info("Invoked EndScan on SubarrayNode")
        return result, message

    def expected_outcome(self):
        return [
            ExpectedStateChange(
                self.telescope.tmc.csp_subarray_leaf_node,
                "cspSubarrayObsState",
                ObsState.READY,
            ),
            ExpectedStateChange(
                self.telescope.tmc.sdp_subarray_leaf_node,
                "sdpSubarrayObsState",
                ObsState.READY,
            ),
            ExpectedStateChange(
                self.telescope.csp.csp_subarray, "obsState", ObsState.READY
            ),
            ExpectedStateChange(
                self.telescope.sdp.sdp_subarray, "obsState", ObsState.READY
            ),
            ExpectedStateChange(
                self.telescope.tmc.subarray_node, "obsState", ObsState.READY
            ),
        ]
