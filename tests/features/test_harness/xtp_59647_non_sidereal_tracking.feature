Feature: Default

	#This scenario is to test Non-sidereal tracking capabilities of TMC. Due to different sources being visible during different times of the day from Dish SKA001, the test scenario is worded in a way that one of the sources mentioned in the parameters is selected and the test case is executed accordingly.
	@XTP-59647 @XTP-28347 @Team_HIMALAYA
	Scenario: Non sidereal tracking in TMC
		Given a Subarray with resources assigned
		When I Configure it for tracking a non-sidereal object from <non_sidereal_objects>
		Then the Subarray is configured successfully
		And the dish is tracking the object
		Examples:
            |non_sidereal_objects               |
            |Sun,Venus,Mars,Saturn,Pluto        |
