param(
    [string]$Kubeconfig = ".\kubeconfig.yaml",
    [string]$ChartPath = ".\spark-operator-chart",
    [string]$ReleaseName = "spark-op",
    [string]$Namespace = "spark-operator"
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path $Kubeconfig)) {
    throw "Kubeconfig not found: $Kubeconfig"
}
if (-not (Test-Path $ChartPath)) {
    throw "Spark Operator chart not found: $ChartPath"
}

$helm = Get-Command helm -ErrorAction SilentlyContinue
if ($helm) {
    $helmExe = $helm.Source
} else {
    $candidate = Get-ChildItem -Path "$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -Recurse -Filter helm.exe -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $candidate) { throw "helm.exe not found" }
    $helmExe = $candidate.FullName
}

& $helmExe upgrade --install $ReleaseName $ChartPath -n $Namespace --create-namespace --kubeconfig $Kubeconfig
kubectl --kubeconfig $Kubeconfig get pods -n $Namespace -o wide
