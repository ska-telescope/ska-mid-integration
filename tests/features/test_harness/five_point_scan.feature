@XTP-28838 @XTP-73598 @XTP-73596 @XTP-73595 @XTP-28347
	Scenario Outline: TMC implements five point calibration scan: TMC executes five point calibration scan successfully.
		Given a TMC
		And a subarray configured for a calibration scan
		And the subarray is in READY obsState
		When I perform four partial configurations with json <partial_configuration_json> and scans
		Then the subarray executes the commands successfully and is in READY obsState
		
		Examples:
		| partial_configuration_json                                                            |
		| partial_configure_1,partial_configure_2,partial_configure_3,partial_configure_4       |