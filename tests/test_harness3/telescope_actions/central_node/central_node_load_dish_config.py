"""Invoke LoadDishCfg command on CentralNode."""

import json

from tests.test_harness3.telescope_actions.state_change_waiter import (
    ExpectedEvent,
)
from tests.test_harness3.telescope_actions.telescope_action import (
    TelescopeAction,
)


class CentralNodeLoadDishConfig(TelescopeAction):
    """Invoke LoadDishCfg command on CentralNode."""

    def __init__(self, dish_vcc_config: str):
        super().__init__()
        self.dish_vcc_config = dish_vcc_config

    def _action(self):
        result, message = self.telescope.tmc.central_node.LoadDishConfig(
            self.dish_vcc_config
        )
        return result, message

    def termination_condition(self):
        def _is_source_dish_cfg_changed(current_value, future_value):
            if not current_value and future_value:
                return False
            return json.loads(current_value) == json.loads(future_value)

        # TODO: be careful about this wait
        return [
            ExpectedEvent(
                device=self.telescope.tmc.csp_master_leaf_node,
                attribute="sourceDishVccConfig",
                predicate=lambda event: _is_source_dish_cfg_changed(
                    event.attribute_value, self.dish_vcc_config
                ),
            )
        ]
