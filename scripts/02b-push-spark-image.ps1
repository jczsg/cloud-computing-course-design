param(
    [string]$Region = $(if ($env:SWR_REGION) { $env:SWR_REGION } else { "cn-east-3" }),
    [string]$Org = $(if ($env:SWR_ORG) { $env:SWR_ORG } else { "cloud-swjtu" }),
    [string]$Tag = $(if ($env:SPARK_IMAGE_TAG) { $env:SPARK_IMAGE_TAG } else { "v1" })
)

$ErrorActionPreference = "Stop"
$Registry = if ($env:SWR_REGISTRY) { $env:SWR_REGISTRY } else { "swr.$Region.myhuaweicloud.com" }
$SparkImage = "$Registry/$Org/pyspark:$Tag"

if (-not $env:SWR_USERNAME -or -not $env:SWR_PASSWORD) {
    throw "Set SWR_USERNAME and SWR_PASSWORD first. Use the temporary SWR docker login token from Huawei Cloud SWR."
}

$env:SWR_PASSWORD | docker login $Registry -u $env:SWR_USERNAME --password-stdin
docker push $SparkImage
