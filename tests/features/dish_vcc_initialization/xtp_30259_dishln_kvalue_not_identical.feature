Feature: TMC handles initialization scenarios of setting and verifying Dish ID - VCC map

	
	@XTP-30259 @XTP-28347 @XTP-73598 @Team_HIMALAYA
	Scenario: TMC Validates and Reports K-Value discrepancy in Dish Leaf Nodes
		Given a TMC with already loaded Dish-VCC map version
		When the Dish Leaf Node is restarted
		And the Dish Leaf Node finds the k-value set on either of the Dish Leaf Node and Dish Manager are not identical
		Then Dish Leaf Node reports the discrepancy to the Central Node
		And the Central Node reports the same and prohibits any further observation command execution