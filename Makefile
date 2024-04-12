# Project makefile for a ska-tmc-integration project. You should normally only need to modify
# CAR_OCI_REGISTRY_USER and PROJECT below.
ALARM_HANDLER_FQDN= "alarm/handler/01"
CAR_OCI_REGISTRY_HOST:=artefact.skao.int
PROJECT = ska-tmc-integration
TANGO_HOST ?= tango-databaseds:10000 ## TANGO_HOST connection to the Tango DS
TELESCOPE ?= SKA-mid
DISH_NAMESPACE_1 ?= dish-lmc-1
DISH_NAMESPACE_2 ?= dish-lmc-2
DISH_NAMESPACE_3 ?= dish-lmc-3
DISH_NAMESPACE_4 ?= dish-lmc-4
KUBE_NAMESPACE ?= ska-tmc-integration
KUBE_NAMESPACE_SDP ?= ska-tmc-integration-sdp

PYTHON_LINT_TARGET ?= tests/

DEPLOYMENT_TYPE = $(shell echo $(TELESCOPE) | cut -d '-' -f2)
MARK ?= $(shell echo $(TELESCOPE) | sed "s/-/_/g") ## What -m opt to pass to pytest
# run one test with FILE=acceptance/test_subarray_node.py::test_check_internal_model_according_to_the_tango_ecosystem_deployed
FILE ?= tests## A specific test file to pass to pytest
ADD_ARGS ?= ## Additional args to pass to pytest
FILE_NAME?= alarm_rules.txt
EXIT_AT_FAIL = true ## Flag for determining exit at failure. Set 'true' to exit at first failure.

ifeq ($(EXIT_AT_FAIL),true)
ADD_ARGS += -x
endif

# KUBE_NAMESPACE defines the Kubernetes Namespace that will be deployed to
# using Helm.  If this does not already exist it will be created
ifneq ($(CI_JOB_ID),)
KUBE_NAMESPACE ?= ci-$(CI_PROJECT_NAME)-$(CI_COMMIT_SHORT_SHA)
endif
# HELM_RELEASE is the release that all Kubernetes resources will be labelled
# with
HELM_RELEASE ?= test

# UMBRELLA_CHART_PATH Path of the umbrella chart to work with
HELM_CHART=ska-tmc-testing-$(DEPLOYMENT_TYPE)
UMBRELLA_CHART_PATH ?= charts/$(HELM_CHART)/
K8S_CHARTS ?= ska-tmc-$(DEPLOYMENT_TYPE) ska-tmc-testing-$(DEPLOYMENT_TYPE)## list of charts
K8S_CHART ?= $(HELM_CHART)

DISH_TANGO_HOST ?= tango-databaseds
COUNT ?= 1
CLUSTER_DOMAIN ?= cluster.local
PORT ?= 10000
SUBARRAY_COUNT ?= 2
DISH_NAME_1 ?= tango://$(DISH_TANGO_HOST).$(DISH_NAMESPACE_1).svc.$(CLUSTER_DOMAIN):$(PORT)/ska001/elt/master
DISH_NAME_36 ?= tango://$(DISH_TANGO_HOST).$(DISH_NAMESPACE_2).svc.$(CLUSTER_DOMAIN):$(PORT)/ska036/elt/master
DISH_NAME_63 ?= tango://$(DISH_TANGO_HOST).$(DISH_NAMESPACE_3).svc.$(CLUSTER_DOMAIN):$(PORT)/ska063/elt/master
DISH_NAME_100 ?= tango://$(DISH_TANGO_HOST).$(DISH_NAMESPACE_4).svc.$(CLUSTER_DOMAIN):$(PORT)/ska100/elt/master
CSP_MASTER ?= tango://$(TANGO_HOST).$(KUBE_NAMESPACE).svc.$(CLUSTER_DOMAIN):$(PORT)/mid-csp/control/0
CSP_SUBARRAY_PREFIX ?= tango://$(TANGO_HOST).$(KUBE_NAMESPACE).svc.$(CLUSTER_DOMAIN):$(PORT)/mid-csp/subarray
SDP_MASTER ?= tango://$(TANGO_HOST).$(KUBE_NAMESPACE).svc.$(CLUSTER_DOMAIN):$(PORT)/mid-sdp/control/0
SDP_SUBARRAY_PREFIX ?= tango://$(TANGO_HOST).$(KUBE_NAMESPACE).svc.$(CLUSTER_DOMAIN):$(PORT)/mid-sdp/subarray

