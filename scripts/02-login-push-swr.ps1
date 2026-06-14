param(
    [string]$Region = $(if ($env:SWR_REGION) { $env:SWR_REGION } else { "cn-east-3" }),
    [string]$Org = $(if ($env:SWR_ORG) { $env:SWR_ORG } else { "cloud-swjtu" }),
    [string]$Tag = $(if ($env:IMAGE_TAG) { $env:IMAGE_TAG } else { "v1" })
)

$ErrorActionPreference = "Stop"
$Registry = if ($env:SWR_REGISTRY) { $env:SWR_REGISTRY } else { "swr.$Region.myhuaweicloud.com" }
$BackendImage = "$Registry/$Org/backend:$Tag"
$FrontendImage = "$Registry/$Org/frontend:$Tag"

if (-not $env:SWR_USERNAME -or -not $env:SWR_PASSWORD) {
    throw "Set SWR_USERNAME and SWR_PASSWORD first. Use the temporary SWR docker login token from Huawei Cloud SWR."
}

Write-Host "Logging in to $Registry as $env:SWR_USERNAME"
$env:SWR_PASSWORD | docker login $Registry -u $env:SWR_USERNAME --password-stdin

Write-Host "Pushing $BackendImage"
docker push $BackendImage

Write-Host "Pushing $FrontendImage"
docker push $FrontendImage

Write-Host "SWR push complete."
