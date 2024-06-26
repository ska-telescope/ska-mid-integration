"""A wrapper for a production CSP."""

from tests.test_harness2.config.test_wrappers_configurations import (
    CSPConfiguration,
)
from tests.test_harness2.helpers import wait_csp_master_off
from tests.test_harness2.sys_components.csp_wrapper import CSPWrapper


class ProductionCSPWrapper(CSPWrapper):
    """A wrapper for a production CSP.

    TODO: describe differences.
    """

    def __init__(
        self, csp_configuration: CSPConfiguration, all_production: bool = False
    ):
        """Initialize the production CSP wrapper.

        :param csp_configuration: the CSP configuration.
        :param all_production: a flag that tell whether all components
            are production. It is needed in the move to on method.
        """
        super().__init__(csp_configuration)
        self.all_production = all_production

    def move_to_on(self) -> None:
        if not self.all_production:
            # NOTE: in old code this line was BEFORE
            # self.central_node.TelescopeOn(). Empirically,
            # it seems the order not to matter, but I am not sure.

            # NOTE: why CSP should be in OFF state when I want the telescope
            # to be ON? It seems a contradiction.
            if self.csp_master.adminMode != 0:
                self.csp_master.adminMode = 0
            wait_csp_master_off()

    def move_to_off(self) -> None:
        """Move to OFF for production test wrapper does nothing."""
        pass

    def tear_down(self) -> None:
        """Tear down production test wrapper does nothing."""
        pass
