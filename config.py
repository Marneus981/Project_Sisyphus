import json
settings_file = r'settings\json\settings.json'
debug_file = r'settings\json\debug.json'
payloads_file = r'settings\json\payloads.json'
class Config:
    def __init__(self):
        self._debug = {}
        self._settings = {}
        self._payloads = {}

    def load_configuration(self, type='CONFIG'):
        #load dictionaries _settings and _debug from settings.json and debug.json
        try:
            if type == 'DEBUG':
                with open(debug_file, 'r', encoding='utf-8') as f:
                    self._debug = json.load(f)
            elif type == 'CONFIG':
                with open(settings_file, 'r', encoding='utf-8') as f:
                    self._settings = json.load(f)
            elif type == 'PAYLOADS':
                with open(settings_file, 'r', encoding='utf-8') as f:
                    self._settings = json.load(f)
                with open(payloads_file, 'r', encoding='utf-8') as f:
                    self._payloads = json.load(f)
                for key in self._payloads.items():
                    self._payloads[key]["payloads_in"]["model"] = self._settings['PAYLOADS']["DEFAULT_MODEL"]
                    self._payloads[key]["ollama_url"] = self._settings['PAYLOADS']["DEFAULT_URL"]
                    self._payloads[key]["payloads_in"]["temperature"] = self._settings['MODELS']["TEMPERATURE"]
        except Exception as e:
            print(f"Error loading configuration: {e}")

    @property
    def DEBUG(self):
        self.load_configuration(type='DEBUG')
        return self._debug
    @property
    def CONFIG(self):
        self.load_configuration(type='CONFIG')
        return self._settings
    @property
    def PAYLOADS(self):
        self.load_configuration(type='PAYLOADS')
        return self._payloads
config = Config()
