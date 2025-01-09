@SP-3715
Feature: Enable and Demonstrate 5-point calibration using TMC
	#*See:*
	# * SP-3630 for corresponding SDP feature.
	# * SP-3705 for related OSO feature.
	#
	#*Who?*
	# * Control system developers.
	# * SDP real-time pipeline developers.
	# * Commissioning scientists.
	#
	#*What?*
	# * Integrated Mid software system (including TMC, Dish LMC, SDP (coordinate with SP-3630),  and OSO-scripting (coordinate with SP-3705)) capable of executing pointing offset calibration observations.
	# * A manual test of the integrated system working on a simulated five-point reference pointing observation, driven by a Jupiter notebook.
	#
	#*Why?*
	# * This functionality is required early in Mid AA0.5 commissioning.
	# * Opportunity to validate the interfaces between OSO-scripting, TMC, Dish LMC and SDP for this observing mode.

	
	@XTP-28838 @XTP-73595 @XTP-73596 @XTP-73598 @SKA_mid
	Scenario Outline: TMC behaviour during five point calibration scan.
		Given a TMC
		And a subarray configured for a calibration scan
		And the subarray is in READY obsState
		When I perform four partial configurations with json <partial_configuration_json> and scans
		Then the subarray executes the commands successfully and is in READY obsState
	
		Examples:
		| partial_configuration_json                                                            |
		| partial_configure_1,partial_configure_2,partial_configure_3,partial_configure_4       |