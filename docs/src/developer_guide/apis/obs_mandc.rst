.. _obs_apis:

===========================
Observation Execution APIs
===========================

The observation execution can be done by following a sequence of APIs as follows:

* `Resource allocation <https://developer.skao.int/projects/ska-tmc-centralnode/en/latest/developer_guide/api/ska_tmc_centralnode.commands.html#module-ska_tmc_centralnode.commands.assign_resources_command>`_
* `Configure a scan <https://developer.skao.int/projects/ska-tmc-subarraynode/en/latest/developer_guide/api/ska_tmc_subarraynode.commands.mid.html#configure-command>`_
* `Perform scan <https://developer.skao.int/projects/ska-tmc-subarraynode/en/latest/developer_guide/api/ska_tmc_subarraynode.commands.mid.html#scan-command>`_
* `End a scan <https://developer.skao.int/projects/ska-tmc-subarraynode/en/latest/developer_guide/api/ska_tmc_subarraynode.commands.mid.html#end-scan-command>`_
* `Resource de-allocation <https://developer.skao.int/projects/ska-tmc-centralnode/en/latest/developer_guide/api/ska_tmc_centralnode.commands.html#module-ska_tmc_centralnode.commands.release_resources_command>`_

Before performing any observation related operation it is necessary that the telescope is in ON state.
