"""Create subarray devices for the requested subarray."""

from tests.test_harness3.telescope_actions.telescope_action import (
    TelescopeAction,
)


class SetSubarrayId(TelescopeAction):
    """Create subarray devices for the requested subarray."""

    def __init__(self, subarray_id: int):
        super().__init__()
        self.subarray_id = subarray_id

    def _action(self):
        self.telescope.sdp.set_subarray_id(self.subarray_id)
        self.telescope.csp.set_subarray_id(self.subarray_id)
        self.telescope.tmc.set_subarray_id(self.subarray_id)

    def expected_outcome(self):
        return []
