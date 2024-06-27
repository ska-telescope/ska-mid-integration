"""Create real or emulated test harness components."""
from tests.test_harness2.central_node_mid import CentralNodeWrapperMid
from tests.test_harness2.config.configuration_factory import (
    TestHarnessConfigurationFactory,
)
from tests.test_harness2.emulated_components.csp_wrapper import (
    EmulatedCSPWrapper,
)
from tests.test_harness2.emulated_components.dishes_wrapper import (
    EmulatedDishesWrapper,
)
from tests.test_harness2.emulated_components.sdp_wrapper import (
    EmulatedSDPWrapper,
)
from tests.test_harness2.production_components.csp_wrapper import (
    ProductionCSPWrapper,
)
from tests.test_harness2.production_components.dishes_wrapper import (
    ProductionDishesWrapper,
)
from tests.test_harness2.production_components.sdp_wrapper import (
    ProductionSDPWrapper,
)
from tests.test_harness2.sys_components.csp_wrapper import CSPWrapper
from tests.test_harness2.sys_components.dishes_wrapper import DishesWrapper
from tests.test_harness2.sys_components.sdp_wrapper import SDPWrapper
from tests.test_harness2.sys_components.tmc_wrapper import TMCWrapper


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
            tmc_wrapper=self.create_tmc_wrapper(),
            sdp_wrapper=self.create_sdp_wrapper(),
            csp_wrapper=self.create_csp_wrapper(),
            dishes_wrapper=self.create_dishes_wrapper(),
        )

    def create_tmc_wrapper(self) -> TMCWrapper:
        """Create a TMC wrapper.

        return: A TMC wrapper instance.
        """
        return TMCWrapper(self.config_factory.get_TMC_configuration())

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
