"""An action to move the central node to ON State."""

from tests.test_harness2.sut_structure.sut_action import SUTAction


class MoveToOn(SUTAction):
    """An action to move the central node to ON State."""

    def _action(self):
        self.tmc.move_central_node_to_on()
        self.csp.move_to_on()

    def expected_outcome(self):
        """No expected outcome for this action."""
        return []
