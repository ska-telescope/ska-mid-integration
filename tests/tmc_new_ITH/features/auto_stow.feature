Feature: Automatic Stowing Functionality on DishLeafNode Devices

       
	@XTP-101898 @XTP-101883 @TEAM_HIMALAYA
	Scenario: Validate auto stow on gust speed
		Given a DishLeafNode device in STANDBY_LP mode
		When the gust speed is greater than the max allowed gust speed
		Then the dish automatically stows
    
	@XTP-101900 @XTP-101883 @TEAM_HIMALAYA
	Scenario: Validate auto stow on mean wind speed exceed
		Given a DishLeafNode device in STANDBY_LP mode
		When the mean wind speed over a measurement time window exceeds the configured maximum threshold
		Then the dish automatically stows

	@XTP-101901 @XTP-101883 @TEAM_HIMALAYA
	Scenario: Validate auto stow on operational wind speed exceed
		Given a DishLeafNode device in STANDBY_LP mode
		When the operational wind speed over a measurement time window exceeds the maximum allowed operational windspeed
		Then the dish automatically stows

	@XTP-101902 @XTP-101883 @TEAM_HIMALAYA
	Scenario: Validate auto stow on operational wind speed exceed threshold percentage
		Given a DishLeafNode device in STANDBY_LP mode
		When the difference between operational wind speeds exceeds the configured percentage threshold
		Then the dish automatically stows
    
	@XTP-101903 @XTP-101883 @TEAM_HIMALAYA
	Scenario: Validate auto stow on max temp
		Given a DishLeafNode device in STANDBY_LP mode
		When the temperature exceeds the configured maximum temperature threshold
		Then the dish automatically stows

	@XTP-101904 @XTP-101883 @TEAM_HIMALAYA
	Scenario: Validate auto stow on max temp exceeds threshold for specific time
		Given a DishLeafNode device in STANDBY_LP mode
		When the temperature change over a specified time window exceeds the configured threshold
		Then the dish automatically stows