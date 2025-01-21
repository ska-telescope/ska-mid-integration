@XTP-30253 @XTP-73598 @XTP-28347 @Team_HIMALAYA
	Scenario: TMC should report Dish-VCC config set as False when Dish-VCC Config is mismatch
		Given TMC with default version of dish vcc map
		When I make Dish-VCC version on CSP Master Leaf Node empty and Restart CSPMasterLeafNode   
		Then TMC should set Dish-VCC config set to False after Restart
		And TMC should report that Dish-VCC version mismatch between CSPMasterLeafNode and CSPMaster