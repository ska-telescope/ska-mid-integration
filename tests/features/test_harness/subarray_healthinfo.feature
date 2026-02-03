Feature: Dish HealthInfo propagation to Subarray

  Background:
    Given Dishes are assigned to Subarray with Health State as OK
    And Subarray is configured successfully and Health State remains OK


  Scenario: Dish health failure is reflected in Subarray HealthInfo
    When band <active_band> is active and band <unavailable_band> becomes unavailable
    Then subarray health state becomes FAILED due to unavailable band