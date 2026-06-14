param(
    [string]$Kubeconfig = ".\kubeconfig.yaml"
)

$ErrorActionPreference = "Continue"

function Test-Cmd($Name) {
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if ($cmd) {
        Write-Host "[OK] $Name -> $($cmd.Source)"
        return $true
    }
    Write-Host "[MISS] $Name"
    return $false
}

function Find-Helm {
    $cmd = Get-Command helm -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $candidate = Get-ChildItem -Path "$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -Recurse -Filter helm.exe -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($candidate) { return $candidate.FullName }
    return $null
}

Write-Host "== Toolchain =="
Test-Cmd docker | Out-Null
Test-Cmd kubectl | Out-Null
$helm = Find-Helm
if ($helm) { Write-Host "[OK] helm -> $helm" } else { Write-Host "[MISS] helm" }

Write-Host "`n== Docker =="
docker info --format "Server={{.ServerVersion}} Context={{.Name}}" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] Docker daemon is not ready."
}

Write-Host "`n== Kubernetes =="
if (Test-Path $Kubeconfig) {
    Write-Host "[OK] kubeconfig found: $Kubeconfig"
    kubectl --kubeconfig $Kubeconfig config current-context
    kubectl --kubeconfig $Kubeconfig get nodes -o wide
} else {
    Write-Host "[MISS] kubeconfig not found: $Kubeconfig"
}

Write-Host "`n== Cloud variables =="
foreach ($name in @("SWR_REGION", "SWR_ORG", "SWR_REGISTRY", "SWR_USERNAME", "SWR_PASSWORD")) {
    if ([string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable($name))) {
        Write-Host "[MISS] $name"
    } else {
        if ($name -eq "SWR_PASSWORD") {
            Write-Host "[OK] $name=<hidden>"
        } else {
            Write-Host "[OK] $name=$([Environment]::GetEnvironmentVariable($name))"
        }
    }
}
