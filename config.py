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
        "MALICIOUS_COMPLIANCE_SK":{
            "PROG":{
                "STATUS":False,
                "NO":"1"
            },
            "TECH":{
                "STATUS":False,
                "NO": "1"
            },
            "SOFT":{
                "STATUS":True,
                "NO":"all"
            },
        },
        "MALICIOUS_COMPLIANCE_COURSES":{
            "STATUS": False,
            "NO": "3"
        },
        "DISTANCE_ALGO_KEY": "token_set_ratio", 
        "DISTANCE_ALGO_DESC": "token_set_ratio",
        "DISTANCE_ALGO_PROG":  "token_set_ratio",
        "DISTANCE_ALGO_TECH":  "token_set_ratio",
        "DISTANCE_ALGO_SOFT":  "token_set_ratio",
        "DISTANCE_ALGO_COURSES": "token_set_ratio",
        "BASE_PRUNE": 5,
        "SECTION_MIN": 1,
        "EXP_H_WEIGHTS": {
            "EXP": 1.0,
            "DESC":1.0,
            "PROG":1.5,
            "TECH":1.0,
            "SOFT":0.5
        },
        "PROG_H_WEIGHT": 1.0,
        "TECH_H_WEIGHT": 1.0,
        "SOFT_H_WEIGHT": 1.0,
        "EXP_RATING_TYPE": "max", #or sum
        "PROG_RATING_TYPE": "max", #or sum
        "TECH_RATING_TYPE": "max", #or sum
        "SOFT_RATING_TYPE": "max", #or sum
        "COURSES_RATING_TYPE": "max",
        "COURSES_PRUNING_TYPE": "max",
        "NO_COURSES":"5",
        "NO_SKILLS":{
            #"TOTAL":"12",
            "PROG": "3",
            "TECH": "5",
            "SOFT":"4"
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
            "PROG":[],
            "TECH":[],
            "SOFT":[],
            "COURSES":[]

        }
    },
    "TAGS":{
        "COURSES":{
            ##Insert course tags for all your degrees
            "CIV102 Structures and Materials":[
                "civil engineering",
                "structure analysis",
                "material science"
            ],
            "ESC101 Praxis I":[
                "project management",
                "teamwork",
                "good communication",
                "documentation"
            ],
            "ESC103 Engineering Mathematics and Computation":[
                "mathematics",
                "computation",
                "math",
                "matlab"
            ],
            "ESC180 Introduction to Computer Programming":[
                "software",
                "programming",
                "c programming",
                "object oriented",
                "linux os",
                "python",
                "git"
            ],
            "MAT194 Calculus I":[
                "calculus",
                "mathematics",
                "math"
            ],
            "PHY180 Classical Mechanics":[
                "physics",
                "calculus",
                "mathematics",
                "mechanics"
            ],
            "ECE159 Fundamentals of Electric Circuits":[
                "circuits",
                "circuit analysis",
                "physics"
            ],
            "ESC102 Praxis II":[
                "project management",
                "teamwork",
                "good communication",
                "documentation"
            ],
            "ESC190 Computer Algorithms and Data Structures":[
                "software",
                "programming",
                "linux os",
                "c++",
                "object oriented",
                "data structures",
                "algorithms",
                "git"
            ],
            "MAT185 Linear Algebra":[
                "mathematics",
                "math",
                "algebra"
            ], 
            "MAT195 Calculus II":[
                "calculus",
                "mathematics",
                "math"
            ], 
            "MSE160 Molecules and Materials":[
                "physics",
                "chemestry",
                "material science"
            ], 
            "ECE212 Circuit Analysis":[
                "circuits",
                "circuit analysis",
                "physics",
                "electrical systems"
            ], 
            "ECE241 Digital Systems":[
                "digital systems",
                "cpu design"
            ], 
            "ECE244 Programming Fundamentals":[
                "software",
                "programming",
                "linux os",
                "c++",
                "object oriented",
                "data structures",
                "algorithms",
                "git"
            ], 
            "MAT290 Advanced Engineering Mathematics":[
                "calculus",
                "advanced calculus",
                "mathematics",
                "math"
            ], 
            "MAT291 Calculus III":[
                "calculus",
                "alegbra",
                "mathematics",
                "math"
            ],
            "ECE216 Signals and Systems":[
                "signals",
                "control systems"
            ], 
            "ECE221 Electric and Magnetic Fields":[
                "electric systems",
                "magnetic systems",
                "electromagnetism",
                "advanced calculus",
                "mathematics",
            ], 
            "ECE231 Introductory Electronics":[
                "circuits",
                "electronics",
                "circuit analysis",
                "physics",
                "electrical systems"
            ], 
            "ECE243 Computer Organization":[
                "assembly",
                "verilog",
                "baremetal programming",
                "linux os",
                "compilers",
            ], 
            "ECE297 Software Communication and Design":[
                "project management",
                "teamwork",
                "good communication",
                "documentation",
                "c++ programming",
                "linux os",
                "gis design",
                "ui/ux design",
                "git"
            ], 
            "BME445 Neural Bioelectricity":[
                "biology",
                "eeg",
                "biotechnology",
                "artificial intelligence",
                "machine learning",
                "scientific modeling",
                "matlab"
            ], 
            "ECE302 Probability and Applications":[
                "mathematics",
                "math",
                "probability",
                "probabilistic modeling",
                "machine learning"
            ], 
            "ECE344 Operating Systems":[
                "c programming",
                "assembly",
                "os programming",
                "mutlthreading",
                "unix os",
                "linux os",
                "pair programming"          
            ], 
            "ECE361 Computer Networks I":[
                "networks",
                "cyber security",
                "c programming",
                "git", 
                "network protocols"
            ], 
            "ECE421 Introduction to Machine Learning":[
                "machine learning",
                "ml",
                "artificial intelligence",
                "ai",
                "python",
                "probabilistic modeling",
                "data science",
                "data engineering",
                "data sets",
            ], 
            "APS360 Applied Fundamentals of Machine Learning":[
                "machine learning",
                "ml",
                "artificial intelligence",
                "ai",
                "python",
                "git",
                "data science",
                "data engineering",
                "data sets",
            ], 
            "CSC384 Introduction to Artificial Intelligence":[
                "machine learning",
                "ml",
                "artificial intelligence",
                "ai",
                "python",
                "c++",
                "algorithms",
                "data science",
                "data engineering",
                "data sets"
            ], 
            "ECE320 Fields and Waves":[
                "waves",
                "electromagnetism",
                "advanced calculus"
            ], 
            "ECE345 Algorithms and Data Structures":[
                "software",
                "programming",
                "linux os",
                "c++",
                "data science",
                "data engineering",
                "data sets",
                "algorithms",
                "git"
            ], 
            "ECE496 Machine Learning Capstone Project":[
                "project management",
                "teamwork",
                "good communication",
                "documentation",
                "c++ programming",
                "linux os",
                "ui/ux design",
                "git",
                "machine learning",
                "ml",
                "artificial intelligence",
                "ai",
                "distributed systems",
                "data science",
                "data engineering",
                "data sets",
                "research",
                "federated learning"
            ], 
            "CLA204 Introduction to Classical Mythology":[
                "mythology",
                "classics"
            ], 
            "ECE368 Probabilistic Reasoning":[
                "mathematics",
                "math",
                "probability",
                "probabilistic modeling",
                "machine learning"
            ], 
            "ECE470 Robot Modeling and Control":[
                "control systems",
                "matlab",
                "robotics"
            ], 
            "AST 251 Life on Other Worlds":[
                "astronomy",
                "physics",
                "scientific method"
                
            ], 
            "JRE420 People Management and Organizational Behaviour":[
                "project management",
                "teamwork",
                "good communication",
                "documentation"
            ], 
            "TEP444 Positive Psychology for Engineers":[
            ]
        }
    }
}