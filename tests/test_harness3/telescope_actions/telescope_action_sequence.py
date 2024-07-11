"""A sequence of `TelescopeAction`s, executed in order."""

from tests.test_harness3.telescope_actions.telescope_action import (
    TelescopeAction,
)


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
        steps: list[TelescopeAction],
    ) -> None:
        """Initialize the action with the telescope and the steps.

        :param steps: The list of sub-actions to be executed.
        """
        super().__init__()
        self.steps = steps

    def _action(self):
        """Execute the sequence of actions."""
        for step in self.steps:
            step.execute()

    def termination_condition(self):
        return []
