"""PromQL helper for querying Prometheus metrics (node CPU/mem/disk, pod status)."""

import os
import urllib.request
import urllib.parse
import json

PROMETHEUS_URL = os.environ.get("PROMETHEUS_URL", "http://prometheus-server.monitoring.svc.cluster.local:9090")


def _query(promql):
    """Execute an instant PromQL query and return the result."""
    try:
        url = f"{PROMETHEUS_URL}/api/v1/query?query={urllib.parse.quote(promql)}"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            if data.get("status") == "success":
                return data.get("data", {}).get("result", [])
    except Exception:
        pass
    return []


def node_cpu_usage():
    """CPU usage per K3s node as percentage."""
    results = _query(
        '100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)'
    )
    nodes = {}
    for r in results:
        instance = r["metric"].get("instance", "")
        nodes[instance] = round(float(r["value"][1]), 1)
    return nodes


def node_memory_usage():
    """Memory usage per K3s node as percentage."""
    results = _query(
        '100 * (1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)'
    )
    nodes = {}
    for r in results:
        instance = r["metric"].get("instance", "")
        nodes[instance] = round(float(r["value"][1]), 1)
    return nodes


def node_disk_usage():
    """Root filesystem usage per K3s node as percentage."""
    results = _query(
        '100 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"} * 100)'
    )
    nodes = {}
    for r in results:
        instance = r["metric"].get("instance", "")
        nodes[instance] = round(float(r["value"][1]), 1)
    return nodes


def pod_count_by_namespace():
    """Count of running pods per namespace."""
    results = _query('count by (namespace) (kube_pod_status_phase{phase="Running"})')
    namespaces = {}
    for r in results:
        ns = r["metric"].get("namespace", "")
        namespaces[ns] = int(float(r["value"][1]))
    return namespaces
