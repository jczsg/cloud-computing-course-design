# 《云计算》课程设计报告

本仓库与最终报告 PDF 保持一致，用于提交《云计算》课程设计的代码、配置、实验结果与报告材料。

- 设计题目：云计算技术课程设计实验报告
- 组号：课程设计小组
- 成员信息：吉昌兆（20233112439）、张志峰（2023112441）
- 班级：计算机2023-02 班
- 指导教师：戴朋林
- 完成日期：2026.6.15
- 最终报告：[cloud_course_design_report.pdf](cloud_course_design_report.pdf)

## 课程设计任务书

本课程设计围绕云计算平台搭建与大数据分析展开，主要包括应用容器化、华为云 CCE 集群部署、Kubernetes 服务暴露、Redis 持久化、ConfigMap 挂载、HPA 弹性伸缩、Spark 大数据分析，以及监控、CI/CD、边缘计算等附加内容。报告完整呈现实验过程、关键截图、问题排查与结果分析。

## 报告目录

报告 PDF 的正文结构如下：

```text
一、华为云环境信息
二、第一部分实验记录：云计算平台搭建
  2.1 任务1：应用容器化
    2.1.1 任务目标
    2.1.2 关键截图
    2.1.3 问题与解决方案
  2.2 任务2：CCE 集群搭建
    2.2.1 任务目标
    2.2.2 关键截图
  2.3 任务3：应用部署
    2.3.1 任务目标
  2.4 任务4：持久化存储验证
    2.4.1 任务目标
    2.4.2 关键截图
  2.5 任务5：ConfigMap Volume 挂载
    2.5.1 任务目标
    2.5.2 关键截图
  2.6 任务6：HPA 弹性伸缩
    2.6.1 任务目标
    2.6.2 关键截图
三、第二部分实验记录：Spark 大数据分析
  3.1 A-0 环境部署
  3.2 A-1 数据清洗
  3.3 A-2 Spark SQL 统计分析
  3.4 A-3 性能对比与 Amdahl 分析
  3.5 问题与解决方案汇总
四、附加题
  4.1 附加题1：监控系统
  4.2 附加题2：CI/CD 流水线
  4.3 附加题3：前沿专题 C-2 K3s + MQTT 边缘计算模拟
五、任务书逐项对照检查
六、总结与收获
七、附录
  7.1 提交前截图清单
```

## 华为云环境信息

报告中的实验环境如下：

- 华为云 Region：华东-上海一（`cn-east-3`）
- CCE 集群名称：`cloud`
- CCE 集群类型：CCE Standard
- Kubernetes 版本：`v1.35.3`
- Worker 节点：4 个 Ready 节点
- 节点系统：Huawei Cloud EulerOS 2.0
- 容器运行时：containerd
- SWR 组织：`cloud-swjtu`
- 镜像范围：`backend`、`frontend`、`pyspark`、`spark-operator-controller`、MQTT 相关镜像

## 仓库与报告对应关系

```text
app/backend/                     对应 2.1 应用容器化中的 Flask 后端
app/frontend/                    对应 2.1 应用容器化中的 Nginx 前端
docker-compose.yml               对应本地联调验证
k8s/                             对应 2.2-2.6 CCE 部署、服务暴露、PVC、ConfigMap、HPA
spark/                           对应第三章 Spark 大数据分析与 Spark 镜像构建
analysis/                        对应 Pandas 本地复现实验与性能对比
outputs/                         对应 Spark/Pandas 统计结果与图表
monitoring/                      对应 4.1 监控系统附加题
.github/workflows/               对应 4.2 CI/CD 流水线附加题
edge_mqtt/                       对应 4.3 K3s + MQTT 边缘计算模拟附加题
cloud_course_design_report.pdf   最终报告 PDF，与提交版保持一致
```

## 团队成员分工

| 成员 | 分工 |
| --- | --- |
| 吉昌兆（20233112439） | 环境搭建、应用部署、实验验证、相关实验内容整理与报告撰写。 |
| 张志峰（2023112441） | 结构设计、正文整合、排版整理、实验过程记录、结果复核与材料汇总。 |

## 提交说明

最终提交以 [cloud_course_design_report.pdf](cloud_course_design_report.pdf) 为准。仓库中的代码和配置用于支撑报告中的实验过程、截图证据、Spark 分析和附加题实现。真实华为云登录口令、SWR 临时 token、kubeconfig 和集群密钥不提交到仓库。
