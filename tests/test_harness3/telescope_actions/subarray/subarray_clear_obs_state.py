"""Clear TMC subarray obs state, putting it into the "EMPTY" state."""

from ska_control_model import ObsState

from tests.test_harness3.telescope_actions.expected_event import (
    ExpectedStateChange,
)
from tests.test_harness3.telescope_actions.subarray.subarray_abort import (
    SubarrayAbort,
)
from tests.test_harness3.telescope_actions.subarray.subarray_restart import (
    SubarrayRestart,
)
from tests.test_harness3.telescope_actions.telescope_action import (
    TelescopeAction,
)


class SubarrayClearObsState(TelescopeAction):
    """Clear TMC subarray obs state, putting it into the "EMPTY" state."""

    def _action(self):
        if self.telescope.tmc.subarray_node.obsState in [
            ObsState.IDLE,
            ObsState.RESOURCING,
            ObsState.READY,
            ObsState.CONFIGURING,
            ObsState.SCANNING,
        ]:
            SubarrayAbort().execute()
            SubarrayRestart().execute()

        # NOTE: if the subarray is in ABORTING state,
        # it would be good to wait for it to transition to ABORTED
        # so Restart can be called safely

        elif self.telescope.tmc.subarray_node.obsState in [
            ObsState.ABORTED,
        ]:
            SubarrayRestart().execute()

        # NOTE: if the subarray is in RESETTING state,
        # it would be good to wait for it to transition to EMPTY

    def termination_condition(self):
        res = [
            ExpectedStateChange(
                self.telescope.csp.csp_subarray, "obsState", ObsState.EMPTY
            ),
            ExpectedStateChange(
                self.telescope.sdp.sdp_subarray, "obsState", ObsState.EMPTY
            ),
            ExpectedStateChange(
                self.telescope.tmc.subarray_node, "obsState", ObsState.EMPTY
            ),
        ]

        # csp subarray leaf node may not be yet initialized
        if self.telescope.tmc.is_subarray_initialized():
            res.extend(
                [
                    ExpectedStateChange(
                        self.telescope.tmc.csp_subarray_leaf_node,
                        "cspSubarrayObsState",
                        ObsState.EMPTY,
                    ),
                    ExpectedStateChange(
                        self.telescope.tmc.sdp_subarray_leaf_node,
                        "sdpSubarrayObsState",
                        ObsState.EMPTY,
                    ),
                ]
            )

        return res
