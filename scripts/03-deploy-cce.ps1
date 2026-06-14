param(
    [string]$Kubeconfig = ".\kubeconfig.yaml",
    [string]$Region = $(if ($env:SWR_REGION) { $env:SWR_REGION } else { "cn-east-3" }),
    [string]$Org = $(if ($env:SWR_ORG) { $env:SWR_ORG } else { "cloud-swjtu" }),
    [string]$Tag = $(if ($env:IMAGE_TAG) { $env:IMAGE_TAG } else { "v1" }),
    [string]$Namespace = "cloud-course",
    [string]$ImagePullSecret = "swr-secret"
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path $Kubeconfig)) {
    throw "Kubeconfig not found: $Kubeconfig"
}

$Registry = if ($env:SWR_REGISTRY) { $env:SWR_REGISTRY } else { "swr.$Region.myhuaweicloud.com" }
$BackendImage = "$Registry/$Org/backend:$Tag"
$FrontendImage = "$Registry/$Org/frontend:$Tag"
$GeneratedDir = "k8s\generated"
New-Item -ItemType Directory -Force -Path $GeneratedDir | Out-Null

Copy-Item -Force k8s\*.yaml $GeneratedDir
$backendYaml = Join-Path $GeneratedDir "04-backend-deployment-service.yaml"
$frontendYaml = Join-Path $GeneratedDir "06-frontend-deployment-service.yaml"
(Get-Content $backendYaml -Raw) -replace 'image:\s*\S+/backend:\S+', "image: $BackendImage" | Set-Content -Encoding utf8 $backendYaml
(Get-Content $frontendYaml -Raw) -replace 'image:\s*\S+/frontend:\S+', "image: $FrontendImage" | Set-Content -Encoding utf8 $frontendYaml

Write-Host "Using backend image:  $BackendImage"
Write-Host "Using frontend image: $FrontendImage"

kubectl --kubeconfig $Kubeconfig apply -f $GeneratedDir

if ($env:SWR_USERNAME -and $env:SWR_PASSWORD) {
    Write-Host "Creating/updating imagePullSecret $ImagePullSecret"
    kubectl --kubeconfig $Kubeconfig -n $Namespace create secret docker-registry $ImagePullSecret `
        --docker-server=$Registry `
        --docker-username=$env:SWR_USERNAME `
        --docker-password=$env:SWR_PASSWORD `
        --dry-run=client -o yaml | kubectl --kubeconfig $Kubeconfig apply -f -

    $patch = '{"spec":{"template":{"spec":{"imagePullSecrets":[{"name":"' + $ImagePullSecret + '"}]}}}}'
    kubectl --kubeconfig $Kubeconfig -n $Namespace patch deployment backend -p $patch
    kubectl --kubeconfig $Kubeconfig -n $Namespace patch deployment frontend -p $patch
}

Write-Host "Waiting for deployments..."
kubectl --kubeconfig $Kubeconfig -n $Namespace rollout status deployment/redis --timeout=300s
kubectl --kubeconfig $Kubeconfig -n $Namespace rollout status deployment/backend --timeout=300s
kubectl --kubeconfig $Kubeconfig -n $Namespace rollout status deployment/frontend --timeout=300s

New-Item -ItemType Directory -Force -Path evidence | Out-Null
kubectl --kubeconfig $Kubeconfig get nodes -o wide | Tee-Object evidence\01-nodes.txt
kubectl --kubeconfig $Kubeconfig -n $Namespace get pods -o wide | Tee-Object evidence\02-pods.txt
kubectl --kubeconfig $Kubeconfig -n $Namespace get svc -o wide | Tee-Object evidence\03-services.txt
kubectl --kubeconfig $Kubeconfig -n $Namespace get pvc -o wide | Tee-Object evidence\04-pvc.txt
kubectl --kubeconfig $Kubeconfig -n $Namespace get hpa -o wide | Tee-Object evidence\05-hpa.txt
