DEBUG = {
    "TIME_LOGGING": True,
    "TOKEN_LOGGING": False,
    "ERROR_LOGGING": True,
    "WARNING_LOGGING": True,
    "INFO_LOGGING": True
}
CONFIG = {
    "WINDOWS": 4,
    "SUMMARY_MODE": "batch", #Options: "single", "batch" or "parallel"
    "SUMMARY_REQUESTS": 2,
    "NOTIFICATIONS": {
        "ENABLED": True,
        "WINDOWS": True,
        "SOUND": True
    },
    "MODELS": {
        "TEMPERATURE": 0.8,
        "RETRIES": 1
    }
}