.. _admin_mode:

Impact of AdminMode on command execution
=========================================

#. The command invocation is not allowed from TMC CentralNode if the adminMode of any subsystem's controller is  either **OFFLINE or NOT_FITTED**
#. The command invocation is not allowed from TMC SubarrayNode if the adminMode of any subsystem's subarray is  either **OFFLINE or NOT_FITTED**
#. The command invocation is allowed if the adminMode of subsystem is either **ONLINE or ENGINEERING**