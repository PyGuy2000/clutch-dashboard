from flask import Blueprint, render_template, jsonify

from queries.infrastructure import (
    get_k8s_nodes,
    get_k8s_pods,
    get_k8s_services,
    get_gpu_metrics,
    get_node_metrics,
    get_ollama_status,
    get_infra_topology,
)

bp = Blueprint("infrastructure", __name__)


@bp.route("/infra")
def infra_index():
    nodes = get_k8s_nodes()
    pods = get_k8s_pods()
    services = get_k8s_services()
    gpu = get_gpu_metrics()
    node_metrics = get_node_metrics()
    ollama = get_ollama_status()

    return render_template(
        "infrastructure.html",
        active_page="infra",
        nodes=nodes,
        pods=pods,
        services=services,
        gpu=gpu,
        node_metrics=node_metrics,
        ollama=ollama,
    )


@bp.route("/api/infra/topology")
def api_topology():
    """JSON endpoint for Cytoscape.js live refresh."""
    return jsonify(get_infra_topology())


@bp.route("/api/infra/gpu")
def api_gpu():
    """JSON endpoint for GPU metrics refresh."""
    return jsonify(get_gpu_metrics())


@bp.route("/api/infra/nodes")
def api_nodes():
    """JSON endpoint for K8s node metrics refresh."""
    return jsonify({"nodes": get_k8s_nodes(), "metrics": get_node_metrics()})


@bp.route("/api/infra/ollama")
def api_ollama():
    """JSON endpoint for Ollama status refresh."""
    return jsonify(get_ollama_status())
