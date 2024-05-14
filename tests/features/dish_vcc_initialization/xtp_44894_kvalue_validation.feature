Feature: TMC handles kValue validation	
	@XTP-44894 @XTP-28347 @Team_HIMALAYA
	Scenario: TMC Validates the kValue when multiple kvalues are same
		Given a Telescope in OFF state 
		When I issue the command LoadDishCfg on TMC with multiple same kValue
		And TMC subarray in ObsState IDLE
		And I invoke Configure command on TMC
		Then the command is failed and the health state of the subarray is DEGRADED
