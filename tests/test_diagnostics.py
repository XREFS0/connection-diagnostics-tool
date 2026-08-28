from app.config.settings import Settings
import os

def test_settings_load_save():
    s = Settings()
    s.filepath = s.filepath + ".test"
    if os.path.exists(s.filepath):
        os.remove(s.filepath)
        
    s.set("default_test_host", "1.1.1.1")
    assert s.get("default_test_host") == "1.1.1.1"
    
    s2 = Settings()
    s2.filepath = s.filepath
    s2.load()
    assert s2.get("default_test_host") == "1.1.1.1"
    
    if os.path.exists(s.filepath):
        os.remove(s.filepath)
