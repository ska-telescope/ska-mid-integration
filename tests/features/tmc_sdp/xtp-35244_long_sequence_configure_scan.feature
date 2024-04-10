Feature:  TMC Mid executes long running sequences with real sdp devices
    @tmc_sdp @Team_SAHYADRI @XTP-35244 @XTP-29381
    Scenario Outline: TMC Mid executes configure-scan sequence of commands successfully

    Given Telescope is ON state
    When I assign resources to TMC SubarrayNode <subarray_id>
    And configure and scan TMC SubarrayNode <subarray_id> for each <scan_types> and <scan_ids>
    And end the configuration on TMC SubarrayNode <subarray_id>
    And release the resources on TMC SubarrayNode <subarray_id>
    Then TMC SubarrayNode <subarray_id> transitions to EMPTY ObsState

    Examples:
            |subarray_id   | scan_ids      | scan_types |
            |1             |["1"]          |["science_A"]  |
            |1             |["1","2"]      |["science_A" , "target:a"] |   #Test Configure-scan pair with different configuration with different scan id with same resources
            |1             |["1","2"]      |["science_A" , "science_A"] |  #Test Configure-scan pair with same configuration with different scan id with same resources
            |1             |["1","1"]      |["science_A" , "science_A"] |  ##Test Configure-scan pair with same configuration with same scan id with same resources
            |1             |["1","2","3"]  |["science_A"  , "target:a","callibration_B" ]|  #Test Configure-scan pair with different configuration with different scan id for multiple scan types with same resources



    @tmc_sdp @Team_SAHYADRI @XTP-35244 @XTP-29381
    Scenario Outline: TMC Mid executes multiple scan with same configuration successfully

    Given Telescope is ON state
    When I assign resources to TMC SubarrayNode <subarray_id>
    And configure and scan TMC SubarrayNode <subarray_id> for each <scan_types> and <scan_ids>
    And reperform scan with same configuration
    And end the configuration on TMC SubarrayNode <subarray_id>
    And release the resources on TMC SubarrayNode <subarray_id>
    Then TMC SubarrayNode <subarray_id> transitions to EMPTY ObsState

    Examples:
            |subarray_id  |scan_ids | scan_types |
            |1            |["1"]    |["science_A"]  |


    @tmc_sdp @Team_SAHYADRI @XTP-35244 @XTP-29381
    Scenario Outline: TMC Mid executes multiple scans with different configurations, intermittently ending configurations

    Given Telescope is ON state
    When I assign resources to TMC SubarrayNode <subarray_id>
    And configure and scan TMC SubarrayNode <subarray_id> for each <scan_types> and <scan_ids>
    And end the configuration on TMC SubarrayNode <subarray_id>
    And configure and scan TMC SubarrayNode <subarray_id> for <new_scan_types> and <new_scan_ids>
    And end the configuration on TMC SubarrayNode <subarray_id>
    And release the resources on TMC SubarrayNode <subarray_id>
    Then TMC SubarrayNode <subarray_id> transitions to EMPTY ObsState

    Examples:

     |subarray_id  | scan_ids | scan_types     | new_scan_ids  | new_scan_types|
     |1            |  ["1"]   | ["science_A"]  | ["2"]         | ["target:a"] |

