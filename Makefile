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
DISH_SIMULATION_ENABLED ?= true
CI_PROJECT_DIR ?= .

MINIKUBE ?= false ## Minikube or not
EXPOSE_All_DS ?= false ## Expose All Tango Services to the external network (enable Loadbalancer service)
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
TANGO_HOST_NAME ?= tango-databaseds
PORT ?= 10000
CSP_MASTER ?= tango://$(TANGO_HOST_NAME).$(KUBE_NAMESPACE).svc.$(CLUSTER_DOMAIN):$(PORT)/mid-csp/control/0
CSP_SUBARRAY_PREFIX ?= tango://$(TANGO_HOST_NAME).$(KUBE_NAMESPACE).svc.$(CLUSTER_DOMAIN):$(PORT)/mid-csp/subarray
SDP_MASTER ?= tango://$(TANGO_HOST_NAME).$(KUBE_NAMESPACE).svc.$(CLUSTER_DOMAIN):$(PORT)/mid-sdp/control/0
SDP_SUBARRAY_PREFIX ?= tango://$(TANGO_HOST_NAME).$(KUBE_NAMESPACE).svc.$(CLUSTER_DOMAIN):$(PORT)/mid-sdp/subarray
HELM_CHARTS_TO_PUBLISH = $(HELM_CHART)
HELM_CHARTS ?= $(HELM_CHARTS_TO_PUBLISH)
K8S_EXTRA_PARAMS ?= 

#dish variables 
DISH_INDICES ?= "001 036 063 100"
DISH_NAMESPACES ?= "integration-ska-mid-tmc-dish01 integration-ska-mid-tmc-dish36 integration-ska-mid-tmc-dish63 integration-ska-mid-tmc-dish100"
DISH_TANGO_HOST ?=  $(TANGO_HOST_NAME)
DISH_NAMESPACE_1 ?= ${KUBE_NAMESPACE}
DISH_NAMESPACE_2 ?= ${KUBE_NAMESPACE}
DISH_NAMESPACE_3 ?= ${KUBE_NAMESPACE}
DISH_NAMESPACE_4 ?= ${KUBE_NAMESPACE}
DISH_NAME_1 ?= tango://$(DISH_TANGO_HOST).$(DISH_NAMESPACE_1).svc.$(CLUSTER_DOMAIN):$(PORT)/mid-dish/dish-manager/SKA001
DISH_NAME_36 ?= tango://$(DISH_TANGO_HOST).$(DISH_NAMESPACE_2).svc.$(CLUSTER_DOMAIN):$(PORT)/mid-dish/dish-manager/SKA036
DISH_NAME_63 ?= tango://$(DISH_TANGO_HOST).$(DISH_NAMESPACE_3).svc.$(CLUSTER_DOMAIN):$(PORT)/mid-dish/dish-manager/SKA063
DISH_NAME_100 ?= tango://$(DISH_TANGO_HOST).$(DISH_NAMESPACE_4).svc.$(CLUSTER_DOMAIN):$(PORT)/mid-dish/dish-manager/SKA100
#tango://$(DISH_TANGO_HOST).$(DISH_NAMESPACE_4).svc.$(CLUSTER_DOMAIN):$(PORT)/mid-dish/dish-manager/SKA100
SDP_DEPLOY ?= true

ifeq ($(SDP_SIMULATION_ENABLED),false)
K8S_EXTRA_PARAMS=	-f charts/ska-mid-integration/tmc_pairwise/tmc_sdp_values.yaml \
	--set tmc-mid.deviceServers.mocks.sdp=$(SDP_SIMULATION_ENABLED)\
	--set global.sdp_master="$(SDP_MASTER)"\
	--set global.sdp_subarray_prefix="$(SDP_SUBARRAY_PREFIX)"\
	--set ska-sdp.enabled=true\
	--set ska-sdp.lmc.loadBalancer=true\
	--set global.operator=true \
	--set tmc-mid.subarray_count=1\
	--set ska-sdp.lmc.nsubarray=1
endif


