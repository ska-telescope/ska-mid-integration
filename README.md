# SKA Mid Deployment Repository

This repository contains deployment tools and related infrastructure for the SKA Observatory's (SKAO) Assembly, Integration, and Verification (AIV) team working on the SKA Mid telescope. It includes deployment infrastructure for the Mid System Under Test (SUT) and the Test Equipment used in the Mid Integration Test Facility (ITF). Additionally, it provides pipelines to trigger verification and integration events for automated deployments.

## Documentation

Click below to access the TMC documentation.

[![Documentation Status](https://readthedocs.org/projects/ska-telescope-ska-mid-integration/badge/?version=latest)](https://developer.skao.int/projects/ska-mid-integration/en/latest/)


### Deployment of Subsystem in Integration 
 #### Deployment of Dish LMC Helm Chart
 * To deploy the dish LMC chart in integration, run the following command:
    ```bash
    make k8s-install-chart DISH_SIMULATION_ENABLED=false
    ```
    All values required for deploying the dish LMC can be provided in the `charts/tmc_pairwise/dish_lmc_values.yml` file.

    Refer to this link for set flag options: https://gitlab.com/ska-telescope/ska-dish-lmc#-set-flag-options
    
    After running the above command, the dish LMC with dishes IDs
    (001 ,100,036,063) is deployed in the provided Kubernetes Namespace (i.e., `KUBE_NAMESPACE`).

    To deploy  dishes,run the command make `k8s-install-chart DISH_SIMULATION_ENABLED=false`

 * Uninstall the dish LMC chart:
    ```bash
    make k8s-uninstall-chart
    ```


 #### Deployment of SDP LMC Helm Chart
 * To deploy the SDP LMC chart in integration, run the following command:
    ```bash
    make k8s-install-chart SDP_SIMULATION_ENABLED=false
    ```
    All values required for deploying the SDP LMC can be provided in the `charts/tmc_pairwise/sdp_lmc_values.yml` file.

    
    After running the above command, the SDP LMC will get
    deployed in the provided Kubernetes Namespace (i.e., `KUBE_NAMESPACE`).


 * Uninstall the dish LMC chart:
    ```bash
    make k8s-uninstall-chart

 #### Deployment of CSP LMC Helm Chart
 * To deploy the CSP LMC chart in integration, run the following command:
    ```bash
    make k8s-install-chart CSP_SIMULATION_ENABLED=false
    ```
    All values required for deploying the CSP LMC can be provided in the `charts/tmc_pairwise/csp_lmc_values.yml` file.

    
    After running the above command, the CSP LMC will get
    deployed in the provided Kubernetes Namespace (i.e., `KUBE_NAMESPACE`).


 * Uninstall the dish LMC chart:
    ```bash
    make k8s-uninstall-chart

## Overview
The SKA Telescope system is divided into two telescopes:

1. **Low Telescope**
2. **Mid Telescope**

Each telescope involves two deployment phases:

1. **Pairwise Deployment**: Focuses on individual subsystems.
2. **System-Level Deployment**: Validates the overall functionality of the telescope.



### Mid Telescope Deployment Structure
#### Pairwise Deployments
- **tmc_csp**
- **tmc_sdp**
- **tmc_dish**

#### System-Level Deployment
- **MARK**: `system_level_tests`

---

## Deployment Commands

### Pairwise Deployment
To run pairwise deployments for the Mid Telescope, use the following command:

```bash
make k8s-install-chart {Subsystem}_SIMULATION_ENABLED=false
```
Replace `{subsystem}` with one of the following:
- `DISH`
- `SDP`
- `CSP`

For example, to deploy the **tmc_dish** subsystem:

```bash
make k8s-install-chart DISH_SIMULATION_ENABLED=false
```

### System-Level Deployment
To deploy system-level charts for the Mid Telescope:

```bash
make k8s-install-chart DISH_SIMULATION_ENABLED=false SDP_SIMULATION_ENABLED=false CSP_SIMULATION_ENABLED=false
```

---

## Flowchart

### Deployment Structure

```plaintext
SKA Telescope
|
|-- Low Telescope
|   |-- Pairwise Testing
|   |   |-- tmc_csp
|   |   |-- tmc_sdp
|   |   |-- tmc_mccs
|   |
|   |-- System-Level Testing
|       |-- system_level_tests
|
|-- Mid Telescope
    |-- Pairwise Deployment
    |   |-- tmc_csp
    |   |-- tmc_sdp
    |   |-- tmc_dish
    |
    |-- System-Level Deployment
        |-- system_level_tests
```


## Contributing
We welcome contributions! Please feel free to open issues or submit merge requests for improvements.

For further assistance, refer to the [ska-mid-integration](https://gitlab.com/ska-telescope/ska-mid-integration) and [ska-low-integration](https://gitlab.com/ska-telescope/ska-low-integration) repositories.

---
