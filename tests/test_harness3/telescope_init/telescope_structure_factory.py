"""Create real or emulated test harness components."""
from tests.test_harness3.telescope_config.configuration_factory import (
    TestHarnessConfigurationFactory,
)
from tests.test_harness3.telescope_structure.csp_devices import CSPDevices
from tests.test_harness3.telescope_structure.dishes_devices import (
    DishesDevices,
)
from tests.test_harness3.telescope_structure.emulated.csp_devices import (
    EmulatedCSPDevices,
)
from tests.test_harness3.telescope_structure.emulated.dishes_devices import (
    EmulatedDishesDevices,
)
from tests.test_harness3.telescope_structure.emulated.sdp_devices import (
    EmulatedSDPDevices,
)
from tests.test_harness3.telescope_structure.production.csp_devices import (
    ProductionCSPDevices,
)
from tests.test_harness3.telescope_structure.production.dishes_devices import (
    ProductionDishesDevices,
)
from tests.test_harness3.telescope_structure.production.sdp_devices import (
    ProductionSDPDevices,
)
from tests.test_harness3.telescope_structure.sdp_devices import SDPDevices
from tests.test_harness3.telescope_structure.telescope_wrapper import (
    TelescopeWrapper,
)
from tests.test_harness3.telescope_structure.tmc_devices import TMCDevices


class TelescopeStructureFactory:
    """Given a configuration, create real or emulated test harness."""

    def __init__(self):
        """Initialize the factory."""
        self.config_factory = TestHarnessConfigurationFactory()

    @property
    def _emulation_config(self):
        return self.config_factory.emulation_configuration

    def create_telescope_wrapper(self) -> TelescopeWrapper:
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

        # TODO: could TelescopeWrapper and its components be singletons (?)
        # or the singleton may be achieved through fixtures

        return TelescopeWrapper(
            tmc=self.create_tmc_wrapper(),
            sdp=self.create_sdp_wrapper(),
            csp=self.create_csp_wrapper(),
            dishes=self.create_dishes_wrapper(),
        )

    def create_tmc_wrapper(self) -> TMCDevices:
        """Create a TMC wrapper.

        return: A TMC wrapper instance.
        """
        return TMCDevices(self.config_factory.get_TMC_configuration())

    def create_sdp_wrapper(self) -> SDPDevices:
        """Create a SDP wrapper.

        return: A SDP wrapper instance.
        """
        if self._emulation_config.sdp:
            return EmulatedSDPDevices(
                self.config_factory.get_SDP_configuration()
            )

        return ProductionSDPDevices(
            self.config_factory.get_SDP_configuration()
        )

    def create_csp_wrapper(self) -> CSPDevices:
        """Create a CSP wrapper.

        return: A CSP wrapper instance.
        """
        if self._emulation_config.csp:
            return EmulatedCSPDevices(
                self.config_factory.get_CSP_configuration()
            )

        return ProductionCSPDevices(
            csp_configuration=self.config_factory.get_CSP_configuration(),
            all_production=self._emulation_config.all_production,
        )

    def create_dishes_wrapper(self) -> DishesDevices:
        """Create a dishes wrapper.

        return: A dishes wrapper instance.
        """
        if self._emulation_config.dish:
            return EmulatedDishesDevices(
                self.config_factory.get_dish_configuration()
            )

        return ProductionDishesDevices(
            self.config_factory.get_dish_configuration()
        )
