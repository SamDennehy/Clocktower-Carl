import os
from pathlib import Path

LOG_FILE = Path(os.environ.get("CLOCKTOWER_LOG_FILE", Path(__file__).resolve().parent / "data" / "clocktower_logs.txt"))
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logs = []


def _read_file_logs():
    if not LOG_FILE.exists():
        return []

    with LOG_FILE.open("r", encoding="utf-8") as log_file:
        return [line.rstrip("\n") for line in log_file if line.strip()]


def add_log(message):
    message = str(message)
    global logs
    logs = _read_file_logs()
    logs.append(message)

    with LOG_FILE.open("a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")
        log_file.flush()

    print(message)


def get_logs():
    global logs
    logs = _read_file_logs()
    return logs