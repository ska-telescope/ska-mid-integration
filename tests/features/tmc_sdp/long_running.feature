Feature:  TMC executes long running sequences with real sdp devices
    @tmc_sdp @Team_SAHYADRI
    Scenario Outline: TMC executes long sequence of commands successfully

    Given Telescope is ON state
    When I assign resources to TMC SubarrayNode <subarray_id>
    And configure and scan TMC SubarrayNode <subarray_id> for each <scan_types> and <scan_ids>


    Examples:
            |subarray_id  | scan_ids | scan_types |
            |1            |  1        | ["science_A"]  |
