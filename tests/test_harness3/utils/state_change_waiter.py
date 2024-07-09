"""A tool to wait a set of state changes from multiple Tango devices."""

import logging
from dataclasses import dataclass
from typing import Any, Callable

from ska_tango_testing.integration.event import ReceivedEvent
from ska_tango_testing.integration.tracer import TangoEventTracer
from tango import DeviceProxy


@dataclass
class ExpectedStateChange:
    """An expected state change in a Tango device attribute.

    This class represents an expected state change in a Tango device,
    as a partial outcome of a command execution. The expected state can be
    defined in two ways:

    1. by a device, an attribute, and an expected value;
    2. by an arbitrary custom predicate.

    If one of the two conditions is met, the state change is considered
    occurred.
    """

    device: DeviceProxy | str | None
    """The Tango device or its name you expect to change state."""

    attribute: str | None
    """The attribute (name) you expect to change state."""

    expected_value: Any | None
    """The expected value of the attribute."""

    predicate: Callable[[ReceivedEvent], bool] | None = None

    def __post_init__(self):
        if self.predicate is None and (
            self.device is None
            or self.attribute is None
            or self.expected_value is None
        ):
            raise ValueError(
                "You must provide either a predicate or a device, "
                "an attribute, and an expected value."
            )

    def _device_to_str(self) -> str:
        if isinstance(self.device, DeviceProxy):
            return self.device.dev_name()
        return self.device

    def __str__(self) -> str:
        if self.predicate is not None:
            return (
                f"Expected custom predicate {self.predicate} to be satisfied."
            )

        return (
            f"Expected device.attribute {self._device_to_str()}"
            f".{self.attribute} to be {self.expected_value}"
        )

    def event_matches_state_change(self, event: ReceivedEvent) -> bool:
        """Check if an event matches the expected state change.

        :param event: The event to check.
        :return: True if the event matches the expected state change,
            False otherwise.
        """
        if self.predicate is not None:
            return self.predicate(event)

        return (
            event.has_device(self.device)
            and event.has_attribute(self.attribute)
            and event.attribute_value == self.expected_value
        )


class StateChangeWaiter:
    """A tool to wait for a set of state changes from multiple Tango devices.

    This class is used to wait for a set of state changes to occur
    on multiple Tango devices. You use this class by creating an
    instance of it, progressively adding state changes to wait for,
    and then calling the `wait_all` method to wait for all the state
    changes to occur (or for a timeout to occur). If all the state
    changes occur before the timeout, the execution continues, else
    it will be raised an exception.

    An instance of this class can be shared among multiple classes, so
    you can separate the responsibility of knowing what conditions
    to wait foreach group of devices (e.g., a TMC class may know what
    to wait for the TMC devices, and a CSP class may know what to wait
    for the CSP devices, etc.) and also move the `wait_all` call in a
    common orchestrator class (that doesn't need to know the details
    of what to wait for).

    Calling the method `reset` you will clear the list of expected
    state changes, so you can reuse the same instance for multiple
    actions.
    """

    def __init__(self) -> None:
        self.event_tracer = TangoEventTracer()
        self.pending_state_changes: list[ExpectedStateChange] = []

    def add_expected_state_changes(
        self,
        state_changes: list[ExpectedStateChange],
    ) -> None:
        """Add a list of expected state changes to wait for.

        :param state_changes: A list of expected state changes to wait for.
        """
        for expected_state_change in state_changes:
            self.pending_state_changes.append(expected_state_change)
            self.event_tracer.subscribe_event(
                expected_state_change.device,
                expected_state_change.attribute,
            )

    def _is_state_change_occurred(
        self,
        state_change: ExpectedStateChange,
    ) -> bool:
        """Check if a state change has already occurred in the event tracer.

        :param state_change: The expected state change to check.
        :return: True if the state change has occurred, False otherwise.
        """
        for event in self.event_tracer.events:
            if state_change.event_matches_state_change(event):
                return True

        return False

    def wait_all(self, timeout: int | float):
        """Wait for all the expected state changes to occur.

        :param timeout: The maximum time (in seconds) to wait for
            the state changes.

        :raises TimeoutError: If not all the expected state changes
            occurred within the timeout.
        """
        if not self.pending_state_changes:
            return

        res = self.event_tracer.query_events(
            # build a predicate that checks if all the state changes
            # have occurred in the event tracer (NOTE: it ignores instead
            # the usual point-wise check that is commonly used for
            # event tracer queries).
            predicate=lambda _: all(
                self._is_state_change_occurred(state_change)
                for state_change in self.pending_state_changes
            ),
            timeout=timeout
            # NOTE: this implementation may be slightly computationally
            # inefficient, but it re-uses existing components and it is
            # very readable and easy to understand.
        )

        # if no event matches the predicate (i.e., at least one of the
        # state changes has not occurred within the timeout), raise an
        # exception.
        if not res:
            msg = (
                "Not all the expected state changes occurred within "
                f"a timeout of {timeout} seconds."
            )

            happened_state_changes = []
            not_happened_state_changes = []

            for state_change in self.pending_state_changes:
                if self._is_state_change_occurred(state_change):
                    happened_state_changes.append(str(state_change))
                else:
                    not_happened_state_changes.append(str(state_change))

            if happened_state_changes:
                msg += "\n\nThe following state changes occurred:\n"
                msg += "\n".join(happened_state_changes)

            if not_happened_state_changes:
                msg += "\n\nThe following state changes did not occur:\n"
                msg += "\n".join(not_happened_state_changes)

            raise TimeoutError(msg)

        logging.info(
            "All the expected state changes occurred. Report:"
            "\n"
            + "\n".join(
                str(state_change)
                for state_change in self.pending_state_changes
            )
        )

    def reset(self):
        """Clear the list of expected state changes."""
        self.event_tracer.unsubscribe_all()
        self.event_tracer.clear_events()
        self.pending_state_changes = []
