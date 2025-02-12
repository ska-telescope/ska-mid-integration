@XTP-30258 @XTP-73598 @XTP-28347 @Team_HIMALAYA
	Scenario: TMC Validates and Reports K-Value set in Dish Leaf Nodes
		Given a TMC with already loaded Dish-VCC map version
		When the Dish Leaf Node is restarted
		And the Dish Leaf Node verifies k-value set on Dish Leaf Node and Dish Manager are identical
		Then Dish Leaf Node reports it to the Central Node
		And the Central Node continues with current operation as their are no discrepancies