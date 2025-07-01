Feature: Default

	#This test verifies that hardcoding present in SDP leaf node is removed and TMC is now able to accept assign resources json with SDP v1.0
	@XTP-84029 @XTP-28347 @TEAM_HIMALAYA
	Scenario: Test AssignResources with SDP v1.0 to verify fix for SKB-927
		Given subarray is in observation state EMPTY
		When I assign resources with SDP interface v1.0 to the TMC Subarray
		Then AssignResources is successfully invoked on SDP with provided version v1.0