from os import environ
from kubernetes import config, client
import htcondor2 as htcondor
from api_models import LiveDashboardStatus
import requests


POD_NAMESPACE = environ.get("DASHBOARD_NAMESPACE", "default")

LABEL_PATTERN = "app={netid}-self-service-ap"

COLLECTOR_PATTERN = "{netid}-self-service-ap.{namespace}.svc.cluster.local:{port}?sock=ap_collector"

DASHBOARD_PATTERN = "{netid}-self-service-ap.{namespace}.svc.cluster.local:{port}"


config.load_incluster_config()
v1 = client.CoreV1Api()

class DashboardStatusCheck():
    """ Util class that queries several APIs (k8s, HTCondor, http) 
    for information about the functionality of an AP dashboard """

    netid: str

    # Populated by reading container ports from k8s API
    htcondor_port: int
    dashboard_port: int

    # Populated by reading pod status from k8s API
    pod_health: str
    pod_health_reason: str


    # Populated by running condor_status against the AP's condor collector
    collector_health: str = "Unknown"
    collector_health_reason: str = ""

    # Populated by sending an HTTP request to the AP's dashboard web server
    dashboard_health: str = "Unknown"
    dashboard_health_reason: str = ""

    def __init__(self, netid: str):
        self.netid = netid


    def populate_k8s_info(self):
        """
        Parse the K8s API for info about the user's pod, including light schema validation.
        """
        pods = v1.list_namespaced_pod(namespace=POD_NAMESPACE, label_selector=LABEL_PATTERN.format(netid=self.netid))
        services = v1.list_namespaced_service(namespace=POD_NAMESPACE, label_selector=LABEL_PATTERN.format(netid=self.netid))

        if len(pods.items) != 1 or len(services.items) != 1:
            self.pod_health = "Poor"
            self.pod_health_reason = f"Expected 1 pod, found {len(pods.items)}"
            return

        pod = pods.items[0]
        status = pod.status.phase
        container_status = pod.status.container_statuses[0]
        if status != 'Running' or container_status.started is False or container_status.ready is False:
            waiting_state = container_status.state.waiting
            self.pod_health = "Poor"
            self.pod_health_reason = f"Container not ready: {waiting_state.reason} - {waiting_state.message}"
            return

        if pod.status.phase != "Running":
            self.pod_health = pod.status.phase
            self.pod_health_reason = f"Pod not running: {pod.status.phase}"
            return

        service = services.items[0]

        ports = service.spec.ports
        self.htcondor_port = next((p.container_port for p in ports if p.name == "htcondor"), None)
        self.dashboard_port = next((p.container_port for p in ports if p.name == "http"), None)

        if not self.htcondor_port or not self.dashboard_port:
            self.pod_health = "Poor"
            self.pod_health_reason = "Container misconfigured: missing expected ports"
            return

        self.pod_health = "Healthy"
        self.pod_health_reason = "Container running"


    def populate_collector_info(self):
        collector_url = COLLECTOR_PATTERN.format(netid=self.netid, namespace=POD_NAMESPACE, port=self.htcondor_port)

        col = htcondor.Collector(collector_url)

        try:
            # Basic sanity check: can we query the collector for Startd ads?
            ads = col.query(htcondor.AdTypes.Startd)
            self.collector_health = "Healthy"
            self.collector_health_reason = f"HTCondor is running. {len(ads)} Execution Points are reporting."
        except Exception as e:
            self.collector_health = "Poor"
            self.collector_health_reason = f"Failed to query HTCondor collector: {str(e)}"

    def populate_dashboard_info(self):
        dashboard_url = DASHBOARD_PATTERN.format(netid=self.netid, namespace=POD_NAMESPACE, port=self.dashboard_port)

        try:
            resp = requests.head(dashboard_url, timeout=5)
            if resp.status_code == 200:
                self.dashboard_health = "Healthy"
                self.dashboard_health_reason = "Dashboard web server is responding."
            else:
                self.dashboard_health = "Poor"
                self.dashboard_health_reason = f"Dashboard web server returned status code {resp.status_code}."
        except Exception as e:
            self.dashboard_health = "Poor"
            self.dashboard_health_reason = f"Failed to connect to dashboard web server: {str(e)}"
            return


    def get_dashboard_status(self):
        self.populate_k8s_info()
        if self.pod_health != "Healthy":
            return

        self.populate_collector_info()
        self.populate_dashboard_info()


def get_live_dashboard_status(netid: str) -> LiveDashboardStatus:
    check = DashboardStatusCheck(netid)
    check.get_dashboard_status()
    return LiveDashboardStatus(
        pod_health=check.pod_health,
        pod_health_reason=check.pod_health_reason,
        collector_health=check.collector_health,
        collector_health_reason=check.collector_health_reason,
        dashboard_health=check.dashboard_health,
        dashboard_health_reason=check.dashboard_health_reason,
    )


