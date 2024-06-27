"""A generic action executed over the SUT."""

import abc

from tests.test_harness2.command_mechanism.state_change_waiter import (
    ExpectedStateChange,
    StateChangeWaiter,
)
from tests.test_harness2.sut_structure.csp_wrapper import CSPWrapper
from tests.test_harness2.sut_structure.dishes_wrapper import DishesWrapper
from tests.test_harness2.sut_structure.sdp_wrapper import SDPWrapper
from tests.test_harness2.sut_structure.tmc_wrapper import TMCWrapper


class SUTAction(abc.ABC):
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

    COMMAND_TIMEOUT = 30

    def __init__(self) -> None:
        super().__init__()
        self._state_change_waiter = StateChangeWaiter()

        self.tmc: TMCWrapper = None
        self.csp: CSPWrapper = None
        self.sdp: SDPWrapper = None
        self.dishes: DishesWrapper = None

    @abc.abstractmethod
    def _action(self):
        """The action executed by the command."""
        pass

    @abc.abstractmethod
    def expected_outcome(self) -> list[ExpectedStateChange]:
        """The expected outcome of the command."""
        pass

    def set_sut_components(
        self,
        tmc: TMCWrapper,
        csp: CSPWrapper,
        sdp: SDPWrapper,
        dishes: DishesWrapper,
    ) -> None:
        """Set the SUT components for the action.

        :param tmc: The TMC component of the SUT.
        :param csp: The CSP component of the SUT.
        :param sdp: The SDP component of the SUT.
        :param dishes: The Dishes component of the SUT.
        """
        self.tmc = tmc
        self.csp = csp
        self.sdp = sdp
        self.dishes = dishes

    def execute(self):
        """Execute the command.

        This method executes the command by performing the action
        and waiting for the expected outcome to occur. If the expected
        outcome does not occur within a timeout,
        a TimeoutError is raised.

        :raises TimeoutError: If the expected outcome does not occur
            within a timeout.
        :raises ValueError: If the SUT components are not set.
        """
        if not all([self.tmc, self.csp, self.sdp, self.dishes]):
            raise ValueError(
                "The SUT components must be set before executing the command."
            )

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
