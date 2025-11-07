DEBUG = {
    "TIME_LOGGING": True,
    "TOKEN_LOGGING": False,
    "ERROR_LOGGING": True,
    "WARNING_LOGGING": True,
    "INFO_LOGGING": True,
    "HEURISTIC_LOGGING": True,
    "PRUNING_LOGGING":True
}
CONFIG = {
    "JOB_SUMM_PRECISION": 4,
    "WINDOWS": 4,
    "SUMMARY_MODE": "batch", #Options: "single", "batch" or "parallel"
    "SUMMARY_REQUESTS": 2,
    "NOTIFICATIONS": {
        "ENABLED": True,
        "WINDOWS": True,
        "SOUND": True
    },
    "MODELS": {
        "TEMPERATURE": 0.1,
        "RETRIES": 2
    },
    "PRUNING": {
        
        # "MALICIOUS_COMPLIANCE_SK":{
        #     "PROG":{
        #         "STATUS":False,
        #         "NO":"1"
        #     },
        #     "TECH":{
        #         "STATUS":False,
        #         "NO": "1"
        #     },
        #     "SOFT":{
        #         "STATUS":False,
        #         "NO":"all"
        #     },
        # },
        # "MALICIOUS_COMPLIANCE_COURSES":{
        #     "STATUS": False,
        #     "NO": "3"
        # },
        # "CUSTOM_SKILLS": {
        #     "PROG": False,
        #     "TECH": False,
        #     "SOFT": False
        # },
        #HEURISTIC FUNCTIONS PER PRUNING ALGORITHM
        #ratio, partial_ratio, toekn_sort_ratio,partial_token_sort_ratio, token_set_ratio
        "DISTANCE_ALGO_KEY": "token_set_ratio", 
        "DISTANCE_ALGO_DESC": "token_set_ratio",
        "DISTANCE_ALGO_PROG":  "token_set_ratio",
        "DISTANCE_ALGO_TECH":  "token_set_ratio",
        "DISTANCE_ALGO_SOFT":  "token_set_ratio",
        "DISTANCE_ALGO_COURSES": "token_set_ratio",
        #PARAMETERS TO CONTROL NUMBER OF EXPERIENCES
        # "MAX_EXPERIENCES": 5,
        # "PER_SECTION_MIN": 1,
        #PARAMETERS TO CONTROL NUMBER OF COURSES    
        # "NO_COURSES":"5",
        #PARAMETERS TO CONTROL NUMBER OF SKILLS    
        "NO_SKILLS":{
            "PROG": 3,
            "TECH": 5,
            "SOFT":4,
            "PREFERENCES_PROG":False,
            "PREFERENCES_TECH":False,
            "PREFERENCES_SOFT":False,
            "ALGO_PROG":2, #AI always fills rest unless ALGO >= MAX
            "ALGO_TECH":2, #AI always fills rest unless ALGO >= MAX
            "ALGO_SOFT":2, #AI always fills rest unless ALGO >= MAX
            "ALGO_PROG_TH": 1.0,
            "ALGO_TECH_TH": 1.0,
            "ALGO_SOFT_TH": 1.0,
            "COPY_PROG": True,#Toggle copy from job description
            "COPY_LEN_PROG":1,
            "COPY_TECH":True, #Toggle copy from job description
            "COPY_LEN_TECH":1,
            "COPY_SOFT":True, #Toggle copy from job description
            "COPY_LEN_SOFT":1,
        },
        "NO_COURSES":{
            "MAX":5,
            "PREFERENCES":False,
            "ALGO":2, #AI always fills rest unless ALGO >= MAX
            "ALGO_TH":1.0
        },
        "NO_EXPERIENCES":{
            "MAX":5,
            "PER_SECTION": 1,
            "PREFERENCES": False,
            "ALGO":3, #AI always fills rest unless ALGO >= MAX
            "ALGO_TH": 1.0
        },
        #WEIGHTS
        "EXP_H_WEIGHTS": {
            "EXP": 1.0,
            "DESC":1.0,
            "PROG":2.0,
            "TECH":1.0,
            "SOFT":0.5
        },
        "PROG_H_WEIGHT": 1.0,
        "TECH_H_WEIGHT": 1.0,
        "SOFT_H_WEIGHT": 1.0,
        #HEURISTIC OPERATION TYPES
        "EXP_RATING_TYPE": "sum", #or sum or SoM (sum of maxes)
        "PROG_RATING_TYPE": "sum", #or sum or SoM (sum of tmaxes)
        "TECH_RATING_TYPE": "sum", #or sum or SoM (sum of maxes)
        "SOFT_RATING_TYPE": "sum", #or sum or SoM (sum of maxes)
        "COURSES_RATING_TYPE": "max", #or sum or SoM (sum of maxes)
        "COURSES_PRUNING_TYPE": "sum",
        #THRESHOLDS FOR SIMILARITY (SET TO 0 IF BELOW SAID NUMBER)
        "THRESHOLDS":{
            "PROG": 70.0,
            "TECH": 70.0,
            "SOFT": 70.0,
            "EXP": 70.0,
            "COURSES": 70.0
        },
        #TAKE HIGHEST OF HEURISTICS WHEN APPLIED BOTH WAYS
        "DUAL_SCORING":{ #take highest score when performing the DISTANCE_ALGO both ways
            "PROG": True,
            "TECH": True,
            "SOFT": True,
            "EXP": True,
            "COURSES": True
        },
        #PREFERRED ITEMS PER CATHEGORY
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
    #COURSE TAGS
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
                "matlab",
                "backend",
            ],
            "ESC180 Introduction to Computer Programming":[
                "software",
                "programming",
                "c programming",
                "object oriented",
                "linux os",
                "python",
                "git",
                "backend",
                "frontend"
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
                "git",
                "backend",
                "frontend",
                "fullstack",
                "object oriented programming",
                "oop",
                "object oriented design"
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
                "cpu design",
                "backend"
            ], 
            "ECE244 Programming Fundamentals":[
                "software",
                "programming",
                "linux os",
                "c++",
                "object oriented",
                "data structures",
                "algorithms",
                "git",
                "backend",
                "frontend",
                "fullstack",
                "object oriented programming",
                "oop",
                "object oriented design"
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
                "backend",
                "veriloghdl"
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
                "git",
                "backend",
                "frontend",
                "fullstack",
                "object oriented programming",
                "oop",
                "object oriented design"
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
                "pair programming",
                "backend"          
            ], 
            "ECE361 Computer Networks I":[
                "networks",
                "cyber security",
                "c programming",
                "git", 
                "network protocols",
                "backend",
                "tcp",
                "ip"
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
                "backend"
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
                "backend"
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
                "data sets",
                "backend",
                "object oriented programming",
                "oop",
                "object oriented design"
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
                "git",
                "backend",
                "object oriented programming",
                "oop",
                "object oriented design"
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
                "federated learning",
                "backend",
                "object oriented programming",
                "oop",
                "object oriented design"
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
                "robotics",
                "backend"
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