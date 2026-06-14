param(
    [string]$Kubeconfig = ".\kubeconfig.yaml",
    [string]$Application = ".\spark\sparkapplication-wordcount.yaml"
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path $Kubeconfig)) {
    throw "Kubeconfig not found: $Kubeconfig"
}
if (-not (Test-Path $Application)) {
    throw "SparkApplication YAML not found: $Application"
}

kubectl --kubeconfig $Kubeconfig apply -f $Application
Start-Sleep -Seconds 5
kubectl --kubeconfig $Kubeconfig get pods -n default -o wide | Tee-Object evidence\11-spark-pods.txt
