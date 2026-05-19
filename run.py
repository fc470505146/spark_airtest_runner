import argparse
import datetime as dt
from pathlib import Path

import yaml

from runner.airtest_cli import AirtestCli
from runner.ldplayer import LDPlayer
from runner.matrix import run_matrix
from runner.report import write_index_html, write_summary


PROJECT_ROOT = Path(__file__).resolve().parent


def load_config(path):
    config_path = Path(path)
    if not config_path.is_absolute():
        config_path = PROJECT_ROOT / config_path
    if config_path.suffix.lower() not in (".yaml", ".yml"):
        raise ValueError("Config file must be a YAML file with .yaml or .yml suffix.")
    with config_path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
    if not isinstance(config, dict):
        raise ValueError("Config file must contain a YAML object.")
    return config


def resolve_path(value):
    path = Path(value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def parse_args():
    parser = argparse.ArgumentParser(description="Run Airtest cases on LDPlayer.")
    parser.add_argument("--config", default="configs/spark.local.yaml")
    parser.add_argument("--keep-running", action="store_true")
    return parser.parse_args()


def require_keys(config, keys):
    missing = [key for key in keys if key not in config or config[key] in (None, "")]
    if missing:
        raise ValueError(f"Missing required config keys: {', '.join(missing)}")


def validate_config(config):
    if "instance" in config:
        raise ValueError("Config key 'instance' is no longer supported. Use 'instances' instead.")

    require_keys(config, ["ldconsole", "apk", "package", "instances", "cases"])

    ldconsole = resolve_path(config["ldconsole"])
    apk = resolve_path(config["apk"])
    if not ldconsole.exists():
        raise FileNotFoundError(ldconsole)
    if not apk.exists():
        raise FileNotFoundError(apk)

    instances = config["instances"]
    if not isinstance(instances, list) or not instances:
        raise ValueError("Config key 'instances' must be a non-empty list.")

    instance_names = []
    for index, instance in enumerate(instances):
        if not isinstance(instance, dict):
            raise ValueError(f"instances[{index}] must be an object.")
        require_keys(instance, ["name", "resolution"])
        instance_names.append(instance["name"])

    if len(instance_names) != len(set(instance_names)):
        raise ValueError("Instance names must be unique.")

    cases = config["cases"]
    if not isinstance(cases, list) or not cases:
        raise ValueError("Config key 'cases' must be a non-empty list.")

    resolved_cases = []
    for case in cases:
        case_path = resolve_path(case)
        if not case_path.exists():
            raise FileNotFoundError(case_path)
        resolved_cases.append(case_path)

    concurrency = int(config.get("concurrency", 1))
    if concurrency < 1:
        raise ValueError("Config key 'concurrency' must be greater than or equal to 1.")

    validated = dict(config)
    validated["ldconsole"] = ldconsole
    validated["apk"] = apk
    validated["cases"] = resolved_cases
    validated["concurrency"] = concurrency
    validated["restart_app_per_case"] = bool(config.get("restart_app_per_case", True))
    return validated


def main():
    args = parse_args()
    config = validate_config(load_config(args.config))

    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    started_at = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run_dir = PROJECT_ROOT / "runs" / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    ldplayer = LDPlayer(config["ldconsole"], PROJECT_ROOT)
    airtest = AirtestCli(PROJECT_ROOT)

    results = run_matrix(config, run_dir, ldplayer, airtest, keep_running=args.keep_running)
    summary_path = write_summary(run_dir, started_at=started_at, concurrency=config["concurrency"], results=results)
    index_path = write_index_html(run_dir, started_at=started_at, concurrency=config["concurrency"], results=results)
    print(f"Summary: {summary_path}")
    print(f"Index report: {index_path}")


if __name__ == "__main__":
    main()
