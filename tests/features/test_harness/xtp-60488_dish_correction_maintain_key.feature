@SP-4209
Feature: TMC Dish Pointing (ADR-95 and ADR-76)
	@XTP-60488 @SKA_mid
	Scenario Outline: TMC Behavior During correction key handling
		Given a TMC
		When five point calibration scan performed on given subarray using correction key <correction_key> 
		Then the dish leaf node receive correction key from SDP and reset all the Dishes

    Examples:
        | correction_key |
        |    MAINTAIN    |