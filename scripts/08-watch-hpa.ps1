param(
    [string]$Kubeconfig = ".\kubeconfig.yaml",
    [string]$Namespace = "cloud-course",
    [int]$Seconds = 180,
    [int]$IntervalSeconds = 10
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path $Kubeconfig)) {
    throw "Kubeconfig not found: $Kubeconfig"
}

New-Item -ItemType Directory -Force -Path evidence | Out-Null
$out = "evidence\15-hpa-watch.txt"
"HPA watch started: $(Get-Date)" | Set-Content -Encoding utf8 $out
$deadline = (Get-Date).AddSeconds($Seconds)
while ((Get-Date) -lt $deadline) {
    "===== $(Get-Date) =====" | Add-Content -Encoding utf8 $out
    kubectl --kubeconfig $Kubeconfig -n $Namespace get hpa | Add-Content -Encoding utf8 $out
    kubectl --kubeconfig $Kubeconfig -n $Namespace get pods | Add-Content -Encoding utf8 $out
    Start-Sleep -Seconds $IntervalSeconds
}
