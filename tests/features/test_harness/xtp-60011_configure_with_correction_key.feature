@XTP-60011 @XTP-73595 @XTP-28347
	Scenario: Configure the telescope having TMC and Dish Subsystems with "UPDATE "correction key
		Scenario Outline: TMC Behavior During correction key handling
		    Given a TMC
		    When I configure the subarray with correction key <correction_key> 
		    Then the dish leaf node receive correction key from SDP and applies them to the Dishes
		    And is in READY obsState
		
		    Examples:
		        | correction_key |
		        |    UPDATE      |