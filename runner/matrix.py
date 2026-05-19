import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from runner.models import CaseResult


def _relative(path, root):
    return str(Path(path).relative_to(root))


def _case_name(case_path):
    return Path(case_path).stem


def _failure_result(instance_name, case_path, stage, error, started_at, run_dir, log_dir=None, report_file=None):
    return CaseResult(
        instance=instance_name,
        case=_case_name(case_path) if case_path else None,
        status="failed",
        stage=stage,
        report=_relative(report_file, run_dir) if report_file else None,
        log_dir=_relative(log_dir, run_dir) if log_dir else None,
        duration_seconds=round(time.perf_counter() - started_at, 3),
        error=str(error),
    )


def run_instance_suite(instance, cases, config, run_dir, ldplayer, airtest, keep_running=False):
    instance_name = instance["name"]
    package_name = config["package"]
    restart_app_per_case = config.get("restart_app_per_case", True)
    instance_run_dir = Path(run_dir) / instance_name

    stage = "ensure_instance"
    started_at = time.perf_counter()
    try:
        ldplayer.ensure_instance(instance)
        stage = "launch_instance"
        ldplayer.launch(instance_name)
        stage = "wait_instance_running"
        ldplayer.wait_instance_running(instance_name)
        stage = "sort_windows"
        ldplayer.sort_windows()
        stage = "wait_adb_ready"
        serial = ldplayer.wait_adb_ready(instance_name)
        print(f"{instance_name} ADB serial: {serial}")
        stage = "install_app"
        ldplayer.install_app(instance_name, config["apk"])
        stage = "wait_package_installed"
        ldplayer.wait_package_installed(instance_name, package_name)
        stage = "resolve_launch_activity"
        activity = ldplayer.resolve_launch_activity(instance_name, package_name)
        print(f"{instance_name} launch activity: {activity}")
    except Exception as error:
        return [_failure_result(instance_name, None, stage, error, started_at, run_dir)]

    results = []
    try:
        for case in cases:
            case_path = Path(case)
            case_started_at = time.perf_counter()
            case_name = _case_name(case_path)
            log_dir = instance_run_dir / "logs" / case_name
            report_file = instance_run_dir / "reports" / f"{case_name}.html"
            stage = "restart_app" if restart_app_per_case else "start_activity"
            try:
                if restart_app_per_case:
                    ldplayer.force_stop_app(instance_name, package_name)
                    ldplayer.wait_poco_stopped(instance_name)

                stage = "start_activity"
                ldplayer.run_app(instance_name, package_name, activity)
                stage = "wait_poco_ready"
                ldplayer.wait_poco_ready(instance_name)
                stage = "airtest_run"
                airtest.run_case(case_path, serial, log_dir, report_file)

                results.append(
                    CaseResult(
                        instance=instance_name,
                        case=case_name,
                        status="passed",
                        stage="completed",
                        report=_relative(report_file, run_dir),
                        log_dir=_relative(log_dir, run_dir),
                        duration_seconds=round(time.perf_counter() - case_started_at, 3),
                    )
                )
            except Exception as error:
                failed_stage = getattr(error, "stage", stage)
                results.append(
                    _failure_result(
                        instance_name,
                        case_path,
                        failed_stage,
                        error,
                        case_started_at,
                        run_dir,
                        log_dir,
                        report_file,
                    )
                )
    finally:
        if keep_running:
            print(f"Keep LDPlayer running: {instance_name}")
        else:
            ldplayer.quit(instance_name)

    return results


def run_matrix(config, run_dir, ldplayer, airtest, keep_running=False):
    instances = config["instances"]
    cases = config["cases"]
    concurrency = config.get("concurrency", 1)

    if concurrency == 1:
        results = []
        for instance in instances:
            results.extend(run_instance_suite(instance, cases, config, run_dir, ldplayer, airtest, keep_running))
        return results

    results = []
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [
            executor.submit(run_instance_suite, instance, cases, config, run_dir, ldplayer, airtest, keep_running)
            for instance in instances
        ]
        for future in as_completed(futures):
            results.extend(future.result())
    return results
