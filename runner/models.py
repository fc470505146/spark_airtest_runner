from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class CaseResult:
    instance: str
    case: Optional[str]
    status: str
    stage: str
    report: Optional[str] = None
    log_dir: Optional[str] = None
    duration_seconds: Optional[float] = None
    error: Optional[str] = None

    def to_dict(self):
        return {key: value for key, value in asdict(self).items() if value is not None}