CI_REGISTRY ?= gitlab.com

K8S_TEST_IMAGE_TO_TEST ?= artefact.skao.int/ska-tango-images-tango-itango:9.3.12## docker image that will be run for testing purpose

TARANTA_ENABLED ?= false

CI_PROJECT_DIR ?= .
XRAY_TEST_RESULT_FILE = "build/cucumber.json"
XAUTHORITY ?= $(HOME)/.Xauthority
THIS_HOST := $(shell ip a 2> /dev/null | sed -En 's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\2/p' | head -n1)
DISPLAY ?= $(THIS_HOST):0
JIVE ?= false# Enable jive
TARANTA ?= false
MINIKUBE ?= false ## Minikube or not
FAKE_DEVICES ?= false ## Install fake devices or not
TANGO_HOST ?= tango-databaseds:10000## TANGO_HOST connection to the Tango DS

ITANGO_DOCKER_IMAGE = $(CAR_OCI_REGISTRY_HOST)/ska-tango-images-tango-itango:9.3.10

# Test runner - run to completion job in K8s
# name of the pod running the k8s_tests
K8S_TEST_RUNNER = test-runner-$(HELM_RELEASE)

CI_PROJECT_PATH_SLUG ?= ska-tmc-integration
CI_ENVIRONMENT_SLUG ?= ska-tmc-integration
CSP_SIMULATION_ENABLED ?= true
SDP_SIMULATION_ENABLED ?= true
DISH_SIMULATION_ENABLED ?= true

ifeq ($(MAKECMDGOALS),k8s-test)
ADD_ARGS +=  --true-context -x
MARK ?= $(shell echo $(TELESCOPE) | sed "s/-/_/g")
endif

# EXIT_AT_FAIL option isn't functioning correctly, so the option -x is added
# at the end. Will be debugged and fixed as a part of improvement.
PYTHON_VARS_AFTER_PYTEST ?= -m '$(MARK)' $(ADD_ARGS) $(FILE) -x
CUSTOM_VALUES1 ?=
CUSTOM_VALUES2 ?=
ifeq ($(CSP_SIMULATION_ENABLED),false)
CUSTOM_VALUES1 =	--set tmc-mid.deviceServers.mocks.csp=$(CSP_SIMULATION_ENABLED)\
	--set ska-csp-lmc-mid.enabled=true
endif

ifeq ($(SDP_SIMULATION_ENABLED),false)
CUSTOM_VALUES2=	--set tmc-mid.deviceServers.mocks.sdp=$(SDP_SIMULATION_ENABLED)\
	--set global.sdp_master="$(SDP_MASTER)"\
	--set global.sdp_subarray_prefix="$(SDP_SUBARRAY_PREFIX)"\
	--set global.sdp.processingNamespace=$(KUBE_NAMESPACE_SDP)\
	--set ska-sdp.enabled=true
endif

K8S_CHART_PARAMS = --set global.minikube=$(MINIKUBE) \
	--set global.tango_host=$(TANGO_HOST) \
	--set ska-tango-base.display=$(DISPLAY) \
	--set ska-tango-base.xauthority=$(XAUTHORITY) \
	--set ska-tango-base.jive.enabled=$(JIVE) \
	--set global.exposeAllDS=false \
	--set global.cluster_domain=$(CLUSTER_DOMAIN) \
	--set global.operator=false \
	--set ska-taranta.enabled=$(TARANTA_ENABLED)\
	--set global.namespace_dish.dish_names[0]="$(DISH_NAME_1)"\
	--set global.namespace_dish.dish_names[1]="$(DISH_NAME_36)"\
	--set global.namespace_dish.dish_names[2]="$(DISH_NAME_63)"\
	--set global.namespace_dish.dish_names[3]="$(DISH_NAME_100)"\
	--set tmc-mid.deviceServers.mocks.dish=$(DISH_SIMULATION_ENABLED)\
	--set tmc-mid.subarray_count=$(SUBARRAY_COUNT)\
	$(CUSTOM_VALUES1)\
	$(CUSTOM_VALUES2)

