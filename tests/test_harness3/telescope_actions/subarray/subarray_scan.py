"""Invoke Scan command on subarray Node."""

import logging

from ska_control_model import ObsState

from tests.test_harness3.telescope_actions.expected_event import (
    ExpectedStateChange,
)
from tests.test_harness3.telescope_actions.telescope_action import (
    TelescopeAction,
)

LOGGER = logging.getLogger(__name__)


class SubarrayScan(TelescopeAction):
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

    def termination_condition(self):
        """No expected outcome for this action."""
        return [
            ExpectedStateChange(
                self.telescope.tmc.csp_subarray_leaf_node,
                "cspSubarrayObsState",
                ObsState.SCANNING,
            ),
            ExpectedStateChange(
                self.telescope.tmc.sdp_subarray_leaf_node,
                "sdpSubarrayObsState",
                ObsState.SCANNING,
            ),
            ExpectedStateChange(
                self.telescope.csp.csp_subarray, "obsState", ObsState.SCANNING
            ),
            ExpectedStateChange(
                self.telescope.sdp.sdp_subarray, "obsState", ObsState.SCANNING
            ),
            ExpectedStateChange(
                self.telescope.tmc.subarray_node, "obsState", ObsState.SCANNING
            ),
        ]
