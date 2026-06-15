# 云计算技术课程设计

本仓库为《云计算》课程设计提交仓库，课程代码 `SCAI004712`。

- 班级：计算机2023-02班
- 组员：吉昌兆（20233112439）、张志峰（2023112441）
- 分工比例：吉昌兆 50%，张志峰 50%
- 方向选择：方向 A - Spark 大数据分析
- 云平台：华为云 CCE，Region 为华东-上海一（`cn-east-3`）
- 最终报告：[cloud_course_design_report.pdf](cloud_course_design_report.pdf)

## 项目内容

本课程设计包含两部分主任务和三项附加题：

1. 云计算平台搭建：完成 Flask 后端、Redis 数据库、Nginx 前端的容器化、本地联调、SWR 镜像推送、CCE 部署、LoadBalancer 暴露、PVC 持久化、ConfigMap Volume 挂载和 HPA 验证。
2. Spark 大数据分析：基于豆瓣电影数据集完成 PySpark 数据清洗、Spark SQL 统计查询、性能对比和 Amdahl 定律分析。
3. 附加题：完成监控系统说明与验证、GitHub Actions 到华为云 SWR/CCE 的 CI/CD 流水线、K3s + MQTT 边缘计算模拟链路。

## 目录说明

```text
app/
  backend/                 Flask 后端 API 与 Dockerfile.backend
  frontend/                Nginx 前端页面与 Dockerfile.frontend
k8s/                       CCE 核心资源 YAML
spark/                     PySpark 作业、SparkApplication 与 Spark 镜像 Dockerfile
analysis/                  本地 Pandas 复现实验脚本
edge_mqtt/                 K3s + MQTT 边缘计算附加题代码与 YAML
monitoring/                Prometheus/Grafana 监控附加题配置说明
scripts/                   本地构建、推送、部署和验收脚本
.github/workflows/         GitHub Actions CI/CD 流水线
outputs/                   数据分析输出结果和图表
cloud_course_design_report.pdf   最终课程设计报告
```

## 本地联调

```bash
docker compose up --build
curl http://localhost:5000/api/ping
curl http://localhost:8080/api/visit
```

后端 `/api/ping` 用于健康检查，`/api/visit` 用于验证前后端链路和 Redis 写入。

## 镜像构建与推送

仓库内脚本默认使用华为云 SWR：

```powershell
$env:SWR_REGION="cn-east-3"
$env:SWR_ORG="cloud-swjtu"
$env:SWR_REGISTRY="swr.cn-east-3.myhuaweicloud.com"
$env:IMAGE_TAG="v1"
$env:SWR_USERNAME="cn-east-3@<AK>"
$env:SWR_PASSWORD="<SWR temporary login token>"

powershell -NoProfile -ExecutionPolicy Bypass -File scripts\01-build-images.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\02-login-push-swr.ps1
```

如果 Docker BuildKit 推送到 SWR 时出现 manifest 解析问题，可在构建命令中使用 `--provenance=false`，脚本中已按该方式处理。

## CCE 部署

在华为云 CCE 控制台配置集群并准备 kubeconfig 后，可按顺序部署：

```bash
kubectl apply -f k8s/
kubectl -n cloud-course get pods -o wide
kubectl -n cloud-course get svc -o wide
kubectl -n cloud-course get pvc
kubectl -n cloud-course get hpa
```

核心验收点：

- Worker 节点 Ready，Kubernetes 版本满足任务书要求。
- `backend-svc` 通过公网 ELB 访问 `/api/ping` 返回 `status=ok`。
- `redis-data-pvc` 处于 `Bound`，删除 Redis Pod 后数据仍可读取。
- Nginx 配置通过 ConfigMap Volume 挂载。
- HPA 已创建，并在报告中记录扩缩容验证与 Metrics API 排查过程。

## Spark 大数据分析

Spark 作业相关文件位于 `spark/`：

- `Dockerfile.pyspark`：构建包含 `wordcount.py` 和 `douban_spark_analysis.py` 的 PySpark 镜像。
- `wordcount.py`：Spark WordCount 示例作业。
- `douban_spark_analysis.py`：豆瓣电影数据清洗、统计查询和性能记录作业。
- `sparkapplication-*.yaml`：Spark Operator 提交模板。

本地复现实验脚本位于 `analysis/douban_local_analysis.py`，输出结果位于 `outputs/`。

## CI/CD

GitHub Actions 工作流位于 `.github/workflows/huawei-swr-cce.yml`，实现：

1. 拉取代码；
2. 构建 backend、frontend、pyspark 镜像；
3. 登录华为云 SWR 并推送镜像；
4. 通过自托管 Runner 在 CCE 集群内执行 `kubectl set image` 和 `rollout status`。

工作流依赖 GitHub Actions Secrets：

- `SWR_USERNAME`
- `SWR_PASSWORD`

真实 SWR 登录口令、kubeconfig、集群 token 不应提交到仓库。

## 提交说明

最终提交材料以 `cloud_course_design_report.pdf` 为准，代码仓库用于支撑报告中的构建、部署、Spark 分析和附加题实现。报告中的云端验收截图已经嵌入 PDF，仓库中不提交真实云账号密钥或临时登录口令。