PYTHON_VARS_BEFORE_PYTEST ?= PYTHONPATH=.:./src \
							 TANGO_HOST=$(TANGO_HOST) \
							 TELESCOPE=$(TELESCOPE) \
							 CLUSTER_DOMAIN=$(CLUSTER_DOMAIN) \
							 CSP_SIMULATION_ENABLED=$(CSP_SIMULATION_ENABLED) \
							 SDP_SIMULATION_ENABLED=$(SDP_SIMULATION_ENABLED) \
							 DISH_SIMULATION_ENABLED=$(DISH_SIMULATION_ENABLED) \
							 DISH_NAMESPACE_1=$(DISH_NAMESPACE_1) \
							 DISH_NAMESPACE_2=$(DISH_NAMESPACE_2) \
							 DISH_NAMESPACE_3=$(DISH_NAMESPACE_3) \
							 DISH_NAMESPACE_4=$(DISH_NAMESPACE_4) \
							 DISH_NAME_1=$(DISH_NAME_1) \
							 DISH_NAME_36=$(DISH_NAME_36) \
							 DISH_NAME_63=$(DISH_NAME_63) \
							 DISH_NAME_100=$(DISH_NAME_100) \
							 KUBE_NAMESPACE=$(KUBE_NAMESPACE) \
							 KUBE_NAMESPACE_SDP=$(KUBE_NAMESPACE_SDP)

K8S_TEST_TEST_COMMAND ?= $(PYTHON_VARS_BEFORE_PYTEST) $(PYTHON_RUNNER) \
						pytest \
						$(PYTHON_VARS_AFTER_PYTEST) ./tests \
						| tee pytest.stdout # k8s-test test command to run in container

-include .make/base.mk
-include .make/k8s.mk
-include .make/helm.mk
-include .make/python.mk
-include .make/oci.mk
-include .make/xray.mk
-include PrivateRules.mak
-include resources/alarmhandler.mk

# to create SDP namespace
k8s-pre-install-chart:
ifeq ($(SDP_SIMULATION_ENABLED),false)
	@echo "k8s-pre-install-chart: creating the SDP namespace $(KUBE_NAMESPACE_SDP)"
	@make k8s-namespace KUBE_NAMESPACE=$(KUBE_NAMESPACE_SDP)
endif

# to create SDP namespace
k8s-pre-install-chart-car:
ifeq ($(SDP_SIMULATION_ENABLED),false)
	@echo "k8s-pre-install-chart-car: creating the SDP namespace $(KUBE_NAMESPACE_SDP)"
	@make k8s-namespace KUBE_NAMESPACE=$(KUBE_NAMESPACE_SDP)
endif

# to delete SDP namespace
k8s-post-uninstall-chart:
ifeq ($(SDP_SIMULATION_ENABLED),false)
	@echo "k8s-post-uninstall-chart: deleting the SDP namespace $(KUBE_NAMESPACE_SDP)"
	@make k8s-delete-namespace KUBE_NAMESPACE=$(KUBE_NAMESPACE_SDP)
endif

taranta-link:
	@echo "#            https://k8s.stfc.skao.int/$(KUBE_NAMESPACE)/taranta/dashboard"

alarm-handler-configurator-link:
	@echo "#            https://k8s.stfc.skao.int/$(KUBE_NAMESPACE)/alarm-handler/"


cred:
	make k8s-namespace
	curl -s https://gitlab.com/ska-telescope/templates-repository/-/raw/master/scripts/namespace_auth.sh | bash -s $(SERVICE_ACCOUNT) $(KUBE_NAMESPACE) || true


test-requirements:
	@poetry export --without-hashes --dev --format requirements.txt --output tests/requirements.txt

k8s-pre-test: test-requirements