import threading
import time
from pathlib import Path

from runner.command import run_cmd


class LDPlayer:
    def __init__(self, console_path, project_root):
        self.console_path = Path(console_path)
        self.project_root = Path(project_root)
        self._command_lock = threading.Lock()

    def run(self, *args, timeout=120, check=True):
        with self._command_lock:
            return run_cmd([self.console_path, *args], cwd=self.project_root, timeout=timeout, check=check)

    def adb(self, name, command, *, timeout=120, check=True):
        return self.run("adb", "--name", name, "--command", command, timeout=timeout, check=check)

    def instance_exists(self, name):
        result = self.run("list2", check=False)
        for line in result.stdout.splitlines():
            columns = [column.strip() for column in line.split(",")]
            if len(columns) >= 2 and columns[1] == name:
                return True
        return False

    def ensure_instance(self, instance):
        name = instance["name"]
        if self.instance_exists(name):
            print(f"LDPlayer instance already exists: {name}")
        else:
            self.run("add", "--name", name, timeout=180, check=False)
            if not self.instance_exists(name):
                raise RuntimeError(f"Failed to create LDPlayer instance: {name}")

        self.run(
            "modify",
            "--name",
            name,
            "--resolution",
            instance["resolution"],
            "--cpu",
            str(instance.get("cpu", 2)),
            "--memory",
            str(instance.get("memory", 2048)),
            timeout=180,
        )

    def launch(self, name):
        self.run("launch", "--name", name, timeout=180)

    def quit(self, name):
        self.run("quit", "--name", name, timeout=60, check=False)

    def install_app(self, name, apk_path):
        result = self.adb(name, f"install -r {Path(apk_path)}", timeout=300)
        if "Success" not in result.stdout:
            raise RuntimeError(f"APK install did not report Success: {apk_path}")

    def run_app(self, name, package_name, activity):
        self.adb(name, f"shell am start -n {package_name}/{activity}", timeout=60)

    def resolve_launch_activity(self, name, package_name):
        result = self.adb(name, f"shell cmd package resolve-activity --brief {package_name}", timeout=60)
        lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        for line in reversed(lines):
            if "/" in line and not line.startswith("priority="):
                package, activity = line.split("/", 1)
                if package != package_name:
                    raise RuntimeError(f"Resolved activity package mismatch: {line}")
                if activity.startswith("."):
                    activity = f"{package_name}{activity}"
                return activity
        raise RuntimeError(f"Failed to resolve launch activity for package: {package_name}")

    def force_stop_app(self, name, package_name):
        self.adb(name, f"shell am force-stop {package_name}", timeout=60, check=False)

    def is_poco_ready(self, name):
        result = self.adb(name, "shell cat /proc/net/tcp", check=False)
        # 5001 decimal == 0x1389. Android /proc/net/tcp stores local port in hex.
        for line in result.stdout.splitlines():
            columns = line.split()
            if len(columns) >= 4 and columns[1].upper().endswith(":1389") and columns[3] == "0A":
                return True
        return False

    def wait_poco_stopped(self, name, timeout=20):
        def stopped():
            return not self.is_poco_ready(name)

        self.wait_until(stopped, timeout=timeout, interval=1, message="Waiting Unity Poco port 5001 to stop")

    def wait_until(self, predicate, *, timeout, interval=2, message="waiting"):
        deadline = time.time() + timeout
        while time.time() < deadline:
            value = predicate()
            if value:
                return value
            print(message)
            time.sleep(interval)
        raise TimeoutError(message)

    def wait_instance_running(self, name, timeout=90):
        def is_running():
            result = self.run("isrunning", "--name", name, check=False)
            return "running" in result.stdout.lower() or result.stdout.strip() == "1"

        self.wait_until(is_running, timeout=timeout, message=f"Waiting LDPlayer instance: {name}")

    def wait_adb_ready(self, name, timeout=120):
        def get_serial():
            result = self.adb(name, "get-state", check=False)
            if "device" in result.stdout.lower():
                serial_result = self.adb(name, "get-serialno", check=False)
                serial = serial_result.stdout.strip()
                if serial and not serial.startswith("error"):
                    return serial
            return None

        return self.wait_until(get_serial, timeout=timeout, message="Waiting emulator ADB device")

    def wait_package_installed(self, name, package_name, timeout=60):
        def installed():
            result = self.adb(name, f"shell pm list packages {package_name}", check=False)
            return package_name in result.stdout

        self.wait_until(installed, timeout=timeout, message=f"Waiting package install: {package_name}")

    def wait_poco_ready(self, name, timeout=90):
        def ready():
            return self.is_poco_ready(name)

        self.wait_until(ready, timeout=timeout, message="Waiting Unity Poco port 5001 in game")
        time.sleep(1)
