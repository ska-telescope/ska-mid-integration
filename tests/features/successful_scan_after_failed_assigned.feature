Feature: Default

	#The scenario is provided to convey the intention, it should be refined.
	#The test should be repeated for several cases:
	#a) the AssignResources passes an invalid (malformed) JSON script
	#b) the AssignResources passes a JSON script that uses resources that are not available. 
	#In addition: 
	#c) execute a) and b) one afer the other, verify that the SUT responds as expected. 
	#d) execute b) and a) one after the other, verify that the SUT responds as expected.
	#e) execute a) at least three times, verify that the SUT responds as expected (i.e. can handle successive invalid commands).
	#d) execute b) at least three times, verify that the SUT responds as expected (i.e. can handle successive requests to assign resources that are not available).
	#Note: Error reporting for cases a) and b) may be different (find out details and update the scenario accordingly). 
	@XTP-20320 @XTP-28347 @SKA_mid
    Scenario: Successfully execute a scan after a failed attempt to assign resources
        Given a subarray <subarray_id> with resources <resources_list> in obsState EMPTY
        When I issue the command AssignResources passing an invalid JSON script to the subarray <subarray_id>
        Then the subarray <subarray_id> returns an error message
        And the subarray <subarray_id> remains in obsState EMPTY 
        When I issue the command AssignResources passing a correct JSON script
        Then the subarray transitions to obsState IDLE
        When I issue the command Configure passing a correct JSON script  
        Then the subarray transitions to obsState READY
        When I issue the command Scan
        Then the subarray transitions to obsState SCANNING
        When I issue the command EndScan 
        Then the subarray transitions to obsState READY
        And implements the teardown

        Examples:
        | subarray_id  | resources_list |
        | 1            | "SKA001"       |


    @XTP-20320 @XTP-28347 @SKA_mid
    Scenario: Successfully execute a scan after a successive failed attempt to assign resources
        Given a subarray <subarray_id> with resources <resources_list> in obsState EMPTY
        When I issue the command AssignResources passing an invalid JSON script to the subarray <subarray_id>
        Then the subarray <subarray_id> returns an error message
        When I issue the command AssignResources passing an invalid JSON script2 to the subarray <subarray_id>
        Then the subarray <subarray_id> returns an error message
        When I issue the command AssignResources passing an invalid JSON script3 to the subarray <subarray_id>
        Then the subarray <subarray_id> returns an error message
        And the subarray <subarray_id> remains in obsState EMPTY 
        When I issue the command AssignResources passing a correct JSON script
        Then the subarray transitions to obsState IDLE
        When I issue the command Configure passing a correct JSON script  
        Then the subarray transitions to obsState READY
        When I issue the command Scan
        Then the subarray transitions to obsState SCANNING
        When I issue the command EndScan 
        Then the subarray transitions to obsState READY
        And implements the teardown
        
        Examples:
        | subarray_id  | resources_list |
        | 1            | "SKA001"       |