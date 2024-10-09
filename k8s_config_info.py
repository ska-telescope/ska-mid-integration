from http.client import HTTPConnection
import json
from kubernetes import client, config, stream
import requests
import time
from kubernetes.stream.ws_client import PortForward

# Step 1: Load Kubernetes configuration
print("Step 1: Loading Kubernetes configuration")
config.load_kube_config()  # Use config.load_incluster_config() if running inside the cluster

# Step 2: Create a CoreV1Api instance to interact with Kubernetes
print("Step 2: Creating CoreV1Api instance")
v1 = client.CoreV1Api()

KUBE_NAMESPACE = "ska-tmc-integration"
SERVICE_NAME = "ska-k8s-config-exporter-service"
LOCAL_PORT = 8080
REMOTE_PORT = 8080  # Since service is using port 8080 as well

# Step 3: Get the service port programmatically
print(f"Step 3: Fetching service port for service '{SERVICE_NAME}' in namespace '{KUBE_NAMESPACE}'")
service = v1.read_namespaced_service(SERVICE_NAME, KUBE_NAMESPACE)
REMOTE_PORT = service.spec.ports[0].port  # Fetching the service port
print(f"Service is using remote port: {REMOTE_PORT}")

# Step 4: Identify the pod associated with the service
print(f"Step 4: Finding pods associated with the service '{SERVICE_NAME}'")
pods = v1.list_namespaced_pod(namespace=KUBE_NAMESPACE, label_selector="app=ska-k8s-config-exporter")
if len(pods.items) == 0:
    raise Exception(f"No pods found for the service: {SERVICE_NAME}")

# Picking the first pod from the service
pod_name = pods.items[0].metadata.name
print(f"Found pod '{pod_name}' for service '{SERVICE_NAME}'")

# Step 5: Port-forward the service using kubernetes.stream API
print(f"Step 5: Forwarding local port {LOCAL_PORT} to remote port {REMOTE_PORT} on pod '{pod_name}'")

class ForwardedKubernetesHTTPConnection(HTTPConnection):
    """Curtesy of: https://stackoverflow.com/a/70025115"""

    def __init__(self, forwarding: PortForward, port: int):
        super().__init__("127.0.0.1", port)
        self.sock = forwarding.socket(port)

    def connect(self) -> None:
        pass

    def close(self) -> None:
        pass

port_forward = stream.portforward(
    v1.connect_get_namespaced_pod_portforward,
    pod_name,
    KUBE_NAMESPACE,
    ports=str(LOCAL_PORT)
)

conn = ForwardedKubernetesHTTPConnection(port_forward, LOCAL_PORT)

# Step 6: Make a request to the forwarded service
print(f"Step 6: Making necessary requests to http://localhost:{LOCAL_PORT}/")
def request(conn: HTTPConnection, method: str, path: str) -> None:
    try:
        conn.request(method, path)
        response = conn.getresponse() 
        # print(f"Response: {response.text}")
        print(f"Status: {response.status}")
        print(f"Headers: {response.headers}")
        # pretty print the JSON response
        # try:
        #     print(json.dumps(json.loads(response.read()), indent=2))
        # except json.JSONDecodeError:
        #     print(response.read())
        print(response.read())
    except requests.RequestException as e:
        print(f"Error making the request: {e}")

for target_path in ["/pods", "/helm", "/dsconfig", "/tango_devices"]:
    print("\n" + "-" * 50)
    print(f"Requesting: {target_path}")
    request(conn, "GET", target_path)

print("Step 7: Port-forwarding session complete")
