# Spark Airtest Runner

面向 Spark Unity Android 包的 Airtest/Poco 自动化测试执行器。

它负责把端到端测试环境拉起来：

```text
雷电实例创建/复用
-> 设置分辨率
-> 启动模拟器
-> 等待 ADB
-> 安装 APK
-> 每个 case 前重启游戏
-> 等待 Unity Poco 5001 端口
-> 顺序执行实例内 Airtest 用例
-> 生成实例分层 HTML 报告
-> 生成 summary.json 和总览 index.html
```

## 快速开始

创建虚拟环境并安装依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

复制配置模板：

```powershell
Copy-Item configs\spark.example.yaml configs\spark.local.yaml
```

按本机路径修改 `configs/spark.local.yaml`，然后运行：

```powershell
.\.venv\Scripts\python.exe run.py --config configs\spark.local.yaml
```

调试时保留模拟器：

```powershell
.\.venv\Scripts\python.exe run.py --config configs\spark.local.yaml --keep-running
```

## 目录

```text
configs/        本机/项目配置
runner/         雷电、ADB、Airtest 调度代码
cases/spark/    Spark 项目的 Airtest/Poco 用例
runs/           运行日志与 HTML 报告，默认不提交
```

## 配置要点

多实例版本只支持 `instances`，不再兼容旧版 `instance`：

```yaml
package: com.fc470.spark
concurrency: 1
restart_app_per_case: true

instances:
  - name: spark_airtest_720x1280
    resolution: 720,1280,320
    cpu: 2
    memory: 2048
```

默认执行模型是实例级并发、实例内串行。每个 case 执行前会 `force-stop` 后重新启动游戏，保证 case 之间状态隔离。

`package` 需要配置，用于安装后确认目标 App、停止 App 和查询启动入口。启动 `activity` 不需要配置，runner 会在 APK 安装后通过 ADB 从设备 PackageManager 查询：

```powershell
adb shell cmd package resolve-activity --brief com.fc470.spark
```

查询结果里的 `package/activity` 会用于显式启动游戏。
