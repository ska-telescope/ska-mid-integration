# SKA Mid Deployment Repository

This repository contains deployment tools and related infrastructure for the SKA Observatory's (SKAO) Assembly, Integration, and Verification (AIV) team working on the SKA Mid telescope. It includes deployment infrastructure for the Mid System Under Test (SUT) and the Test Equipment used in the Mid Integration Test Facility (ITF). Additionally, it provides pipelines to trigger verification and integration events for automated deployments.

## Documentation

Click below to access the TMC documentation.

[![Documentation Status](https://readthedocs.org/projects/ska-telescope-ska-mid-integration/badge/?version=latest)](https://developer.skao.int/projects/ska-mid-integration/en/latest/)

## Component Versions

The following table lists the key components of the SKA Mid Deployment system and their respective versions:

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
 * To deploy the dish LMC chart in integration, run the following command:
    ```bash
    make k8s-install-chart
    ```
    All values required for deploying the dish LMC can be provided in the `charts/tmc_pairwise/dish_lmc_values.yml` file.

    Refer to this link for set flag options: https://gitlab.com/ska-telescope/ska-dish-lmc#-set-flag-options
    
    After running the above command, the dish LMC with dish ID 001 is deployed in the provided Kubernetes Namespace (i.e., `KUBE_NAMESPACE`).

    To deploy multiple dishes, provide multiple values to `global.dishes`. 
    Example: `global.dishes={036,001,...}`

 * Uninstall the dish LMC chart:
    ```bash
    make k8s-uninstall-chart
    ```

 * Test dish LMC with TMC as an entry point:
    To test Dish LMC within the TMC integration, you can set a specific flag to control whether you want to use a real device or a mock device. Here's how you can do it:
    ```bash
    --set tmc-mid.deviceServers.mocks.dish=true or false
    ```
    If you set "enabled" to true, Dish LMC will use a mock device for testing, and if you set "enabled" to false, Dish LMC will use a real device for testing.

## Overview
The SKA Telescope system is divided into two telescopes:

1. **Low Telescope**
2. **Mid Telescope**

Each telescope involves two deployment phases:

1. **Pairwise Deployment**: Focuses on individual subsystems.
2. **System-Level Deployment**: Validates the overall functionality of the telescope.

## Component Versions

Below is the list of components and their corresponding versions used in the SKA Mid Deployment project:

| Component                | OCI Name                     | Version       |
|--------------------------|------------------------------|---------------|
| SKA-TMC (Mid)            | ska-tmc-mid                  | 0.13.1        |
| SKA Mid MCCS             | ska-mid-mccs                 | 0.16.2        |
| CSP-LMC (Mid)            | ska-csp-lmc-mid              | 0.24.1-rc.1   |
| SKA Mid CBF              | ska-mid-cbf                  | 1.1.0-rc.2    |
| SKA Mid CBF Proc         | ska-mid-cbf-proc             | 0.15.0        |
| SKA PST                  | ska-pst                      | 0.12.1        |

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
make k8s-test MARK=<pairwise_test_type>
```
Replace `<pairwise_test_type>` with one of the following:
- `tmc_csp`
- `tmc_sdp`
- `tmc_dish`

For example, to deploy the **tmc_sdp** subsystem:

```bash
make k8s-test MARK=tmc_sdp
```

### System-Level Deployment
To deploy system-level charts for the Mid Telescope:

```bash
make k8s-test MARK=system_level_tests
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

### Deployment Commands
```plaintext
make k8s-install-chart MARK=<deployment_type>
```
- Replace `<deployment_type>` with:
  - For Mid Pairwise Deployment: `tmc_csp`, `tmc_sdp`, or `tmc_dish`
  - For System-Level Deployment: `system_level_tests`

---

## Contributing
We welcome contributions! Please feel free to open issues or submit merge requests for improvements.

For further assistance, refer to the [ska-mid-integration](https://gitlab.com/ska-telescope/ska-mid-integration) and [ska-low-integration](https://gitlab.com/ska-telescope/ska-low-integration) repositories.

---
