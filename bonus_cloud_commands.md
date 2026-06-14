# 满分与附加题云端补证据命令

以下命令默认在华为云 CloudShell 中执行，当前 kubeconfig 已指向 CCE 集群。

## 0. 上传新版代码包

先把本地项目重新压缩上传到 CloudShell，至少需要包含：

- `spark/`
- `monitoring/`
- `edge_mqtt/`
- `.github/workflows/huawei-swr-cce.yml`

进入项目目录后执行：

```bash
cd ~/cloud-course
```

## 1. Spark 满分证据补齐

### 1.1 本地重新构建并推送 PySpark v2 镜像

这一步在本地 PowerShell 执行，不在 CloudShell 执行：

```powershell
$env:SWR_REGION="cn-east-3"
$env:SWR_ORG="cloud-swjtu"
$env:SPARK_IMAGE_TAG="v2"
$env:SWR_USERNAME="cn-east-3@HST3WX9V79SH02TUJTW7"
$env:SWR_PASSWORD="<SWR 登录 token>"
.\scripts\01b-build-spark-image.ps1
.\scripts\02b-push-spark-image.ps1
```

截图：SWR 控制台 `pyspark:v2` 镜像列表。

### 1.2 确保 Spark Operator 正常

```bash
kubectl -n spark-operator get pods -o wide
kubectl get crd | grep -i spark
```

截图：`spark-op-spark-operator-controller` 为 Running。

### 1.3 运行 wordcount SparkApplication

```bash
kubectl delete sparkapplication wordcount -n default --ignore-not-found
kubectl apply -f spark/sparkapplication-wordcount.yaml
kubectl get sparkapplication -n default -w
```

另开或等完成后：

```bash
kubectl get pods -n default -o wide | grep -i wordcount
kubectl logs -n default wordcount-driver | tail -n 40
```

截图：

- `wordcount` 状态 Completed。
- Driver/Executor Pod 截图。
- 日志中 `Top 10 words` 截图。

### 1.4 运行豆瓣 Spark 分析 executor=1

```bash
kubectl delete sparkapplication douban-analysis-1exec -n default --ignore-not-found
kubectl apply -f spark/douban-sparkapplication-1exec.yaml
kubectl get sparkapplication -n default -w
```

完成后：

```bash
kubectl logs -n default douban-analysis-1exec-driver | tee douban-1exec.log
grep -E "Raw schema|Raw sample|Rows before|Rows after|Query|TOTAL_SECONDS" douban-1exec.log
```

截图：

- SparkApplication Completed。
- schema / 前 5 行。
- 缺失比例与清洗前后行数。
- Query 1 到 Query 5 结果。
- `TOTAL_SECONDS=...`。

### 1.5 运行豆瓣 Spark 分析 executor=2

```bash
kubectl delete sparkapplication douban-analysis-2exec -n default --ignore-not-found
kubectl apply -f spark/douban-sparkapplication-2exec.yaml
kubectl get sparkapplication -n default -w
```

完成后：

```bash
kubectl logs -n default douban-analysis-2exec-driver | tee douban-2exec.log
grep "TOTAL_SECONDS" douban-2exec.log
```

截图：

- SparkApplication Completed。
- `TOTAL_SECONDS=...`。

## 2. 监控系统附加题

如果老师给了离线 kube-prometheus-stack Chart，优先使用离线包；否则用公网 Helm 仓库：

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts || true
helm repo update
helm upgrade --install cloud-monitor prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace \
  -f monitoring/kube-prometheus-stack-values.yaml
