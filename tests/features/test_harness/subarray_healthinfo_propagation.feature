Scenario: Subarray health becomes DEGRADED when Band 5 is unavailable while Band 1 is in use
    Given Dishes are assigned to Subarray with Health State as OK
    And Subarray is configured successfully and Health State remains OK
    When Band 1 is in use and Band 5 becomes unavailable
    Then subarray health state becomes DEGRADED due to unavailable Band 5