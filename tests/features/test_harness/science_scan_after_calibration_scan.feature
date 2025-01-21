@XTP-28839 @XTP-73598 @XTP-73595 @XTP-28347 @Team_HIMALAYA
	Scenario: TMC implements five point calibration scan: TMC executes Science scan after calibration successfully.
		Given a TMC
		When five point calibration scan performed on given subarray
		Then the dish leaf node receive calibration solutions from SDP and applies them to the Dishes
		And is in READY obsState