ifeq ($(CSP_SIMULATION_ENABLED),false)
K8S_EXTRA_PARAMS =	-f charts/ska-mid-integration/tmc_pairwise/tmc_csp_values.yaml
endif

DISH_NAMESPACES = ${DISH_NAMESPACE_1} ${DISH_NAMESPACE_2} ${DISH_NAMESPACE_3} ${DISH_NAMESPACE_4}
# Target to deploy dishes
deploy-dishes:
	@echo "Deploying dishes to Kubernetes namespaces..."
	IFS=' ' read -r -a indices <<< "$(DISH_INDICES)"; \
	IFS=' ' read -r -a namespaces <<< "$(DISH_NAMESPACES)"; \
	for index in "$${!indices[@]}"; do \
		DISH_INDEX=$${indices[$$index]}; \
		KUBE_NAMESPACE=$${namespaces[$$index]}; \
		make k8s-install-chart \
			KUBE_NAMESPACE=$$KUBE_NAMESPACE \
			K8S_CHART_PARAMS="-f charts/ska-mid-integration/tmc_pairwise/dish-lmc-values.yaml \
				--set global.dishes={$${DISH_INDEX}} \
				--set global.cluster_domain=$(CLUSTER_DOMAIN)"; \
		make k8s-wait \
			KUBE_NAMESPACE=$$KUBE_NAMESPACE; \
	done


stop-dishes:
	@echo "Stopping dishes in Kubernetes namespaces..."
	echo "DISH_INDICES: $(DISH_INDICES)"
	echo "DISH_NAMESPACES: $(DISH_NAMESPACES)"
	IFS=' ' read -r -a indices <<< "$(DISH_INDICES)"; \
	IFS=' ' read -r -a namespaces <<< "$(DISH_NAMESPACES)"; \
	for index in "$${!indices[@]}"; do \
		DISH_INDEX=$${indices[$$index]}; \
		DISH_NAMESPACE=$${namespaces[$$index]}; \
		echo "Namespace: $$DISH_NAMESPACE"; \
		kubectl -n $$DISH_NAMESPACE delete pods,svc,daemonsets,deployments,replicasets,statefulsets,cronjobs,jobs,ingresses,configmaps --all; \
		make k8s-delete-namespace KUBE_NAMESPACE=$$DISH_NAMESPACE;\
		echo "Uninstalling dish $$DISH_INDEX in namespace $$DISH_NAMESPACE"; \
		make k8s-uninstall-chart \
			KUBE_NAMESPACE=$$DISH_NAMESPACE; \
	done



ifeq ($(DISH_SIMULATION_ENABLED),false)
K8S_EXTRA_PARAMS =	-f charts/ska-mid-integration/tmc_pairwise/tmc_dish_values.yaml
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
	--set global.namespace_dish.dish_names[0]="$(DISH_NAME_1)"\
	--set global.namespace_dish.dish_names[1]="$(DISH_NAME_36)"\
	--set global.namespace_dish.dish_names[2]="$(DISH_NAME_63)"\
	--set global.namespace_dish.dish_names[3]="$(DISH_NAME_100)"\
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


# to create SDP namespace
k8s-pre-install-chart:
ifeq ($(SDP_DEPLOY),true)
	@echo "k8s-pre-install-chart: creating the SDP namespace $(KUBE_NAMESPACE_SDP)"
	@make k8s-namespace KUBE_NAMESPACE=$(KUBE_NAMESPACE_SDP)
endif

# to create SDP namespace
k8s-pre-install-chart-car:
ifeq ($(SDP_DEPLOY),true)
	@echo "k8s-pre-install-chart-car: creating the SDP namespace $(KUBE_NAMESPACE_SDP)"
	@make k8s-namespace KUBE_NAMESPACE=$(KUBE_NAMESPACE_SDP)
endif
# to delete SDP namespace
k8s-post-uninstall-chart:
ifeq ($(SDP_DEPLOY),true)
	@echo "k8s-post-uninstall-chart: deleting the SDP namespace $(KUBE_NAMESPACE_SDP)"
	@make k8s-delete-namespace KUBE_NAMESPACE=$(KUBE_NAMESPACE_SDP)
endif

