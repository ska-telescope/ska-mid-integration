@XTP-78417 @XTP-28347 @Team_HIMALAYA
Scenario: TMC reject LoadDishCfg command if existing dish vcc config is in progress
	Given a TMC
	And a LoadDishCfg command is currently in progress
	When another LoadDishCfg command is issued
	Then TMC should reject the new LoadDishCfg command
	And the in-progress LoadDishCfg command should complete
	And the DishVccCommandStatus should transition to COMPLETED