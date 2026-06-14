param(
    [string]$Kubeconfig = ".\kubeconfig.yaml",
    [string]$Namespace = "cloud-course"
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path $Kubeconfig)) {
    throw "Kubeconfig not found: $Kubeconfig"
}

New-Item -ItemType Directory -Force -Path evidence | Out-Null

Write-Host "== Service external addresses =="
kubectl --kubeconfig $Kubeconfig -n $Namespace get svc -o wide | Tee-Object evidence\03-services.txt

$backendIp = kubectl --kubeconfig $Kubeconfig -n $Namespace get svc backend-svc -o jsonpath="{.status.loadBalancer.ingress[0].ip}"
if (-not $backendIp) {
    $backendIp = kubectl --kubeconfig $Kubeconfig -n $Namespace get svc backend-svc -o jsonpath="{.status.loadBalancer.ingress[0].hostname}"
}
if ($backendIp) {
    Write-Host "Backend ELB: $backendIp"
    curl.exe -s "http://$backendIp/api/ping" | Tee-Object evidence\06-backend-ping.txt
} else {
    Write-Host "Backend LoadBalancer IP is not allocated yet."
}

Write-Host "`n== Redis persistence verification =="
$redisPod = kubectl --kubeconfig $Kubeconfig -n $Namespace get pod -l app=redis -o jsonpath="{.items[0].metadata.name}"
kubectl --kubeconfig $Kubeconfig -n $Namespace exec $redisPod -- redis-cli -a cloud-course-2026 SET testkey hello | Tee-Object evidence\07-redis-set.txt
kubectl --kubeconfig $Kubeconfig -n $Namespace delete pod $redisPod
kubectl --kubeconfig $Kubeconfig -n $Namespace wait --for=condition=ready pod -l app=redis --timeout=180s
$newRedisPod = kubectl --kubeconfig $Kubeconfig -n $Namespace get pod -l app=redis -o jsonpath="{.items[0].metadata.name}"
kubectl --kubeconfig $Kubeconfig -n $Namespace exec $newRedisPod -- redis-cli -a cloud-course-2026 GET testkey | Tee-Object evidence\08-redis-get-after-restart.txt

Write-Host "`n== ConfigMap volume verification =="
$frontendPod = kubectl --kubeconfig $Kubeconfig -n $Namespace get pod -l app=frontend -o jsonpath="{.items[0].metadata.name}"
kubectl --kubeconfig $Kubeconfig -n $Namespace exec $frontendPod -- cat /etc/nginx/conf.d/default.conf | Tee-Object evidence\09-nginx-config.txt

Write-Host "`n== HPA status =="
kubectl --kubeconfig $Kubeconfig -n $Namespace describe hpa backend-hpa | Tee-Object evidence\10-hpa-describe.txt
