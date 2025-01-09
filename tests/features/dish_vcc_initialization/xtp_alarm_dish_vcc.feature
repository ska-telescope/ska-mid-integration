Feature: Test alarm condition when the kValue is not set

	
	@XTP-30395 @XTP-28347 @XTP-73598 @Team_HIMALAYA
	Scenario: TMC validates and raises alarm when K-Value not set in Dish Leaf Nodes
		Given a TMC with already loaded Dish-VCC map version
		When the Dish Leaf Node is restarted
		And the Dish Leaf Node finds k-value not set on Dish Leaf Node
		Then the alarm is raised for kValue not set
		And the Central Node reports the same and prohibits any further command execution