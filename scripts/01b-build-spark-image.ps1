param(
    [string]$Region = $(if ($env:SWR_REGION) { $env:SWR_REGION } else { "cn-east-3" }),
    [string]$Org = $(if ($env:SWR_ORG) { $env:SWR_ORG } else { "cloud-swjtu" }),
    [string]$Tag = $(if ($env:SPARK_IMAGE_TAG) { $env:SPARK_IMAGE_TAG } else { "v1" })
)

$ErrorActionPreference = "Stop"
$Registry = if ($env:SWR_REGISTRY) { $env:SWR_REGISTRY } else { "swr.$Region.myhuaweicloud.com" }
$SparkImage = "$Registry/$Org/pyspark:$Tag"

Write-Host "Building Spark image: $SparkImage"
docker build --provenance=false -t $SparkImage -f spark/Dockerfile.pyspark .
if ($LASTEXITCODE -ne 0) { throw "Spark image build failed." }
docker images $Registry/$Org/pyspark
