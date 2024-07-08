"""A wrapper for emulated dishes."""

from tests.test_harness3.telescope_config.components_config import (
    DishesConfiguration,
)
from tests.test_harness3.telescope_structure.dishes_devices import (
    DishesDevices,
)
from tests.test_harness3.utils.emulated_teardown import (
    clear_command_call,
    reset_health_state,
    reset_transitions_data,
)


class EmulatedDishesDevices(DishesDevices):
    """A wrapper for emulated dishes."""

    def _pre_init_dish_names(
        self, dishes_configuration: DishesConfiguration
    ) -> None:
        """Do nothing when dishes are emulated.

        :param dishes_configuration: The dishes configuration.
        """
        pass

    def clear_command_call(self) -> None:
        """Clear the command call on the Dishes."""
        clear_command_call(self.dish_master_list)

    def reset_transitions_data(self) -> None:
        """Reset the transitions data on the Dishes."""
        reset_transitions_data(self.dish_master_list)

    def reset_health_state(self) -> None:
        """Reset the health state on the Dishes."""
        reset_health_state(self.dish_master_list)
