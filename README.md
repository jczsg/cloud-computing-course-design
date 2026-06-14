# 云计算技术课程设计

本目录已整理为可提交的课程设计工程包，方向选择为 **方向A：Spark 大数据分析**。

## 目录说明

- `app/backend/`：Flask 后端 API，包含 `Dockerfile.backend`。
- `app/frontend/`：Nginx 前端首页和反向代理配置，包含 `Dockerfile.frontend`。
- `docker-compose.yml`：本地联调 Flask + Redis + Nginx。
- `k8s/`：CCE 部署清单，包含 Namespace、ConfigMap、Secret、PVC、Deployment、Service、HPA。
- `spark/`：Spark Operator 示例作业、豆瓣数据分析作业和 SparkApplication YAML。
- `analysis/`：本地 Pandas 复现实验脚本。
- `outputs/`：已基于 `douban_movies.csv` 生成的统计结果和图表。
- `cloud_course_design_report.docx`：课程设计报告初稿，含截图占位和数据分析结果。

## 本地联调

```bash
docker compose up --build
curl http://localhost:5000/api/ping
curl http://localhost:8080/api/visit
```

若推送华为云 SWR 时出现 manifest 解析错误，构建镜像时添加：

```bash
docker build --provenance=false -t swr.cn-east-3.myhuaweicloud.com/cloud-course-2025212245/backend:v1 app/backend
docker build --provenance=false -t swr.cn-east-3.myhuaweicloud.com/cloud-course-2025212245/frontend:v1 app/frontend
```

## CCE 部署

部署前请按实际 Region、组织名和镜像 Tag 修改 `k8s/04-backend-deployment-service.yaml` 与
`k8s/06-frontend-deployment-service.yaml` 中的 SWR 镜像地址。

也可以直接使用 `scripts/` 下的自动化脚本，推荐流程如下：

```powershell
# 1. 检查本机 Docker/kubectl/helm/kubeconfig/SWR 环境
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\00-preflight.ps1

# 2. 构建带 SWR 地址的镜像，默认使用 cn-east-3 / cloud-course-2025212245 / v1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\01-build-images.ps1

# 2b. 可选但推荐：构建包含 wordcount.py 和 douban_spark_analysis.py 的 PySpark 镜像
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\01b-build-spark-image.ps1

# 3. 登录并推送镜像。先在当前 PowerShell 中设置 SWR 临时登录信息：
$env:SWR_REGION="cn-east-3"
$env:SWR_ORG="cloud-course-2025212245"
$env:SWR_REGISTRY="swr.cn-east-3.myhuaweicloud.com"
$env:SWR_USERNAME="cn-east-3@<AK>"
$env:SWR_PASSWORD="<SWR 控制台登录指令里的临时 token>"
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\02-login-push-swr.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\02b-push-spark-image.ps1

# 4. 从 CCE 控制台下载 kubeconfig，保存为 D:\cloud_computing\kubeconfig.yaml
# 然后部署到 CCE
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\03-deploy-cce.ps1

# 5. 自动执行 /api/ping、Redis 持久化、ConfigMap 文件、HPA 状态等验收命令
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\04-verify-cce.ps1

# 6. HPA 压测和观察
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\08-watch-hpa.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\07-hpa-loadtest.ps1
```

脚本会把关键命令输出保存到 `evidence/`，方便截图或粘到报告里。

```bash
kubectl apply -f k8s/
kubectl get pods -n cloud-course -o wide
kubectl get svc -n cloud-course
kubectl get pvc -n cloud-course
kubectl get hpa -n cloud-course
```

## Spark 作业

部署 Spark Operator 后提交示例作业：

```bash
kubectl apply -f spark/sparkapplication-wordcount.yaml
kubectl get pods -n default
```

如果教师给的是离线 Spark Operator Chart，把目录命名为 `spark-operator-chart` 后可执行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\05-spark-operator.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\06-submit-spark.ps1
```

运行豆瓣分析作业前，将 `spark/douban_spark_analysis.py` 中的 `INPUT_PATH` 和 `OUTPUT_PATH`
替换为你的 OBS `s3a://` 路径，并确认 PySpark 镜像已包含该脚本。

## 报告提交前必须补充的截图

1. `docker compose up --build` 前后端联通截图。
2. SWR 镜像列表截图，包含 `backend:v1`、`frontend:v1`。
3. `kubectl get nodes -o wide`，节点 Ready 且版本满足要求。
4. `kubectl get pods -n cloud-course -o wide`，所有 Pod Running。
5. ELB 公网 IP 访问 `/api/ping` 返回 `{"status":"ok"}`。
6. `kubectl get pvc -n cloud-course` 显示 PVC Bound。
7. Redis 写入、删除 Pod、重建后读取 `testkey` 的三张截图。
8. 前端 Pod 内 `cat /etc/nginx/conf.d/default.conf` 的截图。
9. HPA 扩容和缩容截图。
10. Spark Driver/Executor Pod 状态与查询结果截图。

## 已完成的数据结果

本地已运行 `analysis/douban_local_analysis.py`，生成：

- `outputs/missing_ratio.csv`
- `outputs/basic_stats.csv`
- `outputs/genre_top10.csv`
- `outputs/top_movies.csv`
- `outputs/yearly_trend.csv`
- `outputs/country_join_top15.csv`
- `outputs/genre_top10.png`
- `outputs/yearly_rating_trend.png`
