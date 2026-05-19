from pathlib import Path

from runner.command import run_cmd


class AirtestCliError(RuntimeError):
    def __init__(self, stage, message):
        super().__init__(message)
        self.stage = stage


class AirtestCli:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.airtest_exe = self.project_root / ".venv" / "Scripts" / "airtest.exe"
        if not self.airtest_exe.exists():
            self.airtest_exe = self.project_root / ".venv-airtest" / "Scripts" / "airtest.exe"
        if not self.airtest_exe.exists():
            raise FileNotFoundError("Missing Airtest CLI. Install dependencies into .venv first.")

    def run_case(self, case_path, serial, log_dir, report_file):
        case_path = Path(case_path)
        log_dir = Path(log_dir)
        report_file = Path(report_file)
        log_dir.mkdir(parents=True, exist_ok=True)
        report_file.parent.mkdir(parents=True, exist_ok=True)

        run_result = run_cmd(
            [
                self.airtest_exe,
                "run",
                case_path,
                "--device",
                f"Android:///{serial}",
                "--log",
                log_dir,
            ],
            cwd=self.project_root,
            timeout=300,
            check=False,
        )

        report_result = run_cmd(
            [
                self.airtest_exe,
                "report",
                case_path,
                "--log_root",
                log_dir,
                "--outfile",
                report_file,
                "--lang",
                "zh",
            ],
            cwd=self.project_root,
            timeout=120,
            check=False,
        )

        if run_result.returncode != 0:
            raise AirtestCliError("airtest_run", f"Airtest run failed with exit code {run_result.returncode}: {case_path}")
        if report_result.returncode != 0:
            raise AirtestCliError(
                "airtest_report",
                f"Airtest report failed with exit code {report_result.returncode}: {case_path}",
            )

        print(f"Airtest report: {report_file}")
        return report_file
