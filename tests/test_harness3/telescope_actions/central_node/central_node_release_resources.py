"""Invoke ReleaseResources on the CentralNode."""


from ska_control_model import ObsState

from tests.test_harness3.telescope_actions.telescope_action import (
    TelescopeAction,
)
from tests.test_harness3.utils.state_change_waiter import ExpectedStateChange


class CentralNodeReleaseResources(TelescopeAction):
    """A class for releasing resources on the CentralNode."""

    def __init__(self, input_string: str):
        super().__init__()
        self.input_string = input_string

    def _action(self):
        result, message = self.telescope.tmc.central_node.ReleaseResources(
            self.input_string
        )
        return result, message

    def expected_outcome(self):
        return [
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
            # TODO: deal with this
            # self.waits.append(
            #     watch(Resource(self.tmc_subarraynode1)).to_become(
            #         "assignedResources", changed_to=None
            #     )
            # )
            ExpectedStateChange(
                self.telescope.csp.csp_subarray,
                "obsState",
                ObsState.EMPTY,
            ),
            ExpectedStateChange(
                self.telescope.sdp.sdp_subarray,
                "obsState",
                ObsState.EMPTY,
            ),
            ExpectedStateChange(
                self.telescope.tmc.subarray_node,
                "obsState",
                ObsState.EMPTY,
            ),
        ]
