Feature: Dish HealthInfo propagation to Subarray

  Background:
    Given Dishes are assigned to Subarray with Health State as OK
    And Subarray is configured successfully and Health State remains OK


  Scenario: Dish health failure is reflected in Subarray HealthInfo
    When band <active_band> is active and band <unavailable_band> becomes unavailable
    Then subarray health state becomes <expected_health_state> due to unavailable band

    Examples:
        | active_band | unavailable_band | expected_health_state |
        | B1          | B1               | FAILED                |
        | B1          | B2               | OK                    |