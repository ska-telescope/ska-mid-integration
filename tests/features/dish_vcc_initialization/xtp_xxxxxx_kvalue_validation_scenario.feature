Feature: TMC handles kValue validation

	
	Scenario: TMC Validates the kValue when multiple kvalues are same
        Given a TMC
        And Telescope is in ON state 
        When I issue the command LoadDishCfg on TMC with multiple same kValue
        And TMC subarray in ObsState IDLE
        And I invoke Configure command on TMC
		Then the command is failed and <exception> is raised
        And the health state is DEGRADED
        Examples:
            |exception       |
            |Configure command failed: Error in invoking Configure command: K-values must be either all same or all different.|