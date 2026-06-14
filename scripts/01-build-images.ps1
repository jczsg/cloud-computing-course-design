param(
    [string]$Region = $(if ($env:SWR_REGION) { $env:SWR_REGION } else { "cn-east-3" }),
    [string]$Org = $(if ($env:SWR_ORG) { $env:SWR_ORG } else { "cloud-swjtu" }),
    [string]$Tag = $(if ($env:IMAGE_TAG) { $env:IMAGE_TAG } else { "v1" })
)

$ErrorActionPreference = "Stop"
$Registry = if ($env:SWR_REGISTRY) { $env:SWR_REGISTRY } else { "swr.$Region.myhuaweicloud.com" }
$BackendImage = "$Registry/$Org/backend:$Tag"
$FrontendImage = "$Registry/$Org/frontend:$Tag"

Write-Host "Building backend:  $BackendImage"
docker build --provenance=false -t $BackendImage -f app/backend/Dockerfile.backend app/backend
if ($LASTEXITCODE -ne 0) { throw "Backend image build failed." }

Write-Host "Building frontend: $FrontendImage"
docker build --provenance=false -t $FrontendImage -f app/frontend/Dockerfile.frontend app/frontend
if ($LASTEXITCODE -ne 0) { throw "Frontend image build failed." }

Write-Host "`nBuilt images:"
docker images $Registry/$Org/backend
docker images $Registry/$Org/frontend
