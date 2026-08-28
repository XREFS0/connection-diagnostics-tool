import json
import os

class Settings:
    def __init__(self):
        self.filepath = os.path.join(os.path.expanduser("~"), ".connection_diagnostics_settings.json")
        self.defaults = {
            "timeout": 5.0,
            "ping_count": 4,
            "default_test_host": "8.8.8.8",
            "http_test_url": "https://www.google.com",
            "tcp_test_port": 443,
            "history_retention": 50,
            "start_automatically": False,
            "theme": "Dark"
        }
        self.data = self.defaults.copy()
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    loaded = json.load(f)
                    for key, val in self.defaults.items():
                        self.data[key] = loaded.get(key, val)
            except Exception:
                self.data = self.defaults.copy()

    def save(self):
        try:
            with open(self.filepath, "w") as f:
                json.dump(self.data, f, indent=4)
        except Exception:
            pass

    def get(self, key):
        return self.data.get(key, self.defaults.get(key))

    def set(self, key, value):
        self.data[key] = value
        self.save()
