Feature: TMC handles kValue validation	

	@XTP-44895 @XTP-28347 @Team_HIMALAYA
	Scenario: TMC Validates the kValue when all kvalues are same
		Given a Telescope in OFF state 
		When I issue the command LoadDishCfg on TMC with all same kValue
		And TMC subarray in ObsState IDLE
		Then I successfully invoke Configure command on TMC

	@XTP-44898 @XTP-28347 @Team_HIMALAYA
	Scenario: TMC Validates the kValue when all kvalues are different
		Given a Telescope in OFF state 
		When I issue the command LoadDishCfg on TMC with all different kValue
		And TMC subarray in ObsState IDLE
		Then I successfully invoke Configure command on TMC
