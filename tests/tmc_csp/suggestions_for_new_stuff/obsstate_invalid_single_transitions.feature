Feature: subarray Invalid Observation State Transitions

This feature covers invalid state transitions for a subarray during observation states,
focusing on command-triggered transitions that are not allowed in certain states.


Background:
  Given the telescope is turned ON
  Given the subarray 1 can be used

#
#  V=valid I=invalid

#           | EMPTY | RESOURCING | IDLE | CONFIGURING
#-----------+-------+------------+------+------------
#AssignRes. |   V   |     I      |  V   |     I
#ReleaseRes.|   I   |     I      |  V   |     I
#Configure  |   I   |     I      |  V   |     I
#Scan       |   I   |     I      |  I   |     I
#EndScan    |   I   |     I      |  I   |     I
#End        |   I   |     I      |  I   |     I
#Abort      |   I   |     V      |  V   |     V
#Restart    |   I   |     I      |  I   |     I

## EMPTY State Scenarios
Scenario: EMPTY - Invalid CMD ReleaseResources
  Given the subarray 1 is in the EMPTY state
  When the ReleaseResources command is sent to the subarray 1
  Then the subarray 1 should remain in the EMPTY state
  And the subarray 1 should report an invalid command error

Scenario: EMPTY - Invalid CMD Configure
  Given the subarray 1 is in the EMPTY state
  When the Configure command is sent to the subarray 1
  Then the subarray 1 should remain in the EMPTY state
  And the subarray 1 should report an invalid command error

Scenario: EMPTY - Invalid CMD Scan
  Given the subarray 1 is in the EMPTY state
  When the Scan command is sent to the subarray 1
  Then the subarray 1 should remain in the EMPTY state
  And the subarray 1 should report an invalid command error

Scenario: EMPTY - Invalid CMD EndScan
  Given the subarray 1 is in the EMPTY state
  When the EndScan command is sent to the subarray 1
  Then the subarray 1 should remain in the EMPTY state
  And the subarray 1 should report an invalid command error

Scenario: EMPTY - Invalid CMD End
  Given the subarray 1 is in the EMPTY state
  When the End command is sent to the subarray 1
  Then the subarray 1 should remain in the EMPTY state
  And the subarray 1 should report an invalid command error

Scenario: EMPTY - Invalid CMD Abort
  Given the subarray 1 is in the EMPTY state
  When the Abort command is sent to the subarray 1
  Then the subarray 1 should remain in the EMPTY state
  And the subarray 1 should report an invalid command error

Scenario: EMPTY - Invalid CMD Restart
  Given the subarray 1 is in the EMPTY state
  When the Restart command is sent to the subarray 1
  Then the subarray 1 should remain in the EMPTY state
  And the subarray 1 should report an invalid command error

## RESOURCING State Scenarios
Scenario: RESOURCING - Invalid CMD AssignResources
  Given the subarray 1 is in the RESOURCING state
  When the AssignResources command is sent to the subarray 1
  Then the subarray 1 should remain in the RESOURCING state
  And the subarray 1 should report an invalid command error

Scenario: RESOURCING - Invalid CMD ReleaseResources
  Given the subarray 1 is in the RESOURCING state
  When the ReleaseResources command is sent to the subarray 1
  Then the subarray 1 should remain in the RESOURCING state
  And the subarray 1 should report an invalid command error

Scenario: RESOURCING - Invalid CMD Configure
  Given the subarray 1 is in the RESOURCING state
  When the Configure command is sent to the subarray 1
  Then the subarray 1 should remain in the RESOURCING state
  And the subarray 1 should report an invalid command error

Scenario: RESOURCING - Invalid CMD Scan
  Given the subarray 1 is in the RESOURCING state
  When the Scan command is sent to the subarray 1
  Then the subarray 1 should remain in the RESOURCING state
  And the subarray 1 should report an invalid command error

Scenario: RESOURCING - Invalid CMD EndScan
  Given the subarray 1 is in the RESOURCING state
  When the EndScan command is sent to the subarray 1
  Then the subarray 1 should remain in the RESOURCING state
  And the subarray 1 should report an invalid command error

Scenario: RESOURCING - Invalid CMD End
  Given the subarray 1 is in the RESOURCING state
  When the End command is sent to the subarray 1
  Then the subarray 1 should remain in the RESOURCING state
  And the subarray 1 should report an invalid command error

Scenario: RESOURCING - Invalid CMD Restart
  Given the subarray 1 is in the RESOURCING state
  When the Restart command is sent to the subarray 1
  Then the subarray 1 should remain in the RESOURCING state
  And the subarray 1 should report an invalid command error

