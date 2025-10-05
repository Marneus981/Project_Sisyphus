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
        "RETRIES": 2
    },
    "PRUNING": {
        #ratio, partial_ratio, toekn_sort_ratio,partial_token_sort_ratio, token_set_ratio
        "DISTANCE_ALGO_KEY": "token_set_ratio", 
        "DISTANCE_ALGO_DESC": "token_set_ratio", 
        "BASE_PRUNE": 5,
        "SECTION_MIN": 1,
        "EXP_H_WEIGHTS": {
            "EXP": 1.0,
            "DESC":1.0,
            "PROG":1.5,
            "TECH":1.0,
            "SOFT":0.5
        },
        "SKILL_RATING_TYPE": "max", #or sum
        "NO_COURSES":5,
        "NO_SKILLS":{
            "TOTAL":12,
            "PROG": 3,
            "TECH": 5,
            "SOFT":4
        },
        "CUSTOM_SKILLS": {
            "PROG": False,
            "TECH":False,
            "SOFT": True
        },
        "PREFS":{
            "V": [
            ],
            "W":[
            ],
            "P":[
                "Project Sisyphus",
                "MAPPA C++ Geographical Information System"
            ],
            "SKILLS":[
            ],
            "COURSES":[

            ]
        },
        "COURSES_GRPS":
        {
        }
    }
}