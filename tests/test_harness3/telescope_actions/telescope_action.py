"""A generic action executed over the SUT."""

import abc

from tests.test_harness3.telescope_structure.telescope_wrapper import (
    TelescopeWrapper,
)
from tests.test_harness3.utils.state_change_waiter import (
    ExpectedStateChange,
    StateChangeWaiter,
)


class TelescopeAction(abc.ABC):
    """A generic action executed over the SUT and its components.

    An action over the SUT is a command made by:

    - the action itself, which is the procedure that interacts
        with SUT components (TMC, CSP, SDP, Dishes);
    - a synchronization mechanism, which waits for the SUT components
        to reach certain states after the action is performed (
        i.e., the expected outcome).

    This class is a template for the actions that can be executed over
    the SUT. To create a new action, you create a subclass of SUTAction
    and you implement the abstract methods
    :py:meth:`_action` and :py:meth:`expected_outcome` to define the
    action and the expected outcome, respectively. To run an action,
    you create an instance of it, you init it with the SUT components
    and then you call its execute method.

    SUTAction is an abstract class, partially inspired by the
    https://refactoring.guru/design-patterns/command design pattern
    (since it is an action described by a class), partially
    by the https://refactoring.guru/design-patterns/template-method principle
    (since it is an abstract class with a few template methods to define
    to implement a concrete command).
    """

    # TODO: deal action result
    # TODO: fix documentation

    COMMAND_TIMEOUT = 30

    def __init__(self, telescope: TelescopeWrapper) -> None:
        super().__init__()
        self.telescope = telescope
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
            within a timeout.
        """
        # Subscribe to the expected state changes
        self._state_change_waiter.reset()
        self._state_change_waiter.add_expected_state_changes(
            self.expected_outcome()
        )

        # Execute the action
        res = self._action()

        # Wait for the expected state changes to occur within a timeout
        # or raise a TimeoutError
        self._state_change_waiter.wait_all(self.COMMAND_TIMEOUT)

        return res
