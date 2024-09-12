@SP-4209
Feature: TMC Dish Pointing (ADR-95 and ADR-76)
	@XTP-60488 @SKA_mid
	Scenario Outline: TMC Behavior During correction key handling
		Given a TMC
		When I configure subarray with existed offsets using correction key <correction_key> 
		Then the dish leaf node validates existed offsets  

    Examples:
        | correction_key |
        |    MAINTAIN    |