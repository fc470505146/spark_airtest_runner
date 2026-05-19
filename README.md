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

### 1. 准备环境

本项目面向 Windows + 雷电模拟器。运行前需要准备：

- Python 3.11 或兼容版本。
- 雷电模拟器，并确认 `ldconsole.exe` 路径可用。
- 已接入 Poco SDK 的 Spark Android APK。
- APK 包名，例如 `com.fc470.spark`。

创建虚拟环境并安装依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. 创建本机配置

复制配置模板：

```powershell
Copy-Item configs\spark.example.yaml configs\spark.local.yaml
```

按本机环境修改 `configs/spark.local.yaml`：

```yaml
ldconsole: C:\leidian\LDPlayer9\ldconsole.exe
apk: C:\Users\fc470\projects\spark_builds\android\spark-poco-test.apk
package: com.fc470.spark
concurrency: 1
restart_app_per_case: true

instances:
  - name: spark_airtest_720x1280
    resolution: 720,1280,320
    cpu: 2
    memory: 2048

cases:
  - cases\spark\smoke_game_ui.air
  - cases\spark\pause_menu.air
  - cases\spark\touch_mode.air
  - cases\spark\hud_visibility.air
```

`configs/spark.local.yaml` 是本机配置，默认被 `.gitignore` 忽略。公开仓库只提交 `configs/spark.example.yaml`。

### 3. 运行用例

执行默认配置：

```powershell
.\.venv\Scripts\python.exe run.py --config configs\spark.local.yaml
```

调试时保留模拟器：

```powershell
.\.venv\Scripts\python.exe run.py --config configs\spark.local.yaml --keep-running
```

如果不传 `--config`，默认读取 `configs/spark.local.yaml`：

```powershell
.\.venv\Scripts\python.exe run.py
```

### 4. 查看报告

每次运行会在 `runs/<时间戳>/` 下生成一轮结果：

```text
runs/<时间戳>/
  index.html                         总览报告
  summary.json                       机器可读汇总
  <instance>/reports/<case>.html     Airtest 单用例报告
  <instance>/logs/<case>/            Airtest 日志与截图
```

优先打开 `runs/<时间戳>/index.html` 看整体结果。总览表里同一实例的多条用例会合并显示，方便观察实例维度的执行情况。

## 目录

```text
configs/        本机/项目配置
runner/         雷电、ADB、Airtest 调度代码
cases/spark/    Spark 项目的 Airtest/Poco 用例
runs/           运行日志与 HTML 报告，默认不提交
```

## 配置要点

配置文件使用 YAML 格式：

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

字段说明：

- `ldconsole`：雷电模拟器的 `ldconsole.exe` 路径。
- `apk`：要安装并测试的 Android APK 路径。
- `package`：Android 包名。runner 会用它停止 App、确认安装状态，并通过 ADB 查询启动 Activity。
- `concurrency`：实例级并发数。建议先用 `1` 跑稳定后再提高。
- `restart_app_per_case`：是否在每个 case 执行前 `force-stop` 并重新启动游戏，默认建议保持 `true`。
- `instances`：雷电实例矩阵。`name` 是雷电实例名，`resolution` 是 `宽,高,dpi`。
- `cases`：要执行的 `.air` 用例目录列表，按配置顺序执行。

默认执行模型是实例级并发、实例内串行。每个 case 执行前会 `force-stop` 后重新启动游戏，保证 case 之间状态隔离。

`package` 需要配置，用于安装后确认目标 App、停止 App 和查询启动入口。启动 `activity` 不需要配置，runner 会在 APK 安装后通过 ADB 从设备 PackageManager 查询：

```powershell
adb shell cmd package resolve-activity --brief com.fc470.spark
```

查询结果里的 `package/activity` 会用于显式启动游戏。

## 常用操作

### 新增用例

在 `cases/spark/` 下新增一个 `.air` 目录，并把对应路径加入 `configs/spark.local.yaml` 的 `cases`：

```yaml
cases:
  - cases\spark\smoke_game_ui.air
  - cases\spark\new_case.air
```

### 暂时跳过用例

YAML 支持注释，可以直接在本机配置里注释掉某个 case：

```yaml
cases:
  - cases\spark\smoke_game_ui.air
  # 暂时跳过：等待补稳定断言
  # - cases\spark\touch_mode.air
```

### 增加实例

在 `instances` 中增加实例配置，再按机器性能调整 `concurrency`：

```yaml
concurrency: 2

instances:
  - name: spark_airtest_720x1280
    resolution: 720,1280,320
    cpu: 2
    memory: 2048
  - name: spark_airtest_1080x1920
    resolution: 1080,1920,420
    cpu: 2
    memory: 2048
```

runner 会按实例名创建或复用雷电实例，并在每轮开始时安装 APK。

## 常见问题

### 为什么还会输出 `summary.json`？

YAML 只用于人工维护输入配置。`summary.json` 是机器产物，更适合被脚本、CI 或后续平台读取，所以输出端保持 JSON。

### 为什么不配置 Activity？

Activity 容易随 Unity 或 Android 打包设置变化。runner 只要求配置稳定的 `package`，安装 APK 后通过 ADB 查询启动入口，减少手工配置项。

### 运行失败先看哪里？

先打开本轮 `index.html`，看失败 case 的 `阶段` 和 `错误`。再进入对应的 Airtest 单用例报告查看截图、断言步骤和 traceback。
