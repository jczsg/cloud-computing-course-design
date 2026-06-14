# Kubernetes deployment notes

Replace the SWR organization and image tags in the YAML files if your Huawei Cloud
region or organization is different.

Apply all resources:

```bash
kubectl apply -f k8s/
```

Common verification commands:

```bash
kubectl get nodes -o wide
kubectl get pods -n cloud-course -o wide
kubectl get svc -n cloud-course
kubectl get pvc -n cloud-course
kubectl get hpa -n cloud-course
```

Redis persistence verification:

```bash
REDIS_POD=$(kubectl get pod -n cloud-course -l app=redis -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n cloud-course "$REDIS_POD" -- redis-cli -a cloud-course-2026 SET testkey hello
kubectl delete pod -n cloud-course "$REDIS_POD"
kubectl wait --for=condition=ready pod -n cloud-course -l app=redis --timeout=180s
NEW_REDIS_POD=$(kubectl get pod -n cloud-course -l app=redis -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n cloud-course "$NEW_REDIS_POD" -- redis-cli -a cloud-course-2026 GET testkey
```

ConfigMap volume verification:

```bash
kubectl apply -f k8s/05-nginx-configmap.yaml
kubectl delete pod -n cloud-course -l app=frontend
kubectl wait --for=condition=ready pod -n cloud-course -l app=frontend --timeout=180s
FRONTEND_POD=$(kubectl get pod -n cloud-course -l app=frontend -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n cloud-course "$FRONTEND_POD" -- cat /etc/nginx/conf.d/default.conf
```

HPA pressure test:

```bash
kubectl scale deployment/backend -n cloud-course --replicas=1
kubectl get pods -n cloud-course -w
ab -n 10000 -c 200 http://<ELB_IP>/api/ping
kubectl describe hpa backend-hpa -n cloud-course
```
