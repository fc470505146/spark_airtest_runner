import locale
import subprocess


def run_cmd(args, *, cwd, timeout=120, check=True):
    print("RUN:", " ".join(str(arg) for arg in args))
    completed = subprocess.run(
        [str(arg) for arg in args],
        cwd=str(cwd),
        text=True,
        encoding=locale.getpreferredencoding(False),
        errors="replace",
        capture_output=True,
        timeout=timeout,
    )

    stdout = completed.stdout or ""
    stderr = completed.stderr or ""
    if stdout.strip():
        print(stdout.strip())
    if stderr.strip():
        print(stderr.strip())

    if check and completed.returncode != 0:
        raise RuntimeError(f"Command failed with exit code {completed.returncode}: {args}")

    return completed