## IDLE State Scenarios
Scenario: IDLE - Invalid CMD Scan
  Given the subarray 1 is in the IDLE state
  When the Scan command is sent to the subarray 1
  Then the subarray 1 should remain in the IDLE state
  And the subarray 1 should report an invalid command error

Scenario: IDLE - Invalid CMD EndScan
  Given the subarray 1 is in the IDLE state
  When the EndScan command is sent to the subarray 1
  Then the subarray 1 should remain in the IDLE state
  And the subarray 1 should report an invalid command error

Scenario: IDLE - Invalid CMD End
  Given the subarray 1 is in the IDLE state
  When the End command is sent to the subarray 1
  Then the subarray 1 should remain in the IDLE state
  And the subarray 1 should report an invalid command error

Scenario: IDLE - Invalid CMD Restart
  Given the subarray 1 is in the IDLE state
  When the Restart command is sent to the subarray 1
  Then the subarray 1 should remain in the IDLE state
  And the subarray 1 should report an invalid command error

## CONFIGURING State Scenarios
Scenario: CONFIGURING - Invalid CMD AssignResources
  Given the subarray 1 is in the CONFIGURING state
  When the AssignResources command is sent to the subarray 1
  Then the subarray 1 should remain in the CONFIGURING state
  And the subarray 1 should report an invalid command error

Scenario: CONFIGURING - Invalid CMD ReleaseResources
  Given the subarray 1 is in the CONFIGURING state
  When the ReleaseResources command is sent to the subarray 1
  Then the subarray 1 should remain in the CONFIGURING state
  And the subarray 1 should report an invalid command error

Scenario: CONFIGURING - Invalid CMD Configure
  Given the subarray 1 is in the CONFIGURING state
  When the Configure command is sent to the subarray 1
  Then the subarray 1 should remain in the CONFIGURING state
  And the subarray 1 should report an invalid command error

Scenario: CONFIGURING - Invalid CMD Scan
  Given the subarray 1 is in the CONFIGURING state
  When the Scan command is sent to the subarray 1
  Then the subarray 1 should remain in the CONFIGURING state
  And the subarray 1 should report an invalid command error

Scenario: CONFIGURING - Invalid CMD EndScan
  Given the subarray 1 is in the CONFIGURING state
  When the EndScan command is sent to the subarray 1
  Then the subarray 1 should remain in the CONFIGURING state
  And the subarray 1 should report an invalid command error

Scenario: CONFIGURING - Invalid CMD End
  Given the subarray 1 is in the CONFIGURING state
  When the End command is sent to the subarray 1
  Then the subarray 1 should remain in the CONFIGURING state
  And the subarray 1 should report an invalid command error

Scenario: CONFIGURING - Invalid CMD Restart
  Given the subarray 1 is in the CONFIGURING state
  When the Restart command is sent to the subarray 1
  Then the subarray 1 should remain in the CONFIGURING state
  And the subarray 1 should report an invalid command error
#
#  V=valid I=invalid
#           | READY | SCANNING | ABORTING | ABORTED | FAULT | RESTARTING
#-----------+-------+----------+----------+---------+-------+------------
#AssignRes. |   I   |    I     |    I     |    I    |   I   |     I
#ReleaseRes.|   I   |    I     |    I     |    I    |   I   |     I
#Configure  |   V   |    I     |    I     |    I    |   I   |     I
#Scan       |   V   |    I     |    I     |    I    |   I   |     I
#EndScan    |   I   |    V     |    I     |    I    |   I   |     I
#End        |   V   |    I     |    I     |    I    |   I   |     I
#Abort      |   V   |    V     |    I     |    I    |   I   |     I
#Restart    |   I   |    I     |    I     |    V    |   V   |     I
#


## READY State Scenarios
Scenario: READY - Invalid CMD AssignResources
  Given the subarray 1 is in the READY state
  When the AssignResources command is sent to the subarray 1
  Then the subarray 1 should remain in the READY state
  And the subarray 1 should report an invalid command error

Scenario: READY - Invalid CMD ReleaseResources
  Given the subarray 1 is in the READY state
  When the ReleaseResources command is sent to the subarray 1
  Then the subarray 1 should remain in the READY state
  And the subarray 1 should report an invalid command error

Scenario: READY - Invalid CMD EndScan
  Given the subarray 1 is in the READY state
  When the EndScan command is sent to the subarray 1
  Then the subarray 1 should remain in the READY state
  And the subarray 1 should report an invalid command error

Scenario: READY - Invalid CMD Restart
  Given the subarray 1 is in the READY state
  When the Restart command is sent to the subarray 1
  Then the subarray 1 should remain in the READY state
  And the subarray 1 should report an invalid command error

