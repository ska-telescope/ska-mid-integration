"""Dish Pointing Device Facade
"""

import tango


class DishPointingDeviceFacade:
    """A facade to expose the Dish Pointing Device to the tests."""

    def __init__(self) -> None:
        self._dish_pointing_device_dict = {
            "SKA001": tango.DeviceProxy("mid-tmc/dish-pointing/ska001"),
        }

    @property
    def dish_pointing_device_dict(self) -> dict[str, tango.DeviceProxy]:
        """The dish pointing Tango device proxies as a dictionary.

        The key is the dish name, as a string in the format "dish_XXX".
        """
        return self._dish_pointing_device_dict

    @property
    def dish_pointing_device_list(self) -> list[tango.DeviceProxy]:
        """The dish pointing Tango device proxies as a list."""
        return list(self._dish_pointing_device_dict.values())
