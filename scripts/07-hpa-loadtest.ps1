param(
    [string]$Kubeconfig = ".\kubeconfig.yaml",
    [string]$Namespace = "cloud-course",
    [string]$Url = "",
    [int]$Seconds = 120,
    [int]$Concurrency = 80
)

$ErrorActionPreference = "Stop"

if (-not $Url) {
    if (-not (Test-Path $Kubeconfig)) {
        throw "Kubeconfig not found and Url was not provided."
    }
    $backendIp = kubectl --kubeconfig $Kubeconfig -n $Namespace get svc backend-svc -o jsonpath="{.status.loadBalancer.ingress[0].ip}"
    if (-not $backendIp) {
        $backendIp = kubectl --kubeconfig $Kubeconfig -n $Namespace get svc backend-svc -o jsonpath="{.status.loadBalancer.ingress[0].hostname}"
    }
    if (-not $backendIp) {
        throw "backend-svc LoadBalancer address is not ready."
    }
    $Url = "http://$backendIp/api/ping"
}

Write-Host "Load testing $Url for $Seconds seconds with $Concurrency workers."
Write-Host "Open another terminal and run: kubectl --kubeconfig $Kubeconfig -n $Namespace get pods -w"

$until = (Get-Date).AddSeconds($Seconds)
$jobs = @()
for ($i = 0; $i -lt $Concurrency; $i++) {
    $jobs += Start-Job -ScriptBlock {
        param($TargetUrl, $StopAt)
        $count = 0
        while ((Get-Date) -lt $StopAt) {
            try {
                Invoke-WebRequest -UseBasicParsing -Uri $TargetUrl -TimeoutSec 3 | Out-Null
                $count++
            } catch {
            }
        }
        $count
    } -ArgumentList $Url, $until
}

Wait-Job $jobs | Out-Null
$total = 0
foreach ($job in $jobs) {
    $total += [int](Receive-Job $job)
    Remove-Job $job
}

New-Item -ItemType Directory -Force -Path evidence | Out-Null
"url=$Url seconds=$Seconds concurrency=$Concurrency total_requests=$total" | Tee-Object evidence\12-hpa-loadtest.txt
kubectl --kubeconfig $Kubeconfig -n $Namespace get hpa -o wide | Tee-Object evidence\13-hpa-after-load.txt
kubectl --kubeconfig $Kubeconfig -n $Namespace get pods -o wide | Tee-Object evidence\14-pods-after-load.txt
