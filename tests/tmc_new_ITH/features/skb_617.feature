Feature: Default

	#This test verifies that the TMC is able to successfully invoke the assignResources command when the SDP block is empty
	@XTP-XTP-86946 @TEAM_HIMALAYA
	Scenario: Test AssignResources with empty SDP block
		Given subarray is in observation state EMPTY
		When I invoke assign resources with empty SDP block
		Then AssignResources is successfully invoked on TMC