## SCANNING State Scenarios
Scenario: SCANNING - Invalid CMD AssignResources
  Given the subarray 1 is in the SCANNING state
  When the AssignResources command is sent to the subarray 1
  Then the subarray 1 should remain in the SCANNING state
  And the subarray 1 should report an invalid command error

Scenario: SCANNING - Invalid CMD ReleaseResources
  Given the subarray 1 is in the SCANNING state
  When the ReleaseResources command is sent to the subarray 1
  Then the subarray 1 should remain in the SCANNING state
  And the subarray 1 should report an invalid command error

Scenario: SCANNING - Invalid CMD Configure
  Given the subarray 1 is in the SCANNING state
  When the Configure command is sent to the subarray 1
  Then the subarray 1 should remain in the SCANNING state
  And the subarray 1 should report an invalid command error

Scenario: SCANNING - Invalid CMD Scan
  Given the subarray 1 is in the SCANNING state
  When the Scan command is sent to the subarray 1
  Then the subarray 1 should remain in the SCANNING state
  And the subarray 1 should report an invalid command error

Scenario: SCANNING - Invalid CMD End
  Given the subarray 1 is in the SCANNING state
  When the End command is sent to the subarray 1
  Then the subarray 1 should remain in the SCANNING state
  And the subarray 1 should report an invalid command error

Scenario: SCANNING - Invalid CMD Restart
  Given the subarray 1 is in the SCANNING state
  When the Restart command is sent to the subarray 1
  Then the subarray 1 should remain in the SCANNING state
  And the subarray 1 should report an invalid command error

## ABORTING State Scenarios
Scenario: ABORTING - Invalid CMD AssignResources
  Given the subarray 1 is in the ABORTING state
  When the AssignResources command is sent to the subarray 1
  Then the subarray 1 should remain in the ABORTING state
  And the subarray 1 should report an invalid command error

Scenario: ABORTING - Invalid CMD ReleaseResources
  Given the subarray 1 is in the ABORTING state
  When the ReleaseResources command is sent to the subarray 1
  Then the subarray 1 should remain in the ABORTING state
  And the subarray 1 should report an invalid command error

Scenario: ABORTING - Invalid CMD Configure
  Given the subarray 1 is in the ABORTING state
  When the Configure command is sent to the subarray 1
  Then the subarray 1 should remain in the ABORTING state
  And the subarray 1 should report an invalid command error

Scenario: ABORTING - Invalid CMD Scan
  Given the subarray 1 is in the ABORTING state
  When the Scan command is sent to the subarray 1
  Then the subarray 1 should remain in the ABORTING state
  And the subarray 1 should report an invalid command error

Scenario: ABORTING - Invalid CMD EndScan
  Given the subarray 1 is in the ABORTING state
  When the EndScan command is sent to the subarray 1
  Then the subarray 1 should remain in the ABORTING state
  And the subarray 1 should report an invalid command error

Scenario: ABORTING - Invalid CMD End
  Given the subarray 1 is in the ABORTING state
  When the End command is sent to the subarray 1
  Then the subarray 1 should remain in the ABORTING state
  And the subarray 1 should report an invalid command error

Scenario: ABORTING - Invalid CMD Abort
  Given the subarray 1 is in the ABORTING state
  When the Abort command is sent to the subarray 1
  Then the subarray 1 should remain in the ABORTING state
  And the subarray 1 should report an invalid command error

Scenario: ABORTING - Invalid CMD Restart
  Given the subarray 1 is in the ABORTING state
  When the Restart command is sent to the subarray 1
  Then the subarray 1 should remain in the ABORTING state
  And the subarray 1 should report an invalid command error

## ABORTED State Scenarios
Scenario: ABORTED - Invalid CMD AssignResources
  Given the subarray 1 is in the ABORTED state
  When the AssignResources command is sent to the subarray 1
  Then the subarray 1 should remain in the ABORTED state
  And the subarray 1 should report an invalid command error

Scenario: ABORTED - Invalid CMD ReleaseResources
  Given the subarray 1 is in the ABORTED state
  When the ReleaseResources command is sent to the subarray 1
  Then the subarray 1 should remain in the ABORTED state
  And the subarray 1 should report an invalid command error

Scenario: ABORTED - Invalid CMD Configure
  Given the subarray 1 is in the ABORTED state
  When the Configure command is sent to the subarray 1
  Then the subarray 1 should remain in the ABORTED state
  And the subarray 1 should report an invalid command error

Scenario: ABORTED - Invalid CMD Scan
  Given the subarray 1 is in the ABORTED state
  When the Scan command is sent to the subarray 1
  Then the subarray 1 should remain in the ABORTED state
  And the subarray 1 should report an invalid command error

