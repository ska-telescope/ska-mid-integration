Feature: Default

	#This test covers the scan functionality with TMC and mock devices for the subsequent subsystems.
	@XTP-80579 @XTP-28347
	Scenario: Test scan command
		Given the subarray is in the READY state
		When the Scan command is sent to the subarray
		Then the subarray should transition to the SCANNING state
		Then the subarray should transition to the READY state