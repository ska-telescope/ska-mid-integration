Feature:  TMC Mid executes long running sequences with real csp devices
    @tmc_csp @Team_SAHYADRI @XTP-29381 @XTP-40175
    Scenario Outline: TMC Mid executes configure-scan sequence of commands successfully

    Given Telescope is ON state
    When I assign resources to TMC SubarrayNode <subarray_id>
    And configure and scan TMC SubarrayNode <subarray_id> for each <scan_types> and <scan_ids>
    And end the configuration on TMC SubarrayNode <subarray_id>
    And release the resources on TMC SubarrayNode <subarray_id>
    Then TMC SubarrayNode <subarray_id> transitions to EMPTY ObsState

    Examples:
            |subarray_id   | scan_ids      | scan_types                                  |
            |1             |["1"]          |["science_A"]                                |
            |1             |["1","2"]      |["science_A" , "target:a"]                   |
            |1             |["1","2"]      |["science_A" , "science_A"]                  |
            |1             |["1","1"]      |["science_A" , "science_A"]                  |
            |1             |["1","2","3"]  |["science_A" , "target:a", "calibration:b" ]|



    @tmc_csp @Team_SAHYADRI @XTP-29381 @XTP-40176
    Scenario Outline: TMC Mid executes multiple scan with same configuration successfully

    Given Telescope is ON state
    When I assign resources to TMC SubarrayNode <subarray_id>
    And configure and scan TMC SubarrayNode <subarray_id> for each <scan_types> and <scan_ids>
    And reperform scan with same configuration and new scan id
    And end the configuration on TMC SubarrayNode <subarray_id>
    And release the resources on TMC SubarrayNode <subarray_id>
    Then TMC SubarrayNode <subarray_id> transitions to EMPTY ObsState

    Examples:
            |subarray_id  |scan_ids | scan_types    |
            |1            |["1"]    |["science_A"]  |