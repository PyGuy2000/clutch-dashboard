"""Infrastructure queries — K8s API, Prometheus, Ollama, GPU exporter."""

import os
import json
import urllib.request

from queries.prometheus import (
    node_cpu_usage,
    node_memory_usage,
    node_disk_usage,
    pod_count_by_namespace,
)
from queries.ollama import running_models, available_models, ollama_health

GPU_EXPORTER_URL = os.environ.get("GPU_EXPORTER_URL", "http://192.168.1.50:9101")

# Kubernetes API — in-cluster access via service account
K8S_API = "https://kubernetes.default.svc"
K8S_TOKEN_PATH = "/var/run/secrets/kubernetes.io/serviceaccount/token"
K8S_CA_PATH = "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"


def _k8s_get(path):
    """Make an authenticated GET to the K8s API server."""
    try:
        with open(K8S_TOKEN_PATH) as f:
            token = f.read().strip()
    except FileNotFoundError:
        return None

    try:
        url = f"{K8S_API}{path}"
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            },
        )
        import ssl
        ctx = ssl.create_default_context(cafile=K8S_CA_PATH)
        with urllib.request.urlopen(req, timeout=5, context=ctx) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


def _http_get_json(url, timeout=5):
    """Simple HTTP GET returning parsed JSON."""
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


def get_k8s_nodes():
    """Get K3s node status and resource info."""
    data = _k8s_get("/api/v1/nodes")
    if not data:
        return []
    nodes = []
    for item in data.get("items", []):
        meta = item.get("metadata", {})
        status = item.get("status", {})
        conditions = {c["type"]: c["status"] for c in status.get("conditions", [])}
        capacity = status.get("capacity", {})
        nodes.append({
            "name": meta.get("name", ""),
            "ip": next(
                (a["address"] for a in status.get("addresses", []) if a["type"] == "InternalIP"),
                "",
            ),
            "ready": conditions.get("Ready") == "True",
            "cpu_capacity": capacity.get("cpu", "0"),
            "memory_capacity_gb": round(
                int(capacity.get("memory", "0Ki").replace("Ki", "")) / 1024 / 1024, 1
            ),
            "os_image": status.get("nodeInfo", {}).get("osImage", ""),
            "kubelet_version": status.get("nodeInfo", {}).get("kubeletVersion", ""),
        })
    return nodes


def get_k8s_pods():
    """Get all pods across all namespaces."""
    data = _k8s_get("/api/v1/pods")
    if not data:
        return []
    pods = []
    for item in data.get("items", []):
        meta = item.get("metadata", {})
        status = item.get("status", {})
        phase = status.get("phase", "Unknown")
        pods.append({
            "name": meta.get("name", ""),
            "namespace": meta.get("namespace", ""),
            "phase": phase,
            "node": item.get("spec", {}).get("nodeName", ""),
            "restarts": sum(
                cs.get("restartCount", 0)
                for cs in status.get("containerStatuses", [])
            ),
            "ready": all(
                cs.get("ready", False)
                for cs in status.get("containerStatuses", [])
            ),
        })
    return pods


def get_k8s_services():
    """Get all services across all namespaces."""
    data = _k8s_get("/api/v1/services")
    if not data:
        return []
    services = []
    for item in data.get("items", []):
        meta = item.get("metadata", {})
        spec = item.get("spec", {})
        ns = meta.get("namespace", "")
        # Skip kube-system internals
        if ns == "kube-system" and meta.get("name") in ("kube-dns", "metrics-server"):
            continue
        services.append({
            "name": meta.get("name", ""),
            "namespace": ns,
            "type": spec.get("type", ""),
            "cluster_ip": spec.get("clusterIP", ""),
            "ports": [
                {"port": p.get("port"), "target": p.get("targetPort")}
                for p in spec.get("ports", [])
            ],
        })
    return services


def get_k8s_namespaces():
    """Get all namespaces."""
    data = _k8s_get("/api/v1/namespaces")
    if not data:
        return []
    return [
        item["metadata"]["name"]
        for item in data.get("items", [])
    ]


def get_gpu_metrics():
    """Get GPU metrics from the custom exporter on AI Workstation."""
    data = _http_get_json(f"{GPU_EXPORTER_URL}/metrics")
    if not data:
        return {"gpus": [], "gpu_count": 0, "online": False}
    data["online"] = True
    return data


def get_node_metrics():
    """Aggregate node metrics from Prometheus."""
    cpu = node_cpu_usage()
    mem = node_memory_usage()
    disk = node_disk_usage()

    # Merge by instance
    all_instances = set(list(cpu.keys()) + list(mem.keys()) + list(disk.keys()))
    nodes = []
    for inst in sorted(all_instances):
        nodes.append({
            "instance": inst,
            "cpu_pct": cpu.get(inst, 0),
            "memory_pct": mem.get(inst, 0),
            "disk_pct": disk.get(inst, 0),
        })
    return nodes


def get_ollama_status():
    """Get Ollama health, running models, and available models."""
    healthy = ollama_health()
    return {
        "online": healthy,
        "running": running_models() if healthy else [],
        "available": available_models() if healthy else [],
    }


def get_infra_topology():
    """Build the full topology data structure for the Cytoscape.js graph."""
    k8s_nodes = get_k8s_nodes()
    pods = get_k8s_pods()
    gpu = get_gpu_metrics()
    ollama = get_ollama_status()
    node_metrics = get_node_metrics()

    # Static infrastructure nodes
    topology = {
        "physical": [
            {"id": "udm-pro", "label": "UDM Pro", "type": "gateway", "ip": "192.168.1.1"},
            {"id": "nuc1", "label": "NUC1", "type": "hypervisor", "ip": "192.168.1.10"},
            {"id": "nuc2", "label": "NUC2", "type": "hypervisor", "ip": "192.168.1.11"},
            {"id": "nuc3", "label": "NUC3", "type": "hypervisor", "ip": "192.168.1.12"},
            {"id": "nas", "label": "Synology NAS", "type": "storage", "ip": "192.168.1.126"},
            {"id": "ai-workstation", "label": "AI Workstation", "type": "gpu", "ip": "192.168.1.50",
             "gpu": gpu, "ollama": ollama},
            {"id": "openclaw-vm", "label": "OpenClaw VM", "type": "vm", "ip": "192.168.1.38"},
            {"id": "postgres-vm", "label": "PostgreSQL VM", "type": "database", "ip": "192.168.1.25"},
        ],
        "k8s_nodes": [
            {**node, "metrics": next(
                (m for m in node_metrics if node["ip"] in m["instance"]),
                {"cpu_pct": 0, "memory_pct": 0, "disk_pct": 0},
            )}
            for node in k8s_nodes
        ],
        "pods": pods,
        "pod_counts": pod_count_by_namespace(),
    }
    return topology