Scenario: ABORTED - Invalid CMD EndScan
  Given the subarray 1 is in the ABORTED state
  When the EndScan command is sent to the subarray 1
  Then the subarray 1 should remain in the ABORTED state
  And the subarray 1 should report an invalid command error

Scenario: ABORTED - Invalid CMD End
  Given the subarray 1 is in the ABORTED state
  When the End command is sent to the subarray 1
  Then the subarray 1 should remain in the ABORTED state
  And the subarray 1 should report an invalid command error

Scenario: ABORTED - Invalid CMD Abort
  Given the subarray 1 is in the ABORTED state
  When the Abort command is sent to the subarray 1
  Then the subarray 1 should remain in the ABORTED state
  And the subarray 1 should report an invalid command error

## FAULT State Scenarios
Scenario: FAULT - Invalid CMD AssignResources
  Given the subarray 1 is in the FAULT state
  When the AssignResources command is sent to the subarray 1
  Then the subarray 1 should remain in the FAULT state
  And the subarray 1 should report an invalid command error

Scenario: FAULT - Invalid CMD ReleaseResources
  Given the subarray 1 is in the FAULT state
  When the ReleaseResources command is sent to the subarray 1
  Then the subarray 1 should remain in the FAULT state
  And the subarray 1 should report an invalid command error

Scenario: FAULT - Invalid CMD Configure
  Given the subarray 1 is in the FAULT state
  When the Configure command is sent to the subarray 1
  Then the subarray 1 should remain in the FAULT state
  And the subarray 1 should report an invalid command error

Scenario: FAULT - Invalid CMD Scan
  Given the subarray 1 is in the FAULT state
  When the Scan command is sent to the subarray 1
  Then the subarray 1 should remain in the FAULT state
  And the subarray 1 should report an invalid command error

Scenario: FAULT - Invalid CMD EndScan
  Given the subarray 1 is in the FAULT state
  When the EndScan command is sent to the subarray 1
  Then the subarray 1 should remain in the FAULT state
  And the subarray 1 should report an invalid command error

Scenario: FAULT - Invalid CMD End
  Given the subarray 1 is in the FAULT state
  When the End command is sent to the subarray 1
  Then the subarray 1 should remain in the FAULT state
  And the subarray 1 should report an invalid command error

Scenario: FAULT - Invalid CMD Abort
  Given the subarray 1 is in the FAULT state
  When the Abort command is sent to the subarray 1
  Then the subarray 1 should remain in the FAULT state
  And the subarray 1 should report an invalid command error

## RESTARTING State Scenarios
Scenario: RESTARTING - Invalid CMD AssignResources
  Given the subarray 1 is in the RESTARTING state
  When the AssignResources command is sent to the subarray 1
  Then the subarray 1 should remain in the RESTARTING state
  And the subarray 1 should report an invalid command error

Scenario: RESTARTING - Invalid CMD ReleaseResources
  Given the subarray 1 is in the RESTARTING state
  When the ReleaseResources command is sent to the subarray 1
  Then the subarray 1 should remain in the RESTARTING state
  And the subarray 1 should report an invalid command error

Scenario: RESTARTING - Invalid CMD Configure
  Given the subarray 1 is in the RESTARTING state
  When the Configure command is sent to the subarray 1
  Then the subarray 1 should remain in the RESTARTING state
  And the subarray 1 should report an invalid command error

Scenario: RESTARTING - Invalid CMD Scan
  Given the subarray 1 is in the RESTARTING state
  When the Scan command is sent to the subarray 1
  Then the subarray 1 should remain in the RESTARTING state
  And the subarray 1 should report an invalid command error

Scenario: RESTARTING - Invalid CMD EndScan
  Given the subarray 1 is in the RESTARTING state
  When the EndScan command is sent to the subarray 1
  Then the subarray 1 should remain in the RESTARTING state
  And the subarray 1 should report an invalid command error

Scenario: RESTARTING - Invalid CMD End
  Given the subarray 1 is in the RESTARTING state
  When the End command is sent to the subarray 1
  Then the subarray 1 should remain in the RESTARTING state
  And the subarray 1 should report an invalid command error

Scenario: RESTARTING - Invalid CMD Abort
  Given the subarray 1 is in the RESTARTING state
  When the Abort command is sent to the subarray 1
  Then the subarray 1 should remain in the RESTARTING state
  And the subarray 1 should report an invalid command error

Scenario: RESTARTING - Invalid CMD Restart
  Given the subarray 1 is in the RESTARTING state
  When the Restart command is sent to the subarray 1
  Then the subarray 1 should remain in the RESTARTING state
  And the subarray 1 should report an invalid command error