"""A wrapper for emulated dishes."""

from tests.resources.test_harness.config.test_wrappers_configurations import (
    DishesConfiguration,
)
from tests.resources.test_harness.sys_components.dishes_wrapper import (
    DishesWrapper,
)
from tests.resources.test_harness.utils.emulated_teardown import (
    clear_command_call,
    reset_health_state,
    reset_transitions_data,
)


class EmulatedDishesWrapper(DishesWrapper):
    """A wrapper for emulated dishes."""

    def _pre_init_dish_names(
        self, dishes_configuration: DishesConfiguration
    ) -> None:
        """Do nothing when dishes are emulated.

        :param dishes_configuration: The dishes configuration.
        """
        pass

    def tear_down(self) -> None:
        """Tear down the emulated dishes."""
        reset_health_state(self.dish_master_list)
        clear_command_call(self.dish_master_list)
        reset_transitions_data(self.dish_master_list)
