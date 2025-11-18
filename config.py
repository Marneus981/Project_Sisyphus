import json
import logging
import subprocess
settings_file = r'settings\json\settings.json'
debug_file = r'settings\json\debug.json'
payloads_file = r'settings\json\payloads.json'
print = logging.info
class Config:
    def __init__(self):
        self._debug = {}
        self._settings = {}
        self._payloads = {}
        self.LOAD

    def load_configuration(self):
        #load dictionaries _settings and _debug from settings.json and debug.json
        try:
            subprocess.run(['python', 'export_py_to_json.py', 'debug'])
            subprocess.run(['python', 'export_py_to_json.py', 'config'])
            subprocess.run(['python', 'export_py_to_json.py', 'payloads'])
            with open(debug_file, 'r', encoding='utf-8') as f:
                self._debug = json.load(f)
            with open(settings_file, 'r', encoding='utf-8') as f:
                self._settings = json.load(f)
            with open(payloads_file, 'r', encoding='utf-8') as f:
                self._payloads = json.load(f)
            for key in self._payloads:
                self._payloads[key]["payload_in"]["model"] = self._settings['PAYLOADS']["DEFAULT_MODEL"]
                self._payloads[key]["ollama_url"] = self._settings['PAYLOADS']["DEFAULT_URL"]
                self._payloads[key]["payload_in"]["temperature"] = self._settings['MODELS']["TEMPERATURE"]
        except Exception as e:
            print(f"[ERROR]Error loading configuration: {e}")

    @property
    def LOAD(self):
        self.load_configuration()
        return 
    @property
    def DEBUG(self):
        return self._debug
    @property
    def CONFIG(self):
        return self._settings
    @property
    def PAYLOADS(self):
        return self._payloads
config = Config()