```

等待：

```bash
kubectl -n monitoring get pods -o wide
kubectl -n monitoring get svc
```

截图：

- monitoring 命名空间主要 Pod Running。
- Grafana Service 的 EXTERNAL-IP。
- Grafana Dashboard：节点 CPU 利用率折线图。
- Grafana Dashboard：各 Pod 内存使用柱状图。

登录 Grafana：

- 用户名：`admin`
- 密码：`cloud-course-2026`

## 3. CI/CD 附加题

### 3.1 GitHub 仓库 Secrets

在 GitHub 仓库 Settings -> Secrets and variables -> Actions 中添加：

- `SWR_USERNAME`
- `SWR_PASSWORD`
- `KUBE_CONFIG_DATA`

`KUBE_CONFIG_DATA` 在 CloudShell 或本地生成：

```bash
base64 -w 0 ~/.kube/config
```

### 3.2 触发流水线

推送代码到 `main`，或在 Actions 页面手动运行 `Build Push And Deploy To Huawei CCE`。

截图：

- GitHub Actions 所有步骤 Passed。
- `Push images` 步骤日志。
- `Verify deployed images` 步骤展示 backend/frontend 镜像 Tag 为 commit hash。
- CloudShell 执行：

```bash
kubectl -n cloud-course get deployment backend frontend \
  -o custom-columns=NAME:.metadata.name,IMAGE:.spec.template.spec.containers[0].image
```

截图：Deployment 镜像 Tag 已更新。

## 4. 前沿专题 C-2：K3s + MQTT 云边协同

### 4.1 本地构建并推送 MQTT 镜像

本地 PowerShell：

```powershell
$Registry="swr.cn-east-3.myhuaweicloud.com"
$Org="cloud-swjtu"
docker build --provenance=false -t "$Registry/$Org/mqtt-collector:v1" -f edge_mqtt/Dockerfile.collector .
docker build --provenance=false -t "$Registry/$Org/mqtt-publisher:v1" -f edge_mqtt/Dockerfile.publisher .
docker push "$Registry/$Org/mqtt-collector:v1"
docker push "$Registry/$Org/mqtt-publisher:v1"
```

截图：SWR 中 `mqtt-collector:v1` 与 `mqtt-publisher:v1`。

### 4.2 云端部署 MQTT Broker 和 Collector

CloudShell：

```bash
kubectl apply -f edge_mqtt/k8s-cloud-mqtt.yaml
kubectl -n cloud-course get pods -l 'app in (mqtt-broker,mqtt-collector)' -o wide
kubectl -n cloud-course get svc mqtt-broker
```

记录 `mqtt-broker` 的公网 EXTERNAL-IP，下面用 `<MQTT_ELB_IP>` 替换。

截图：

- `mqtt-broker` 和 `mqtt-collector` Running。
- `mqtt-broker` Service 公网 IP。

### 4.3 K3s 边缘侧发布传感器数据

在本地 K3s 节点或边缘虚拟机上，把 `edge_mqtt/k3s-edge-publisher-job.yaml` 中 `<MQTT_ELB_IP>` 替换为上一步 IP，然后执行：

```bash
kubectl apply -f edge_mqtt/k3s-edge-publisher-job.yaml
kubectl get pod -l job-name=edge-sensor-publisher -o wide
kubectl logs -l job-name=edge-sensor-publisher
```

截图：

- 边缘 Job Completed。
- Publisher 日志中连续 `published topic=edge/sensor/temperature`。

### 4.4 云端 Redis 验证数据入库

CloudShell：

```bash
kubectl -n cloud-course logs deployment/mqtt-collector --tail=50
REDIS_POD=$(kubectl -n cloud-course get pod -l app=redis -o jsonpath='{.items[0].metadata.name}')
kubectl -n cloud-course exec "$REDIS_POD" -- redis-cli -a cloud-course-2026 LLEN edge:mqtt:events
kubectl -n cloud-course exec "$REDIS_POD" -- redis-cli -a cloud-course-2026 LRANGE edge:mqtt:events 0 2
```

截图：

- Collector 日志 showing `stored redis_key=edge:mqtt:events`。
- Redis `LLEN` 大于 0。
- Redis `LRANGE` 显示传感器 JSON 数据。
