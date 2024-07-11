# This BDD test performs TMC-Dish pairwise testing to verify CentralNode TelescopeHealthState
Scenario Outline: Verify CentralNode TelescopeHealthState
    Given a Telescope consisting of TMC, DISH, simulated CSP and simulated SDP
    And the Telescope is in ON state
    When the <devices> health state changes to <health_state>
    Then the telescope health state is <telescope_health_state>
    Examples:
    | devices | health_state | telescope_health_state |
    | spf device,dish | DEGRADED,DEGRADED | DEGRADED |
    | spfrx device,dish | FAILED,FAILED | FAILED |
    | spf device,dish | UNKNOWN,DEGRADED | DEGRADED |