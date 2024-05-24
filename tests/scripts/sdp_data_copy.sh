#!/bin/bash

#Export variables 
export SDP_NAMESPACE="${KUBE_NAMESPACE_SDP:-"ska-tmc-integration-sdp"}"
export POD_CONTAINER="data-prep"
export SDP_DATA_COPY_PATH="/mnt/data/product/eb-test-20210630-00001/ska-sdp/pb-test-20211111-00001/" 

#Install k8s python package
pip list | grep -i kubernetes
if [ "$?" -ne "0" ]
then
    pip install kubernetes
fi

#Create pod
if [ "$1" == "create_pod" ]
then
python << EOL
import os
from kubernetes import client, config
config.load_kube_config()

POD_CONTAINER = "data-prep"
POD_COMMAND = [
    "/bin/bash",
    "-c",
    "apt-get update && apt-get install -y git git-lfs;"
    "git clone -n --depth=1 --filter=tree:0 --branch=0.20.0 "
    "https://gitlab.com/ska-telescope/sdp/ska-sdp-integration.git; cd ska-sdp-integration;"
    "git checkout; git lfs fetch; cd tests/resources/data/pointing-data;"
    "mkdir -p {path}; cp -rv *.ms {path}; ls -l /mnt/data/product/eb-test-20210630-00001/ska-sdp/pb-test-20211111-00001/*.ms;echo data_copied_successfully"
    " trap : TERM; sleep infinity & wait",
]

DATA_POD_DEF = {
    "apiVersion": "v1",
    "kind": "Pod",
    "metadata": {"name": "receive-data"},
    "spec": {
        "securityContext": {"runAsUser": 0},  # run as root so that we can download data
        "containers": [
            {
                "image": "artefact.skao.int/ska-sdp-realtime-receive-modules:5.0.0",  # noqa: E501
                "name": POD_CONTAINER,
                "command": POD_COMMAND,
                "volumeMounts": [{"mountPath": "/mnt/data", "name": "data"}],
            }
        ],
        "volumes": [{"name": "data", "persistentVolumeClaim": {"claimName": "test-pvc"}}],
    },
}
core_api = client.CoreV1Api()
pod_spec = DATA_POD_DEF.copy()

# Update the name of the pod and the data PVC
pod_spec["metadata"]["name"] = "sdp-data-copy"
pod_spec["spec"]["volumes"][0]["persistentVolumeClaim"]["claimName"] = "test-pvc"
pod_spec["spec"]["containers"][0]["command"][2] = (
pod_spec["spec"]["containers"][0]["command"][2].format(path=os.environ.get("SDP_DATA_COPY_PATH"))
)
# Check Pod does not already exist
k8s_pods = core_api.list_namespaced_pod(os.environ.get("SDP_NAMESPACE"))
for item in k8s_pods.items:
    assert (
        item.metadata.name != pod_spec["metadata"]["name"]
    ), f"Pod {item.metadata.name} already exists"

core_api.create_namespaced_pod(os.environ.get("SDP_NAMESPACE"), pod_spec)
    
EOL
echo "Creating SDP data copy pod in $SDP_NAMESPACE"
kubectl get all,pvc -n $SDP_NAMESPACE
kubectl describe pod/sdp-data-copy -n $SDP_NAMESPACE
echo "*****************************************************************"
kubectl describe pvc test-pvc -n $SDP_NAMESPACE
fi


#Delete pod
if [ "$1" == "delete_pod" ]
then
echo "Deleting SDP data copy pod in $SDP_NAMESPACE"
python << EOL
import os
from kubernetes import client, config
from kubernetes.client.rest import ApiException
config.load_kube_config()
core_api = client.CoreV1Api()
try:
    core_api.delete_namespaced_pod(
        "sdp-data-copy",os.environ.get("SDP_NAMESPACE"), 
        async_req=False, grace_period_seconds=0
    )
except ApiException as e:
    if e.status == 404:
        print(f"Pod sdp-data-copy does not exist in namespace {os.environ.get('SDP_NAMESPACE')}.")
    else:
        print(f"An error occurred: {e}")
EOL
kubectl get all,pvc -n $SDP_NAMESPACE
fi