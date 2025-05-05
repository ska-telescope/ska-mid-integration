Scenario: Scan 
    Given the subarray is in the READY state
    When the Scan command is sent to the subarray
    Then the subarray should transition to the SCANNING state
    Then the subarray should transition to the READY state
