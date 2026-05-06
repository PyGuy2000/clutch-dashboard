"""Pediatrica dashboard health queries — pipeline status + K8s pod health."""

import json
import urllib.request
from datetime import datetime, timezone

# In-cluster K8s API access (same pattern as infrastructure.py)
K8S_API = "https://kubernetes.default.svc"
K8S_TOKEN_PATH = "/var/run/secrets/kubernetes.io/serviceaccount/token"
K8S_CA_PATH = "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"

# Pediatrica app endpoint (in-cluster service discovery)
PEDIATRICA_STATUS_URL = (
    "http://pediatrica.pediatrica.svc.cluster.local/data/pipeline_status.json"
)
PEDIATRICA_STATUS_FALLBACK = (
    "https://pediatrica-embed.kazzerlabs.dev/data/pipeline_status.json"
)


def _k8s_get(path):
    """Make an authenticated GET to the K8s API server."""
    try:
        with open(K8S_TOKEN_PATH) as f:
            token = f.read().strip()
    except FileNotFoundError:
        return None

    try:
        import ssl

        url = f"{K8S_API}{path}"
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            },
        )
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


def get_pipeline_status():
    """Fetch pipeline_status.json from the deployed Pediatrica app."""
    data = _http_get_json(PEDIATRICA_STATUS_URL)
    if not data:
        data = _http_get_json(PEDIATRICA_STATUS_FALLBACK)
    return data


def get_deployed_pods():
    """Get Pediatrica pods from K8s API."""
    data = _k8s_get("/api/v1/namespaces/pediatrica/pods")
    if not data:
        return []

    pods = []
    for item in data.get("items", []):
        meta = item.get("metadata", {})
        status = item.get("status", {})
        containers = status.get("containerStatuses", [])

        image = ""
        restarts = 0
        ready = True
        for cs in containers:
            image = cs.get("image", "")
            restarts += cs.get("restartCount", 0)
            if not cs.get("ready", False):
                ready = False

        pods.append({
            "name": meta.get("name", ""),
            "phase": status.get("phase", "Unknown"),
            "image": image,
            "image_tag": image.split(":")[-1] if ":" in image else "unknown",
            "restarts": restarts,
            "ready": ready,
            "node": item.get("spec", {}).get("nodeName", ""),
        })
    return pods


def get_pediatrica_health():
    """Aggregate pipeline status + pod health into a single health assessment."""
    pipeline = get_pipeline_status()
    pods = get_deployed_pods()

    issues = []
    metrics = {
        "pipeline": pipeline,
        "pods": pods,
        "data_age_hours": None,
        "deployed_tag": None,
    }

    # Check pipeline status JSON
    if not pipeline:
        issues.append({
            "severity": "critical",
            "message": "Cannot reach pipeline_status.json — app may be down or status file not yet deployed",
        })
    else:
        # Calculate data age
        try:
            last_scrape = datetime.fromisoformat(pipeline["last_scrape"])
            now = datetime.now(timezone.utc)
            age_hours = (now - last_scrape).total_seconds() / 3600
            metrics["data_age_hours"] = round(age_hours, 1)

            if age_hours > 48:
                issues.append({
                    "severity": "critical",
                    "message": f"Data is {age_hours:.0f}h old (>48h threshold)",
                })
            elif age_hours > 26:
                issues.append({
                    "severity": "warning",
                    "message": f"Data is {age_hours:.0f}h old (expected <26h for daily refresh)",
                })
        except (KeyError, ValueError):
            issues.append({
                "severity": "warning",
                "message": "Cannot parse last_scrape timestamp from pipeline status",
            })

    # Check pod health
    if not pods:
        issues.append({
            "severity": "warning",
            "message": "No pods found in pediatrica namespace",
        })
    else:
        metrics["deployed_tag"] = pods[0].get("image_tag")
        for pod in pods:
            if not pod["ready"]:
                issues.append({
                    "severity": "critical",
                    "message": f"Pod {pod['name']} is not ready (phase: {pod['phase']})",
                })
            if pod["restarts"] >= 5:
                issues.append({
                    "severity": "warning",
                    "message": f"Pod {pod['name']} has {pod['restarts']} restarts",
                })

    # Determine overall status
    if any(i["severity"] == "critical" for i in issues):
        status = "critical"
    elif issues:
        status = "warning"
    else:
        status = "healthy"

    return {
        "status": status,
        "issues": issues,
        "metrics": metrics,
    }
