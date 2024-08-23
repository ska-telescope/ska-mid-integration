@SP-4209
Feature: TMC Dish Pointing (ADR-95 and ADR-76)
	@XTP-60480 @SKA_mid
	Scenario Outline: TMC Behavior During correction key handling
		Given a TMC
		When I configure the subarray with correction key <correction_key>
		Then the dish leaf node receives correction key from SDP and reset all the Dishes
		And is in READY obsState

    Examples:
        | correction_key |
        |    RESET       |