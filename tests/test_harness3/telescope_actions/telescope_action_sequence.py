"""A sequence of `TelescopeAction`s, executed in order."""

from tests.test_harness3.telescope_actions.telescope_action import (
    TelescopeAction,
)
from tests.test_harness3.telescope_structure.telescope_wrapper import (
    TelescopeWrapper,
)
from tests.test_harness3.utils.state_change_waiter import ExpectedStateChange


class TelescopeActionSequence(TelescopeAction):
    """A sequence of `TelescopeAction`s, executed in order.

    This action is used to group a sequence of actions together, so that the
    can be executed as a single action. The sub-actions are executed in
    the order they are provided and the synchronization is done after
    each sub action (step).

    By default, the expected outcome is none, but it can be overridden by
    a subclass to provide a custom expected outcome.
    """

    def __init__(
        self,
        telescope: TelescopeWrapper,
        steps: list[TelescopeAction],
    ) -> None:
        """Initialize the action with the telescope and the steps.

        :param telescope: The target telescope.
        :param steps: The list of sub-actions to be executed.
        """
        super().__init__(telescope)
        self.steps = steps

    def _action(self):
        """Execute the sequence of actions."""
        for step in self.steps:
            step.execute()

    def expected_outcome(self) -> list[ExpectedStateChange]:
        return []
