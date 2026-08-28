import json
import os
import time
from typing import List, Dict, Any

class HistoryStore:
    def __init__(self):
        self.filepath = os.path.join(os.path.expanduser("~"), ".connection_diagnostics_history.json")

    def save_session(self, session: Dict[str, Any], max_retention: int = 50):
        history = self.get_all()
        history.insert(0, session)
        history = history[:max_retention]
        try:
            with open(self.filepath, "w") as f:
                json.dump(history, f, indent=4)
        except Exception:
            pass

    def get_all(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.filepath):
            return []
        try:
            with open(self.filepath, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception:
            pass
        return []

    def clear(self):
        try:
            if os.path.exists(self.filepath):
                os.remove(self.filepath)
        except Exception:
            pass
