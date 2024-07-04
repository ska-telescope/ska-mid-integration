"""Clear TMC subarray obs state, putting it into the "EMPTY" state."""

from tests.test_harness3.telescope_actions.subarray.subarray_abort import (
    SubarrayAbort,
)
from tests.test_harness3.telescope_actions.subarray.subarray_restart import (
    SubarrayRestart,
)
from tests.test_harness3.telescope_actions.telescope_action import (
    TelescopeAction,
)
from tests.test_harness3.utils.state_change_waiter import ExpectedStateChange


class SubarrayClearObsState(TelescopeAction):
    """Clear TMC subarray obs state, putting it into the "EMPTY" state."""

    def _action(self):
        if self.telescope.tmc.subarray_obs_state in [
            "IDLE",
            "RESOURCING",
            "READY",
            "CONFIGURING",
            "SCANNING",
        ]:
            SubarrayAbort(self.telescope).execute()
            SubarrayRestart(self.telescope).execute()
        elif self.telescope.tmc.subarray_obs_state == "ABORTED":
            SubarrayRestart(self.telescope).execute()

    def expected_outcome(self) -> list[ExpectedStateChange]:
        return []
