"""A wrapper for production dishes."""

from tango.db import Database

from tests.test_harness2.config.test_wrappers_configurations import (
    DishesConfiguration,
)
from tests.test_harness2.sys_components.dishes_wrapper import DishesWrapper


class ProductionDishesWrapper(DishesWrapper):
    """A wrapper for production dishes."""

    def _pre_init_dish_names(
        self, dishes_configuration: DishesConfiguration
    ) -> None:
        """Initialize real dishes in a Tango database.

        :param dishes_configuration: The dishes configuration.
        """
        # Create database object for TMC TANGO DB
        self.db = Database()

        # Create database object for Dish1 TANGO DB
        dish1_tango_host = dishes_configuration.dish_master1_name.split("/")[2]
        dish1_host = dish1_tango_host.split(":")[0]
        dish1_port = dish1_tango_host.split(":")[1]
        self.dish1_db = Database(dish1_host, dish1_port)

        # Get the Dish1 device class and server
        dish1_info = self.dish1_db.get_device_info(
            "mid-dish/dish-manager/SKA001"
        )
        self.dish1_dev_class = dish1_info.class_name
        self.dish1_dev_server = dish1_info.ds_full_name

    def tear_down(self):
        """Tear down the production dishes does nothing."""
        pass
