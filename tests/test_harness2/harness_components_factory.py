"""Create real or emulated test harness components."""
from tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
from tests.resources.test_harness.config.configuration_factory import (
    TestHarnessConfigurationFactory,
)
from tests.resources.test_harness.emulated_components.csp_wrapper import (
    EmulatedCSPWrapper,
)
from tests.resources.test_harness.emulated_components.dishes_wrapper import (
    EmulatedDishesWrapper,
)
from tests.resources.test_harness.emulated_components.sdp_wrapper import (
    EmulatedSDPWrapper,
)
from tests.resources.test_harness.production_components.csp_wrapper import (
    ProductionCSPWrapper,
)
from tests.resources.test_harness.production_components.dishes_wrapper import (
    ProductionDishesWrapper,
)
from tests.resources.test_harness.production_components.sdp_wrapper import (
    ProductionSDPWrapper,
)
from tests.resources.test_harness.sys_components.csp_wrapper import CSPWrapper
from tests.resources.test_harness.sys_components.dishes_wrapper import (
    DishesWrapper,
)
from tests.resources.test_harness.sys_components.sdp_wrapper import SDPWrapper


class HarnessComponentsFactory:
    """Given a configuration, create real or emulated test harness."""

    def __init__(self):
        """Initialize the factory."""
        self.config_factory = TestHarnessConfigurationFactory()

    @property
    def _emulation_config(self):
        return self.config_factory.emulation_configuration

    def create_central_node_wrapper(self) -> CentralNodeWrapperMid:
        """Create a central node wrapper (i.e., test harness entry point).

        return: A central node wrapper instance.
        """
        # TODO: add exaustive logging to describe what am I creating. This may
        # include:
        # - which sub-components are intended to be used
        #   (production or emulated configuration)
        # - how are they configured (device names, etc.)
        # - what's the actual state of the system (some version information
        #   asked directly to the devices, etc.)

        return CentralNodeWrapperMid(
            tmc_configuration=self.config_factory.get_TMC_configuration(),
            sdp_wrapper=self.create_sdp_wrapper(),
            csp_wrapper=self.create_csp_wrapper(),
            dishes_wrapper=self.create_dishes_wrapper(),
        )

    def create_sdp_wrapper(self) -> SDPWrapper:
        """Create a SDP wrapper.

        return: A SDP wrapper instance.
        """
        if self._emulation_config.sdp:
            return EmulatedSDPWrapper(
                self.config_factory.get_SDP_configuration()
            )

        return ProductionSDPWrapper(
            self.config_factory.get_SDP_configuration()
        )

    def create_csp_wrapper(self) -> CSPWrapper:
        """Create a CSP wrapper.

        return: A CSP wrapper instance.
        """
        if self._emulation_config.csp:
            return EmulatedCSPWrapper(
                self.config_factory.get_CSP_configuration()
            )

        return ProductionCSPWrapper(
            csp_configuration=self.config_factory.get_CSP_configuration(),
            all_production=self._emulation_config.all_production,
        )

    def create_dishes_wrapper(self) -> DishesWrapper:
        """Create a dishes wrapper.

        return: A dishes wrapper instance.
        """
        if self._emulation_config.dish:
            return EmulatedDishesWrapper(
                self.config_factory.get_dish_configuration()
            )

        return ProductionDishesWrapper(
            self.config_factory.get_dish_configuration()
        )
