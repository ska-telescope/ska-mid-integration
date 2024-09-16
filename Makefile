# CAR_OCI_REGISTRY_USER  and PROJECT are combined to define the Docker
# tag for this project. The definition below inherits the standard
# value for CAR_OCI_REGISTRY_USER  (=artefact.skao.int) and overwrites
# PROJECT to give a final Docker tag of artefact.skao.int/ska-tmc-cdm
#
CAR_OCI_REGISTRY_HOST ?= artefact.skao.int
CAR_OCI_REGISTRY_USERNAME ?= ska-telescope
PROJECT_NAME = ska-mid-integration

KUBE_APP ?= ska-mid-integration
KUBE_NAMESPACE ?= ska-mid-integration
KUBE_NAMESPACE_SDP ?= $(KUBE_NAMESPACE)-sdp
HELM_CHART ?= ska-mid-integration
UMBRELLA_CHART_PATH ?= charts/$(HELM_CHART)/
RELEASE_NAME = $(HELM_CHART)
SDP_SIMULATION_ENABLED ?= true
CSP_SIMULATION_ENABLED ?= true
CI_PROJECT_DIR ?= .

MINIKUBE ?= true ## Minikube or not
EXPOSE_All_DS ?= true ## Expose All Tango Services to the external network (enable Loadbalancer service)
SKA_TANGO_OPERATOR ?= true
ODA_URI ?= http://ska-db-oda-rest-$(HELM_RELEASE).$(KUBE_NAMESPACE).svc.$(CLUSTER_DOMAIN):5000/$(KUBE_NAMESPACE)/api/v1

NOTEBOOK_IGNORE_FILES = not notebook.ipynb

OCI_IMAGE_BUILD_CONTEXT = $(PWD)

# disable convention and refactoring lint warnings
PYTHON_SWITCHES_FOR_PYLINT += --disable=C,R,W0612,E0401,W0611,W0105

# resolve various conflicts with Black formatting
PYTHON_SWITCHES_FOR_FLAKE8 += --extend-ignore=E501,W291,W503,F401,E402,F541,F704,F841

# include OCI Images support
include .make/oci.mk

# include k8s support
include .make/k8s.mk

# include Helm Chart support
include .make/helm.mk

# Include Python support
include .make/python.mk

# include raw support
include .make/raw.mk

# include core make support
include .make/base.mk

# include your own private variables for custom deployment configuration
-include PrivateRules.mak

# Chart for testing
K8S_CHART = $(HELM_CHART)
K8S_CHARTS = $(K8S_CHART)

CI_JOB_ID ?= local##pipeline job id
TANGO_HOST ?= tango-databaseds:10000## TANGO_HOST connection to the Tango DS
TANGO_SERVER_PORT ?= 45450## TANGO_SERVER_PORT - fixed listening port for local server
CLUSTER_DOMAIN ?= cluster.local## Domain used for naming Tango Device Servers
K8S_TEST_RUNNER = test-runner-$(CI_JOB_ID)##name of the pod running the k8s-test
TARANTA_AUTH_DASHBOARD_ENABLE ?= false
# Single image in root of project
OCI_IMAGES = ska-mid-integration

ITANGO_ENABLED ?= true

HELM_CHARTS_TO_PUBLISH = $(HELM_CHART)
HELM_CHARTS ?= $(HELM_CHARTS_TO_PUBLISH)
K8S_EXTRA_PARAMS ?= 


HELM_CHARTS_TO_PUBLISH = $(HELM_CHART)
HELM_CHARTS ?= $(HELM_CHARTS_TO_PUBLISH)
K8S_EXTRA_PARAMS ?= 


