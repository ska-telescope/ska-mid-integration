
# SKA Mid Integration
This repository contains integration tests and related tools for the SKA Observatory's (SKAO) Assembly, Integration, and Verification (AIV) team working on the SKA Mid telescope. It includes deployment infrastructure for the Mid System Under Test (SUT) and the Test Equipment used in the Mid Integration Test Facility (ITF). Additionally, it provides pipelines to trigger verification and integration events for automated tests. 


## Documentation


Click below to access the TMC documentation.

[![Documentation Status](https://readthedocs.org/projects/ska-telescope-ska-mid-integration/badge/?version=latest)](https://developer.skao.int/projects/ska-mid-integration/en/latest/)



## Component Versions

The following table lists the key components of the SKA Mid Integration system and their respective versions:

| Component                | OCI Name                     | Version       |
|--------------------------|------------------------------|---------------|
| Mid-CBF                 | ska-mid-cbf-mcs             | 0.24.1-rc.1   |
| SKA-DISH                | ska-dish-lmc                | 6.0.0         |
| SKA-TMC                 | ska-tmc-mid                 | 0.13.1        |
| CSP-LMC                 | ska-csp-lmc-mid             | 0.24.1-rc.1   |
| SDP Master Leaf Node    | ska-tmc-sdpleafnodes        | 0.14.2        |
| SKA Mid CBF Leaf Node   | ska-mid-cbf-tmleafnode      | 1.1.0-rc.2    |


### Deployment of Subsystem in Integration 
 #### Deployment of Dish LMC Helm Chart
 * To Deploy dish lmc chart in integration run following command
    ```bash
    make k8s-install-chart
    ```
    All values required for deploying dish lmc can be provided in charts/tmc_pairwise/dish_lmc_values.yml file.

    Refer this link for set flag option https://gitlab.com/ska-telescope/ska-dish-lmc#-set-flag-options
    
    After running above command dish lmc with dish Id 001 deployed in provided Kubernetes Namespace(i.e KUBE_NAMESPACE)

    To deploy multiple dishes provide multiple values to global.dishes. 
    Example: `global.dishes={036,001,...}`

 * Uninstall dish lmc chart
    ```bash
    make k8s-uninstall-chart
    ```
 * Test dish lmc with TMC as an entrypoint
    To test Dish LMC within the TMC integration, you can set a specific flag to control whether you want to use a real device or a mock device. Here's how you can do it:
    ```bash
    --set tmc-mid.deviceServers.mocks.dish=true or false
    ```
    If you set "enabled" to true, Dish LMC will use a mock device for testing and if you set "enabled" to false, Dish LMC will use a real device for testing.
