# Monitoring bonus evidence

This folder contains a lightweight `kube-prometheus-stack` values file for the
course bonus task.

Run from CloudShell after uploading the folder:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts || true
helm repo update
helm upgrade --install cloud-monitor prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace \
  -f monitoring/kube-prometheus-stack-values.yaml

kubectl -n monitoring get pods -o wide
kubectl -n monitoring get svc
```

Screenshots to capture:

- `kubectl -n monitoring get pods -o wide`, all major pods Running.
- Grafana Service external IP.
- Grafana dashboard with node CPU utilization line chart.
- Grafana dashboard with Pod memory usage chart.

Report concepts:

- Prometheus Pull: Prometheus periodically scrapes HTTP metrics endpoints of
  nodes, kube-state-metrics, and Kubernetes components.
- Node CPU utilization: CPU time consumed by the node workload and system
  components.
- Pod memory usage: working set memory currently used by a Pod.
- Pod restart count: cumulative container restarts, useful for detecting
  unstable workloads.
