@XTP-81360 @XTP-28347
Scenario Outline: TMC Mid execute mosiac scan
	Given TMC Subarray is in observation state IDLE
	And a subarray configured for a mosaic scan with multiple groups
	And the subarray is in READY obsState
	When I perform partial configurations with <x_offsets> <y_offsets> offsets followed by scans
	Then the subarray executes the commands successfully and is in READY obsState
	Examples:
		| x_offsets        | y_offsets        |
		| -5.0,5.0         | 5.0,1.0          |