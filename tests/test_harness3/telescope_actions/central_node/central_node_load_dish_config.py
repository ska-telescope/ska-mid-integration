"""Invoke LoadDishCfg command on CentralNode."""

import json

from ska_tango_testing.integration.event import ReceivedEvent

from tests.test_harness3.telescope_actions.telescope_action import (
    TelescopeAction,
)
from tests.test_harness3.utils.state_change_waiter import ExpectedEvent


class CentralNodeLoadDishConfig(TelescopeAction):
    """Invoke LoadDishCfg command on CentralNode."""

    def __init__(self, telescope, dish_vcc_config: str):
        super().__init__(telescope)
        self.dish_vcc_config = dish_vcc_config

    def _action(self):
        result, message = self.telescope.tmc.central_node.LoadDishConfig(
            self.dish_vcc_config
        )
        return result, message

    def expected_outcome(self):
        def is_source_dish_cfg_changed(current_value, future_value):
            if not current_value and future_value:
                return False
            return json.loads(current_value) == json.loads(future_value)

        def state_change_predicate(event: ReceivedEvent) -> bool:
            return (
                event.has_device(self.telescope.tmc.csp_master_leaf_node)
                and event.has_attribute("sourceDishVccConfig")
                and is_source_dish_cfg_changed(
                    event.attribute_value, self.dish_vcc_config
                )
            )

        # TODO: be careful about this wait
        return [ExpectedEvent(state_change_predicate)]
