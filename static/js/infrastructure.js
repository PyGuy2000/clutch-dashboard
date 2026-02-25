/**
 * Infrastructure topology graph using Cytoscape.js with dagre layout.
 * Fetches live data from /api/infra/topology every 30 seconds.
 */

(function () {
    'use strict';

    // Color palette matching the dashboard CSS variables
    const COLORS = {
        green: '#4ade80',
        yellow: '#facc15',
        red: '#f87171',
        blue: '#60a5fa',
        accent: '#38bdf8',
        surface: '#1e293b',
        border: '#334155',
        text: '#e2e8f0',
        muted: '#94a3b8',
        purple: '#c084fc',
        orange: '#fb923c',
    };

    // Node type → shape and color mapping
    const NODE_STYLES = {
        gateway:    { color: COLORS.orange, shape: 'diamond' },
        hypervisor: { color: COLORS.blue, shape: 'round-rectangle' },
        storage:    { color: COLORS.purple, shape: 'barrel' },
        gpu:        { color: COLORS.green, shape: 'hexagon' },
        vm:         { color: COLORS.accent, shape: 'round-rectangle' },
        database:   { color: COLORS.yellow, shape: 'round-rectangle' },
        k8s_node:   { color: COLORS.blue, shape: 'ellipse' },
        pod:        { color: COLORS.green, shape: 'ellipse' },
    };

    let cy = null;

    function initGraph(data) {
        const elements = buildElements(data);

        cy = cytoscape({
            container: document.getElementById('cy'),
            elements: elements,
            style: [
                {
                    selector: 'node',
                    style: {
                        'label': 'data(label)',
                        'text-valign': 'bottom',
                        'text-halign': 'center',
                        'font-size': '12px',
                        'color': COLORS.text,
                        'text-margin-y': 8,
                        'text-wrap': 'wrap',
                        'text-max-width': '300px',
                        'min-zoomed-font-size': 0,
                        'background-color': 'data(color)',
                        'shape': 'data(shape)',
                        'width': 40,
                        'height': 40,
                        'border-width': 2,
                        'border-color': COLORS.border,
                    }
                },
                {
                    selector: 'node[type = "k8s_node"]',
                    style: {
                        'width': 50,
                        'height': 50,
                    }
                },
                {
                    selector: 'node[type = "gpu"]',
                    style: {
                        'width': 55,
                        'height': 55,
                    }
                },
                {
                    selector: 'node[type = "gateway"]',
                    style: {
                        'width': 50,
                        'height': 50,
                    }
                },
                {
                    selector: 'node.unhealthy',
                    style: {
                        'border-color': COLORS.red,
                        'border-width': 3,
                    }
                },
                {
                    selector: 'node.warning',
                    style: {
                        'border-color': COLORS.yellow,
                        'border-width': 3,
                    }
                },
                {
                    selector: 'edge',
                    style: {
                        'width': 2,
                        'line-color': COLORS.border,
                        'curve-style': 'bezier',
                        'target-arrow-shape': 'none',
                    }
                },
                {
                    selector: 'node:selected',
                    style: {
                        'border-color': COLORS.accent,
                        'border-width': 3,
                    }
                },
            ],
            layout: {
                name: 'dagre',
                rankDir: 'TB',
                nodeSep: 180,
                rankSep: 110,
                padding: 100,
                fit: true,
            },
            userZoomingEnabled: true,
            userPanningEnabled: true,
            boxSelectionEnabled: false,
            textureOnViewport: false,
        });

        // Re-fit with extra padding after layout to account for label overflow
        cy.on('layoutstop', function () {
            cy.fit(cy.elements(), 100);
        });

        // Click handler for detail panel
        cy.on('tap', 'node', function (evt) {
            showDetail(evt.target.data());
        });

        cy.on('tap', function (evt) {
            if (evt.target === cy) {
                hideDetail();
            }
        });
    }

    function buildElements(data) {
        const elements = [];

        // Physical infrastructure nodes
        if (data.physical) {
            data.physical.forEach(function (node) {
                const style = NODE_STYLES[node.type] || NODE_STYLES.vm;
                elements.push({
                    data: {
                        id: node.id,
                        label: node.label + '\n' + node.ip,
                        color: style.color,
                        shape: style.shape,
                        type: node.type,
                        ip: node.ip,
                        raw: node,
                    }
                });
            });
        }

        // K8s nodes
        if (data.k8s_nodes) {
            data.k8s_nodes.forEach(function (node) {
                const style = NODE_STYLES.k8s_node;
                let statusClass = '';
                if (!node.ready) statusClass = 'unhealthy';
                else if (node.metrics && (node.metrics.cpu_pct > 85 || node.metrics.memory_pct > 85)) statusClass = 'warning';

                elements.push({
                    data: {
                        id: 'k8s-' + node.name,
                        label: node.name + '\n' + node.ip,
                        color: style.color,
                        shape: style.shape,
                        type: 'k8s_node',
                        ip: node.ip,
                        raw: node,
                    },
                    classes: statusClass,
                });
            });
        }

        // Edges — connect physical topology
        // UDM Pro → all NUCs
        ['nuc1', 'nuc2', 'nuc3'].forEach(function (nuc) {
            elements.push({ data: { source: 'udm-pro', target: nuc } });
        });
        // UDM Pro → NAS, AI Workstation
        elements.push({ data: { source: 'udm-pro', target: 'nas' } });
        elements.push({ data: { source: 'udm-pro', target: 'ai-workstation' } });

        // NUC1 → OpenClaw VM, PostgreSQL VM
        elements.push({ data: { source: 'nuc1', target: 'openclaw-vm' } });
        elements.push({ data: { source: 'nuc1', target: 'postgres-vm' } });

        // NUCs → K8s nodes
        if (data.k8s_nodes) {
            var k8sNodeIds = data.k8s_nodes.map(function (n) { return 'k8s-' + n.name; });
            // Control plane on NUC1, workers on NUC2/NUC3
            if (k8sNodeIds.length >= 1) elements.push({ data: { source: 'nuc1', target: k8sNodeIds[0] } });
            if (k8sNodeIds.length >= 2) elements.push({ data: { source: 'nuc2', target: k8sNodeIds[1] } });
            if (k8sNodeIds.length >= 3) elements.push({ data: { source: 'nuc3', target: k8sNodeIds[2] } });
        }

        // OpenClaw → AI Workstation (Ollama, faster-whisper)
        elements.push({ data: { source: 'openclaw-vm', target: 'ai-workstation' } });

        return elements;
    }

    function showDetail(nodeData) {
        var panel = document.getElementById('detail-panel');
        var title = document.getElementById('detail-title');
        var content = document.getElementById('detail-content');

        panel.style.display = 'block';
        title.textContent = nodeData.label.replace('\n', ' — ');

        var html = '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; font-size: 0.875rem;">';
        html += '<div><strong>IP:</strong> ' + (nodeData.ip || 'N/A') + '</div>';
        html += '<div><strong>Type:</strong> ' + (nodeData.type || 'N/A') + '</div>';

        if (nodeData.raw) {
            var raw = nodeData.raw;

            // K8s node details
            if (nodeData.type === 'k8s_node') {
                html += '<div><strong>Status:</strong> ' + (raw.ready ? '<span style="color:#4ade80">Ready</span>' : '<span style="color:#f87171">Not Ready</span>') + '</div>';
                html += '<div><strong>K3s:</strong> ' + (raw.kubelet_version || '') + '</div>';
                html += '<div><strong>CPU:</strong> ' + (raw.cpu_capacity || '') + ' cores</div>';
                html += '<div><strong>RAM:</strong> ' + (raw.memory_capacity_gb || '') + ' GB</div>';
                if (raw.metrics) {
                    html += '<div><strong>CPU Usage:</strong> ' + raw.metrics.cpu_pct + '%</div>';
                    html += '<div><strong>Mem Usage:</strong> ' + raw.metrics.memory_pct + '%</div>';
                    html += '<div><strong>Disk Usage:</strong> ' + raw.metrics.disk_pct + '%</div>';
                }
            }

            // GPU/AI Workstation details
            if (nodeData.type === 'gpu' && raw.gpu) {
                var gpuData = raw.gpu;
                if (gpuData.gpus) {
                    gpuData.gpus.forEach(function (g) {
                        html += '<div style="grid-column: 1 / -1; margin-top: 0.5rem; border-top: 1px solid #334155; padding-top: 0.5rem;">';
                        html += '<strong>GPU ' + g.index + ':</strong> ' + g.name;
                        html += ' | ' + g.utilization_pct + '% util';
                        html += ' | ' + g.memory_used_mb + '/' + g.memory_total_mb + ' MB VRAM';
                        html += ' | ' + g.temperature_c + '&deg;C';
                        html += '</div>';
                    });
                }
                if (raw.ollama && raw.ollama.running) {
                    html += '<div style="grid-column: 1 / -1; margin-top: 0.5rem; border-top: 1px solid #334155; padding-top: 0.5rem;">';
                    html += '<strong>Loaded Models:</strong> ';
                    html += raw.ollama.running.map(function (m) { return m.name + ' (' + m.vram_gb + 'GB)'; }).join(', ');
                    html += '</div>';
                }
            }
        }

        html += '</div>';
        content.innerHTML = html;
    }

    function hideDetail() {
        document.getElementById('detail-panel').style.display = 'none';
    }

    // Auto-refresh every 30 seconds
    function refresh() {
        fetch('/api/infra/topology')
            .then(function (res) { return res.json(); })
            .then(function (data) {
                if (cy) {
                    // Update node data without re-rendering layout
                    updateNodeData(data);
                }
            })
            .catch(function () {
                // Silently fail on network errors
            });
    }

    function updateNodeData(data) {
        // Update K8s node metrics
        if (data.k8s_nodes) {
            data.k8s_nodes.forEach(function (node) {
                var cyNode = cy.getElementById('k8s-' + node.name);
                if (cyNode.length) {
                    cyNode.data('raw', node);
                    cyNode.removeClass('unhealthy warning');
                    if (!node.ready) cyNode.addClass('unhealthy');
                    else if (node.metrics && (node.metrics.cpu_pct > 85 || node.metrics.memory_pct > 85)) cyNode.addClass('warning');
                }
            });
        }

        // Update AI Workstation data
        if (data.physical) {
            data.physical.forEach(function (node) {
                var cyNode = cy.getElementById(node.id);
                if (cyNode.length) {
                    cyNode.data('raw', node);
                }
            });
        }
    }

    // Initial load
    fetch('/api/infra/topology')
        .then(function (res) { return res.json(); })
        .then(function (data) {
            initGraph(data);
        })
        .catch(function () {
            document.getElementById('cy').innerHTML = '<div style="text-align:center;padding:2rem;color:#94a3b8;">Unable to load topology data. K8s API may not be accessible.</div>';
        });

    // Refresh every 30 seconds
    setInterval(refresh, 30000);
})();
