Feature: Default

	#Verify the output_host and output_port in configure json send to csp subarray
	@XTP-45178 @XTP-28347 @SKA_mid 
	Scenario: Verify the output_host and output_port in configure json send to csp subarray 
		Given the telescope is in ON state
		And TMC subarray in ObsState IDLE
		When I invoke configure command on TMC subarray
		Then TMC subarray invokes configure on csp with json containing output_host and output_port
		And the TMC subarray transitions to ObsState READY