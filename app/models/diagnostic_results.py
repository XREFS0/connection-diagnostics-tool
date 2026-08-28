from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class DiagnosticStepResult:
    name: str
    status: str
    duration_ms: float = 0.0
    result: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    error: str = ""