ifeq ($(SDP_SIMULATION_ENABLED),false)
K8S_EXTRA_PARAMS=	-f charts/ska-mid-integration/tmc_pairwise/tmc_csp_values.yaml \
	--set tmc-mid.deviceServers.mocks.sdp=$(SDP_SIMULATION_ENABLED)\
	--set global.sdp_master="$(SDP_MASTER)"\
	--set global.sdp_subarray_prefix="$(SDP_SUBARRAY_PREFIX)"\
	--set ska-sdp.proccontrol.replicas=$(SDP_PROCCONTROL_REPLICAS)\
	--set ska-sdp.enabled=true\
	--set ska-sdp.lmc.loadBalancer=true\
	--set tmc-mid.subarray_count=1\
	--set ska-sdp.lmc.nsubarray=1
endif


ifeq ($(CSP_SIMULATION_ENABLED),false)
K8S_EXTRA_PARAMS =	-f charts/ska-mid-integration/tmc_pairwise/tmc_csp_values.yaml \
	--set global.csp_master=$(CSP_MASTER)\
	--set global.csp_subarray_prefix=$(CSP_SUBARRAY_PREFIX)
endif


K8S_CHART_PARAMS = --set global.minikube=$(MINIKUBE) \
	--set global.exposeAllDS=$(EXPOSE_All_DS) \
	--set global.tango_host=$(TANGO_HOST) \
	--set global.cluster_domain=$(CLUSTER_DOMAIN) \
	--set global.device_server_port=$(TANGO_SERVER_PORT) \
	--set global.operator=$(SKA_TANGO_OPERATOR) \
	--set global.sdp.processingNamespace=$(KUBE_NAMESPACE_SDP) \
	--set ska-tango-base.itango.enabled=$(ITANGO_ENABLED) \
	--set ska-sdp.kafka.zookeeper.clusterDomain=$(CLUSTER_DOMAIN) \
	--set ska-sdp.kafka.clusterDomain=$(CLUSTER_DOMAIN) \
	--set ska-sdp.ska-sdp-qa.redis.clusterDomain=$(CLUSTER_DOMAIN) \
	--set ska-oso-oet.rest.ingress.enabled=$(OET_INGRESS_ENABLED) \
	--set ska-oso-oet.rest.oda.url=$(ODA_URI) \
	--set ska-db-oda.rest.backend.type=filesystem \
	--set ska-db-oda.pgadmin4.enabled=false \
	--set ska-db-oda.postgresql.enabled=false \
	$(K8S_EXTRA_PARAMS)

# ifeq ($(strip $(MINIKUBE)),true)
# ifeq ($(strip $(TARANTA_AUTH_DASHBOARD_ENABLE)),true)
# K8S_CHART_PARAMS += \
# 	--set ska-taranta.enabled=true \
# 	--set ska-taranta.tangogql.replicas=1 \
# 	--set global.taranta_auth_enabled=true \
# 	--set global.taranta_dashboard_enabled=true
# else
# K8S_CHART_PARAMS += --set ska-taranta.enabled=false
# endif
# else
# K8S_CHART_PARAMS += --set ska-taranta.enabled=true
# ifeq ($(strip $(TARANTA_AUTH_DASHBOARD_ENABLE)),true)
# K8S_CHART_PARAMS += \
# 	--set global.taranta_auth_enabled=true \
# 	--set global.taranta_dashboard_enabled=true
# endif
# endif


k8s-pre-install-chart:
	@echo "k8s-pre-install-chart: creating the CSP namespace $(KUBE_NAMESPACE_SDP)"
	@make k8s-namespace KUBE_NAMESPACE=$(KUBE_NAMESPACE_SDP)

k8s-pre-install-chart-car:
	@echo "k8s-pre-install-chart-car: creating the SDP namespace $(KUBE_NAMESPACE_SDP)"
	@make k8s-namespace KUBE_NAMESPACE=$(KUBE_NAMESPACE_SDP)

k8s-pre-uninstall-chart:
	@echo "k8s-post-uninstall-chart: deleting the CSP namespace $(KUBE_NAMESPACE_SDP)"
	@if [ "$(KEEP_NAMESPACE)" != "true" ]; then make k8s-delete-namespace KUBE_NAMESPACE=$(KUBE_NAMESPACE_SDP); fi