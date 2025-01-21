@SP-4029
Feature: TMC Dish Pointing (ADR-95 and ADR-76)
	#Ticket created to develop Feature around Dish Pointing around (ADR-95), also added work related to ADR-76.
	#
	#Most of the ADR-95 related functionality agreed to be implemented in PI21, was implemented in PI21. The only remaining change is to pass the ScanID via the Scan command. See ADR-95 page in Confluence: 
	#[https://confluence.skatelescope.org/display/SWSI/ADR-95+DISH+Pointing]
	#
	#Details for the changes to be introduced by ADR-76 are outlined on the Confluence page, but will be finalized in the week beginning on March 11. The estimates and plans should be based on the currently listed content of the ADR-76 page: 
	#[https://confluence.skatelescope.org/display/SWSI/ADR-76+SDP+to+TMC+real-time+pointing+calibration+interface]
	#
	#In general what is expected from TMC for ADR-76 is:
	# # Finalise and integrate interfaces with SDP for SDP reading of intended & actual pointing (offsets) 
	# # TMC when directed by the "configure" command (see below) to wait for and retrieve calibration results from SDP and apply them to the DISH LMC 
	# # Be able to parse the optional extra directives in the configure JSON sent by OSO (or otherwise loaded) that determine control over applying the calibration results from SDP:
	# ## If no directive present do nothing;
	# ## If the directive is to "apply" the calibration results then apply them as in (2) above;
	# ## If the directive is to "reset" then instruct DISH. LMC to reset the static pointing model to its default. Note: In the first meeting discussing SS-120 ([https://confluence.skatelescope.org/display/SE/2024-03-11+SS-120+AA0.5+Mid+interferometric+pointing+calibration)] it was decided that "reset to default" can be taken to mean set the offset values back to 0.0, 0.0.

	
	@XTP-49147 @XTP-73595 @XTP-28347
	Scenario Outline: TMC is able to process pointing calibration received from SDP during five point calibration scan.
		Given a TMC
		When I assign resources for five point calibration scan
		And I configure subarray for a calibration scan
		And I invoke calibration scan five times with scan ids <scan_ids>
		Then the TMC receive pointing calibration from SDP and applies them to the Dishes
		
		Examples:
			| scan_ids                                                            |
			| 1,2,3,4,5                                                           |