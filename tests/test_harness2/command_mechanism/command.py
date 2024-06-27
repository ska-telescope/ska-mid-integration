"""A generic command executed over the test harness."""

import abc

from tests.test_harness2.command_mechanism.state_change_waiter import (
    ExpectedStateChange,
    StateChangeWaiter,
)


class TestHarnessCommand(abc.ABC):
    """A command executed over the test harness.

    A command is an operation that is executed over the test harness.
    A command is made by:

    - an action, which is a method that does something on the test harness
        interacting with its components (TMC, CSP, SDP, etc);
    - an expected outcome, expressed as a set of expected state changes
        in the test harness components devices.

    Command is an abstract class, partially inspired by the
    https://refactoring.guru/design-patterns/command design pattern
    (since it is an action described by a class), partially
    by the https://refactoring.guru/design-patterns/template-method principle
    (since it is an abstract class with a few template methods to define
    to implement a concrete command).

    To create a new command, you create a subclass of TestHarnessCommand
    and you implement the abstract methods (the action and the expected
    outcome). To run a command, you create an instance of the command
    and you call its execute method.
    """

    COMMAND_TIMEOUT = 30

    def __init__(self) -> None:
        super().__init__()
        self._state_change_waiter = StateChangeWaiter()

    @abc.abstractmethod
    def _action(self):
        """The action executed by the command."""
        pass

    @abc.abstractmethod
    def expected_outcome(self) -> list[ExpectedStateChange]:
        """The expected outcome of the command."""
        pass

    def execute(self):
        """Execute the command.

        This method executes the command by performing the action
        and waiting for the expected outcome to occur. If the expected
        outcome does not occur within a timeout,
        a TimeoutError is raised.

        :raises TimeoutError: If the expected outcome does not occur
        """

        # Subscribe to the expected state changes
        self._state_change_waiter.reset()
        self._state_change_waiter.add_expected_state_changes(
            self.expected_outcome()
        )

        # Execute the action
        self._action()

        # Wait for the expected state changes to occur within a timeout
        # or raise a TimeoutError
        self._state_change_waiter.wait_all(self.COMMAND_TIMEOUT)
