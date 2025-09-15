Feature: Default

	#This test verifies that hardcoding present in SDP Subarray mock devices is removed and TMC is now able to accept configure command json with scan_type provided in AssignResources json
    @TEAM_HIMALAYA
	Scenario: Test Configure command to verify skb-918
		Given subarray is in observation state EMPTY
		And I assign resources with scan_type_id <scan_type_id> to TMC Subarray
        When I invoke configure command with scan_type_id <scan_type_id> on TMC Subarray
        Then mock SDP subarray mock successfully executes the Configure command and goes to READY obsstate
		Examples:
            | scan_type_id  |
            | science6      |
            | target:c      |
            | calibration:x | 