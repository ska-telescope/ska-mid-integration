@SP-4029
Feature: TMC Dish Pointing (ADR-95 and ADR-76)	
	@XTP-50437 @XTP-28347 @SKA_mid
	Scenario: TMC mid raises an alarm when it encounters NaN in received pointing calibration
		Given a TMC mid with already executed calibration scans
		When the Dish Leaf Node receives NaN number from SDP
		Then an alarm is raised for NaN found in last pointing data