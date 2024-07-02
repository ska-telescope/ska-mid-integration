"""An action to move the central node to ON State."""

import logging

from tests.test_harness3.sut_structure.sut_action import SUTAction

LOGGER = logging.getLogger(__name__)


class MoveToOn(SUTAction):
    """An action to move the central node to ON State."""

    def _action(self):
        LOGGER.info("Moving the central node to ON state")

        self.tmc.move_central_node_to_on()
        self.csp.move_to_on()

    def expected_outcome(self):
        """No expected outcome for this action."""
        return []
