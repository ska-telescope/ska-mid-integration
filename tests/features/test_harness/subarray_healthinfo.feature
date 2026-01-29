Feature: Dish HealthInfo propagation to Subarray

  Background:
    Given the subarray is in ON state
    And dishes are assigned to the subarray

  Scenario: Dish health failure is reflected in Subarray HealthInfo
    When dish "ska001" capability state becomes UNAVAILABLE
    Then subarray health info should show dish "ska001" as FAILED
    And the health info reason should contain "Requested band"

  Scenario: Dish health recovers and Subarray HealthInfo is updated
    Given dish "ska001" is in FAILED state
    When dish "ska001" capability state becomes AVAILABLE
    Then subarray health info should show dish "ska001" as OK