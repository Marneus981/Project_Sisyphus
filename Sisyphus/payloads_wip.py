from config import CONFIG
DEFAULT_MODEL = "llama3:8b"
DEFAULT_URL = "http://localhost:11434"
"""
Call functions: Ollama and Ollama Sync
    These merge the runtime_info passed by the user and the payloads.PAYLOADS templates
Runtime Functions: All these
         These take a merged call_info object (sample_starts used rarely so it is included)
On ollama functions (not ollama_call or ollama_sync):
FIRST 5 attributes will be used generally from call_id = {
        "call_id": "tailor_summary", #ALWAYS PROVIDED
        "payload_in": {"model": DEFAULT_MODEL, #PROVIDED
                        "system": "", # #system="", #PROVIDED
                        "stream": False, #MERGED
                        "temperature": CONFIG["MODELS"]["TEMPERATURE"]}, #MERGED
        "format": {
            "info_piece_1": "" or [] or {} #PROVIDED
            "info_piece_2": "" or [] or {} #PROVIDED
            ...
            "standard_calls": [], #MERGED
            "non_standard_calls": [],#MERGED
        }, 
        "prompt_in": "", #USUALLY MERGED, SOMETIMES COULD BE EMPTY/PROVIDED
        "ollama_url": DEFAULT_URL, #PROVIDED
        "sample_starts": [] #MERGED
    },
Provided means that these attrubutes must be provided to ollama_call or ollama_call_async as
runtime_info objects. Merged fields will be fetched from payloads.PAYLOADS
"""

"""
Prompt Format:

**REQUEST:START**

**REQUEST:END**
**OUTPUT FORMAT:START**

**OUTPUT FORMAT:END**
**EXAMPLE:START**

**EXAMPLE:END**
**INPUT:START**

**INPUT:END**


- Return the requested information, strictly filling out the OUTPUT FORMAT and following the included OUTPUT EXAMPLES.
"""

PAYLOADS= {
    # STANDARD CALLS
    "consistency_checker_vs_cv_cl": #DONE
    {
        "call_id": "consistency_checker_vs_cv_cl", 
        "payload_in": {
                       "model": DEFAULT_MODEL, #Set at runtime
                       "system": "",  #Set at runtime
                       "stream": False,
                       "temperature": CONFIG["MODELS"]["TEMPERATURE"]
                       },
        "format": {#Set at runtime
                   "cv_data": "",
                   "cv_data_orig": ""  
                   },
        "prompt_in": 
"""**REQUEST:START**
Given a cover letter and a wholistic summary of a resume (both part of the same job application):
Perform a consistency check on the tailored cover letter against the resume. This consistency check should include:
- Whether the cover letter is consistent with the resume, meaning that all skills and experiences mentioned in the cover letter should be present in the resume.
- Whether the cover letter is consistent with itself, meaning that there should be no contradictions or inconsistencies in the information provided.
The report should follow these guidelines:
- Be mindful not to include any line breaks in  the content of any of the sections/subsections.
- Be as objective as possible, and if you must make assumptions, make very conservative assumptions
- Do not create nor imagine any data that is not present in the original data.
- When filling out the output format, include the numbers "[0]", "[1]", and do not modify the format.
- Return the requested information, strictly filling out the OUTPUT FORMAT and following the included OUTPUT EXAMPLES.
**REQUEST:END**
**OUTPUT FORMAT:START**
[0]Consistency Checker Vs Resume:
[1]Inconsistencies With Resume: Number of inconsistencies found (return 'None' if no inconsistencies). List of inconsistencies found, if any, must be a continuous block of text, composed of sentences separated by ";", not line breaks.
[1]Inconsistencies With Self: Number of inconsistencies found (return 'None' if no inconsistencies). List of inconsistencies found, if any, must be a continuous block of text, composed of sentences separated by ";", not line breaks.
[1]Suggestions for Improvement: List of suggestions for improvement, if any (return 'None' if no suggestions). must be a continuous block of text, composed of sentences separated by ";", not line breaks.
**OUTPUT FORMAT:END**
**EXAMPLE:START**
EXAMPLE OUTPUT 1:
[0]Consistency Checker Vs Resume:
[1]Inconsistencies With Resume: None.
[1]Inconsistencies With Self: None.
[1]Suggestions for Improvement: None.
EXAMPLE OUTPUT 2:
[0]Consistency Checker Vs Resume:
[1]Inconsistencies With Resume: 2 inconsistencies found with Resume. The cover letter talks about a non-existent position at WestCo manufacturing; There is a data mismatch on the Masters of Manufacturing completion date.  
[1]Inconsistencies With Self: 1 inconsistency found. The cover letter mentions a degree in economics, but then mentions the lack of it.
[1]Suggestions for Improvement: Correct the above inconsistencies; Do not refer to the candidate in the thrid person since you are meant to write the cover letter in their place.
**EXAMPLE:END**
**INPUT:START**
INPUT cover letter:
{cv_data}

INPUT wholistic summary of the resume meant to accompany the above cover letter on a job application:
{cv_data_orig}
**INPUT:END**
""",
        "ollama_url": DEFAULT_URL, #Set at runtime
        "sample_starts": ["strict", "digits", "[0]Consistency Checker Vs Resume:", "[1]Inconsistencies With Resume:","[1]Inconsistencies With Self:","[1]Suggestions for Improvement:"] #[type, sample starts]
    },
    "summarize_job_description": #DONE
    {
        "call_id": "summarize_job_description", 
        "payload_in": {
                       "model": DEFAULT_MODEL, #Set at runtime
                       "system": "",  #Set at runtime
                       "stream": False,
                       "temperature": CONFIG["MODELS"]["TEMPERATURE"]
                       },
        "format": {#Set at runtime
                   "job_description": "" 
                   },
        "prompt_in": 
"""**REQUEST:START**
Summarize the input job description by extracting the following information in the format specified under the OUTPUT FORMAT section:
-Company Name
-Job Title
-Key responsibilities
-Requirements:
    -Programming Languages
    -Techincal Skills
    -Soft Skills
    -Other Skills
When filling out the OUTPUT FORMAT, follow these guidelines:
- Do not modify the format and always include the line prefixes ([0]) as well as the field name (e.g. [0]Company Title:).
- Do not add any information not present in the provided job description, your goal is to extract information and summarize.
- Use simple and concise language when possible, but do use specific keywords.
- Return the requested information, strictly filling out the OUTPUT FORMAT and following the included OUTPUT EXAMPLES.
**REQUEST:END**
**OUTPUT FORMAT:START**
[0]Company Name: Company Name
[0]Job Title: Position Name
[0]Key responsibilities: List of key responsabilities as a single block of text separated by ";"
[0]Requirements: List of basic requirements as a single block of text separated by ";"
[0]Programming Languages: List of programming languages required, presented as a single block of text separated by ";"
[0]Technical Skills: List of technical skills required, presented as a single block of text separated by ";"
[0]Soft Skills:Soft List of soft skills required, presented as a single block of text separated by ";"
[0]Other Skills:Other List of other skills required, presented as a single block of text separated by ";"
**OUTPUT FORMAT:END**
**EXAMPLE:START**
[0]Company Name: Sentry
[0]Job Title: Software Engineer, New Grad
[0]Key Responsibilities: Develop and extend software in Python or JavaScript (or both); Full software development lifecycle: design, develop, test, and operate in production; Communicate effectively with teams and stakeholders; Act on feedback, coaching, and mentorship from manager and teammates
[0]Requirements: B.S. or higher in Computer Science (or similar degree program); At least 1 previous internship or equivalent practical experience
[0]Programming Languages: Proficiency in one or more general-purpose programming languages (e.g. Python, JavaScript, Java)
[0]Technical Skills: Knowledge of algorithms, data structures, and object-oriented design principles; Implementation skills with version control and unit testing
[0]Soft Skills Needed: Effective communication with teams and stakeholders; Ability to act on feedback, coaching, and mentorship from manager and teammates
**EXAMPLE:END**
**INPUT:START**
INPUT job description:
{job_description}
**INPUT:END**
""",
        "ollama_url": DEFAULT_URL, #Set at runtime
        "sample_starts": [] #[type, sample starts]
    },
    ##similar start
    "step0_volunteering_and_leadership": #DONE
    {
        "call_id": "step0_volunteering_and_leadership", 
        "payload_in": {
                       "model": DEFAULT_MODEL, #Set at runtime
                       "system": "",  #Set at runtime
                       "stream": False,
                       "temperature": CONFIG["MODELS"]["TEMPERATURE"]
                       },
        "format": {#Set at runtime
                   "raw_cv_data": "",
                   "job_description": ""
                   },
        "prompt_in": 
"""**REQUEST:START**
Given a "Volunteering and Leadership" resume section and a job description, select up to 5 roles based on the job description. When selecting:
- If the total number of roles is less than or equal to 5, return all of them.
- If the total number of roles is greater than or equal to 5 before selection: Select the most relevant 5 roles based on the job description.
- Do not change the name of the roles.
- Prioritize roles that match relevant skills and experience present in the job description.
- It is okay to not select any roles if none are relevant.
- Display the Role Titles explicitly; do not write "Role Title:" before the Role Title
- When filling out the output format,  you may not change the role title text, do not include any text before [R] or after the role title text.
- Return the requested information, strictly filling out the OUTPUT FORMAT and following the included OUTPUT EXAMPLES.
**REQUEST:END**
**OUTPUT FORMAT:START**
[R]Role Title 1
[R]Role Title 2
[R]Role Title 3
[R]Role Title 4
[R]Role Title 5
**OUTPUT FORMAT:END**
**EXAMPLE:START**
EXAMPLE OUTPUT 1 (NUMBER OF INPUT ROLES = 2):
[R]Animal Shelter Volunteer
[R]Engineering Convention Organizer
EXAMPLE OUTPUT 2 (NUMBER OF INPUT ROLES = 8; CHOSE 5 BEST):
[R]MIT Hackaton Team Leader
[R]Engineering Ambassador Program
[R]Team Leader at Robotics Olympics
[R]Engineering Convention Organizer
[R]Homeless Shelter Volunteer
**EXAMPLE:END**
**INPUT:START**
INPUT "Volunteering and Leadership" resume section:
{raw_cv_data}
INPUT job description:
{job_description}
**INPUT:END**
""",
        "ollama_url": DEFAULT_URL, #Set at runtime
        "sample_starts": ["flexible", "cap_letters", "[R]"]
    },
    "step3_volunteering_and_leadership": #DONE
    {
        "call_id": "step3_volunteering_and_leadership", 
        "payload_in": {
                       "model": DEFAULT_MODEL, #Set at runtime
                       "system": "",  #Set at runtime
                       "stream": False,
                       "temperature": CONFIG["MODELS"]["TEMPERATURE"]
                       },
        "format": {#Set at runtime
                   "experience": "",
                   "job_description": ""
                   },
        "prompt_in": 
"""**REQUEST:START**
Given the "Description" and "Skills" attributes of a role belonging to the "Volunteering and Leadership" section of a resume and a job description, rewrite the experience to best match the job description, following these guidelines:
- Do not include any information not present in the original experience.
- In the Description subsection, rewrite to highlight achievements and relevant skills for the job, using up to 2 sentences (max 20 words each), as a single block of text.
- In the Skills subsection, include up to 6 relevant skills (Programming Languages, Technical Skills, Soft Skills). Every skill category should be present, even if empty.
- Do not use line breaks inside any subsection. Do not use the ":" character in the Description.
- Skills must be comma-separated and follow the format below. 
- If there are no skills in a given category, use " ", then follow up as the format below indicates 
    - For example: Programming Languages: ; Technical Skills: ; Soft Skills: Communication, Teamwork
- Include the prefix [1] at the start of each line (as seen in the format below).
- Return the requested information, strictly filling out the OUTPUT FORMAT and following the included OUTPUT EXAMPLES.
**REQUEST:END**
**OUTPUT FORMAT:START**
[1]Description: Brief role description.
[1]Skills: Programming Languages: ...; Technical Skills: ...; Soft Skills: ...
**OUTPUT FORMAT:END**
**EXAMPLE:START**
EXAMPLE INPUT 1:
INPUT job description:
Company Name: Sentry
Job Title: Software Engineer, New Grad
Key Responsibilities:
- Develop and extend the Sentry product by writing software in Python or JavaScript (or both)
- Complete full software development lifecycle - design, development, testing, and operating in production
- Communicate effectively with team members, other teams, and stakeholders
- Act on feedback, coaching, and mentorship from manager and teammates
Key Skills:
- Programming skills in one or more general-purpose languages (Python, JavaScript, Java, etc.)
- Knowledge of algorithms, data structures, and object-oriented design principles
- Experience working with version control and unit testing
- Strong communication and collaboration skills
Soft Skills:
- Eagerness to actively use the product being built (Sentry)
- Desire to start career at a high-growth startup
- Excitement about contributing to an open-source project daily
- Willingness to receive feedback, coaching, and mentorship from manager and teammates
Education: 
- B.S. or higher in Computer Science (or similar degree program)
Experience: 
- At least 1 previous internship or equivalent practical experience
INPUT "Description" and "Skills" attributes of a role belonging to the "Volunteering and Leadership" section of a resume:
[1]Description: Mentored over 100 aspiring developers in Python and web development, designing and delivering curriculum modules on REST APIs, Docker, and cloud integration. Achieved a 90% bootcamp completion rate and improved participant job placement by 35%. Fostered a collaborative learning environment, provided personalized feedback, and facilitated group projects and hackathons to encourage teamwork and innovation. Developed advanced workshops on microservices and cloud computing, resulting in measurable increases in participant technical proficiency. Provided ongoing career guidance and support, helping graduates secure positions at leading tech companies. Consistently received positive feedback from participants and program coordinators for dedication, expertise, and impact. Led outreach initiatives to local schools and organizations, expanding program reach and promoting diversity in tech. Recognized for exceptional mentoring, communication, and leadership skills. Coordinated alumni networking events and maintained relationships with graduates to track career progress and offer continued support. Implemented feedback systems to improve curriculum and teaching methods, ensuring the program remained relevant and effective. Collaborated with other mentors to share best practices and develop new instructional materials, contributing to the overall success and reputation of the bootcamp
[1]Skills: Programming Languages: Python, JavaScript, Java, C++, SQL, Dart; Soft Skills: Mentoring, Communication, Leadership, Problem Solving, Teamwork, Adaptability; Technical Skills: Web Development, REST APIs, Docker, Kubernetes, Cloud Integration, Data Visualization 
EXAMPLE OUTPUT 1:
[1]Description: Mentored aspiring developers in Python, designing curriculum modules on REST APIs and cloud integration. Fostered a collaborative learning environment and developed advanced workshops.
[1]Skills: Programming Languages: Python, JavaScript; Technical Skills: Web Development, REST APIs, Docker, Cloud Integration; Soft Skills: Mentoring, Communication
**EXAMPLE:END**
**INPUT:START**
INPUT job description:
{job_description}

INPUT "Description" and "Skills" attributes of a role belonging to the "Volunteering and Leadership" section of a resume:
{experience}
**INPUT:END**
""",
        "ollama_url": DEFAULT_URL, #Set at runtime
        "sample_starts": ["strict", "digits", "[1]Description:", "[1]Skills:"]
    },
    "step0_work_experience": #DONE
    {
        "call_id": "step0_work_experience",
        "payload_in": {
            "model": DEFAULT_MODEL,
            "system": "",
            "stream": False,
            "temperature": CONFIG["MODELS"]["TEMPERATURE"]
        },
        "format": {
            "raw_cv_data": "",
            "job_description": ""
        },
        "prompt_in": 
"""**REQUEST:START**
Given a "Work Experience" resume section and a job description, select up to 5 jobs based on the job description. When selecting:
- If the total number of jobs is less than or equal to 5, return all of them.
- If the total number of jobs is greater than or equal to 5 before selection: Select the most relevant 5 jobs based on the job description.
- Do not change the name of the jobs.
- Prioritize jobs that match relevant skills and experience present in the job description.
- It is okay to not select any jobs if none are relevant.
- Display the Job Titles explicitly; do not write "Job Title:" before the Job Title
- When filling out the output format,  you may not change the job title text, do not include any text before [J] or after the job title text.
- Return the requested information, strictly filling out the OUTPUT FORMAT and following the included OUTPUT EXAMPLES.
**REQUEST:END**
**OUTPUT FORMAT:START**
[J]Job Title 1
[J]Job Title 2
[J]Job Title 3
[J]Job Title 4
[J]Job Title 5
**OUTPUT FORMAT:END**
**EXAMPLE:START**
EXAMPLE OUTPUT 1 (NUMBER OF INPUT ROLES = 2):
[J]Software Engineer
[J]Backend Engineer
EXAMPLE OUTPUT 2 (NUMBER OF INPUT ROLES = 6; CHOSE 5 BEST):
[J]Senior Engineering Manager
[J]Full-Stack Engineer
[J]Computer Engineer II
[J]Backend Engineer
[J]QA Analyst
**EXAMPLE:END**
**INPUT:START**
INPUT "Work Experience" resume section:
{raw_cv_data}

INPUT job description:
{job_description}
**INPUT:END**
""",
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["flexible", "cap_letters", "[J]"]
    },
    "step3_work_experience": #DONE
    {
        "call_id": "step3_work_experience",
        "payload_in": {
            "model": DEFAULT_MODEL,
            "system": "",
            "stream": False,
            "temperature": CONFIG["MODELS"]["TEMPERATURE"]
        },
        "format": {
            "experience": "",
            "job_description": ""
        },
        "prompt_in": 
"""**REQUEST:START**
Given the "Description" and "Skills" subsections of a role belonging to the "Work Experience" section of a resume and a job description, rewrite the experience to best match the job description, following these guidelines:
- Do not include any information not present in the original experience.
- In the Description subsection, rewrite to highlight achievements and relevant skills for the job, using up to 2 sentences (max 20 words each), as a single block of text.
- In the Skills subsection, include up to 6 relevant skills (Programming Languages, Technical Skills, Soft Skills). Every skill category should be present, even if empty.
- Do not use line breaks inside any subsection. Do not use the ":" character in the Description.
- Skills must be comma-separated and follow the format below. 
- If there are no skills in a given category, use " ", then follow up as the format below indicates 
    - For example: Programming Languages: ; Technical Skills: ; Soft Skills: Communication, Teamwork
- Include the prefix [1] at the start of each line (as seen in the format below).
- Return the requested information, strictly filling out the OUTPUT FORMAT and following the included OUTPUT EXAMPLES.
**REQUEST:END**
**OUTPUT FORMAT:START**
[1]Description: Brief role description.
[1]Skills: Programming Languages: ...; Technical Skills: ...; Soft Skills: ...
**OUTPUT FORMAT:END**
**EXAMPLE:START**
EXAMPLE INPUT 1:
INPUT job description:
Company Name: Sentry
Job Title: Software Engineer, New Grad
Key Responsibilities:
- Develop and extend the Sentry product by writing software in Python or JavaScript (or both)
- Complete full software development lifecycle - design, development, testing, and operating in production
- Communicate effectively with team members, other teams, and stakeholders
- Act on feedback, coaching, and mentorship from manager and teammates
Key Skills:
- Programming skills in one or more general-purpose languages (Python, JavaScript, Java, etc.)
- Knowledge of algorithms, data structures, and object-oriented design principles
- Experience working with version control and unit testing
- Strong communication and collaboration skills
Soft Skills:
- Eagerness to actively use the product being built (Sentry)
- Desire to start career at a high-growth startup
- Excitement about contributing to an open-source project daily
- Willingness to receive feedback, coaching, and mentorship from manager and teammates
Education: 
- B.S. or higher in Computer Science (or similar degree program)
Experience: 
- At least 1 previous internship or equivalent practical experience
INPUT "Description" and "Skills" subsections of a role belonging to the "Work Experience" section of a resume:
[1]Description: Led the design and implementation of scalable microservices architecture using Python, Go, and Docker, reducing system downtime by 40% and increasing transaction throughput by 25%. Managed a team of 5 engineers, mentored junior staff, and fostered a culture of continuous improvement. Spearheaded cloud migration, improving reliability and reducing operational costs by 30%. Collaborated with cross-functional teams to deliver high-performance financial applications, integrating Kubernetes for automated deployment and monitoring. Implemented advanced security protocols and compliance measures, ensuring data integrity and regulatory adherence. Provided technical guidance and training to team members, enhancing overall productivity and expertise. Consistently delivered projects on time and within budget, exceeding client expectations and contributing to company growth. Led post-mortem analyses and process improvements, resulting in a 20% reduction in incident response times. Recognized for outstanding leadership, analytical thinking, and technical excellence. Developed documentation and best practices for microservices development, contributing to knowledge sharing and team efficiency. Coordinated with stakeholders to prioritize feature development and address business needs, ensuring alignment with organizational goals
[1]Skills: Programming Languages: Python, Go, Java, JavaScript, C++, SQL; Soft Skills: Leadership, Problem Solving, Communication, Teamwork, Adaptability, Analytical Thinking; Technical Skills: Microservices, Docker, Kubernetes, API Development, Database Design, Cloud Computing
EXAMPLE OUTPUT 1:
[1]Description: Spearheaded scalable microservices architecture, leveraging Python and Docker. Mentored junior staff and fostered continuous improvement, delivering high-performance applications.
[1]Skills: Programming Languages: Python; Technical Skills: Microservices, Docker; Soft Skills: Leadership, Communication
**EXAMPLE:END**
**INPUT:START**
INPUT job description:
{job_description}

INPUT "Description" and "Skills" subsections of a role belonging to the "Work Experience" section of a resume:
{experience}
**INPUT:END**
""",
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["strict", "digits" ,"[1]Description:", "[1]Skills:"]
    },
    "step0_projects": #DONE
    {
        "call_id": "step0_projects",
        "payload_in": {
            "model": DEFAULT_MODEL,
            "system": "",
            "stream": False,
            "temperature": CONFIG["MODELS"]["TEMPERATURE"]
        },
        "format": {
            "raw_cv_data": "",
            "job_description": ""
        },
        "prompt_in": 
"""**REQUEST:START**
Given a "Projects" resume section and a job description, select up to 5 projects based on the job description. When selecting:
- If the total number of projects is less than or equal to 5, return all of them.
- If the total number of projects is greater than or equal to 5 before selection: Select the most relevant 5 projects based on the job description.
- Do not change the name of the projects.
- Prioritize projects that match relevant skills and experience present in the job description.
- It is okay to not select any projects if none are relevant.
- Display the Project Titles explicitly; do not write "Project Title:" before the Project Title
- When filling out the output format,  you may not change the project title text, do not include any text before [P] or after the project title text.
- Return the requested information, strictly filling out the OUTPUT FORMAT and following the included OUTPUT EXAMPLES.
**REQUEST:END**
**OUTPUT FORMAT:START**
[P]Project Title 1
[P]Project Title 2
[P]Project Title 3
[P]Project Title 4
[P]Project Title 5
**OUTPUT FORMAT:END**
**EXAMPLE:START**
EXAMPLE OUTPUT 1 (NUMBER OF INPUT ROLES = 2):
[P]ml_for_dummies Open Source Library
[P]IoT Controller App
EXAMPLE OUTPUT 2 (NUMBER OF INPUT ROLES = 7; CHOSE 5 BEST):
[P]RAG Powered Local Search Engine
[P]Classic Game Solver with AI
[P]IoT Controller App
[P]Cyber Security Capstone Project
[P]Custom DB Manager
**EXAMPLE:END**
**INPUT:START**
INPUT "Projects" resume section:
{raw_cv_data}

INPUT job description:
{job_description}
**INPUT:END**
""",
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["flexible", "cap_letters", "[P]"]
    },
    "step3_projects": #DONE
    {
        "call_id": "step3_projects",
        "payload_in": {
            "model": DEFAULT_MODEL,
            "system": "",
            "stream": False,
            "temperature": CONFIG["MODELS"]["TEMPERATURE"]
        },
        "format": {
            "experience": "",
            "job_description": ""
        },
        "prompt_in": 
"""**REQUEST:START**
Given the "Description" and "Skills" subsections of a project belonging to the "Projects" section of a resume and a job description, rewrite the experience to best match the job description, following these guidelines:
- Do not include any information not present in the original experience.
- In the Description subsection, rewrite to highlight achievements and relevant skills for the job, using up to 2 sentences (max 20 words each), as a single block of text.
- In the Skills subsection, include up to 6 relevant skills (Programming Languages, Technical Skills, Soft Skills). Every skill category should be present, even if empty.
- Do not use line breaks inside any subsection. Do not use the ":" character in the Description.
- Skills must be comma-separated and follow the format below. 
- If there are no skills in a given category, use " ", then follow up as the format below indicates 
    - For example: Programming Languages: ; Technical Skills: ; Soft Skills: Communication, Teamwork
- Include the prefix [1] at the start of each line (as seen in the format below).
- Return the requested information, strictly filling out the OUTPUT FORMAT and following the included OUTPUT EXAMPLES.
**REQUEST:END**
**OUTPUT FORMAT:START**
[1]Description: Brief project description.
[1]Skills: Programming Languages: ...; Technical Skills: ...; Soft Skills: ....
**OUTPUT FORMAT:END**
**EXAMPLE:START**
EXAMPLE INPUT 1:
INPUT job description:
Company Name: Sentry
Job Title: Software Engineer, New Grad
Key Responsibilities:
- Develop and extend the Sentry product by writing software in Python or JavaScript (or both)
- Complete full software development lifecycle - design, development, testing, and operating in production
- Communicate effectively with team members, other teams, and stakeholders
- Act on feedback, coaching, and mentorship from manager and teammates
Key Skills:
- Programming skills in one or more general-purpose languages (Python, JavaScript, Java, etc.)
- Knowledge of algorithms, data structures, and object-oriented design principles
- Experience working with version control and unit testing
- Strong communication and collaboration skills
Soft Skills:
- Eagerness to actively use the product being built (Sentry)
- Desire to start career at a high-growth startup
- Excitement about contributing to an open-source project daily
- Willingness to receive feedback, coaching, and mentorship from manager and teammates
Education: 
- B.S. or higher in Computer Science (or similar degree program)
Experience: 
- At least 1 previous internship or equivalent practical experience
INPUT "Description" and "Skills" subsections of a project belonging to the "Projects" section of a resume:
[1]Description: Developed a real-time analytics dashboard using Python and React, enabling clients to monitor KPIs and generate actionable reports. Integrated WebSockets for live data updates and advanced data visualization, increasing user engagement by 50%. Optimized backend performance, reducing query latency by 35%. Designed modular architecture to support future scalability and feature expansion. Collaborated with stakeholders to define requirements and deliver a user-friendly interface. Provided training and documentation for end users, ensuring successful adoption and utilization. Implemented role-based access controls and security features to protect sensitive data. Received positive feedback from clients and management for technical excellence and business impact. Led post-launch support and feature enhancements, maintaining high user satisfaction and system reliability. Developed automated reporting tools and export features to support business analysis and decision-making
[1]Skills: Programming Languages: Python, JavaScript, Dart, Java, C++, SQL; Soft Skills: Presentation, Documentation, UX Design, Initiative, Creativity, Self-Motivation; Technical Skills: Data Visualization, WebSockets, Mobile Development, Cloud Integration, API Integration, NLP
EXAMPLE OUTPUT 1:
[1]Description: Built a real-time analytics dashboard using Python and React, with skills in data visualization and WebSockets. Collaborated with stakeholders to deliver user-friendly interfaces.
[1]Skills: Programming Languages: Python, JavaScript; Technical Skills: Data Visualization, WebSockets, API Integration; Soft Skills: Communication
**EXAMPLE:END**
**INPUT:START**
INPUT job description:
{job_description}

INPUT "Description" and "Skills" subsections of a project belonging to the "Projects" section of a resume:
{experience}
**INPUT:END**
""",
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["strict", "digits", "[1]Description:", "[1]Skills:"]
    },
    ##similar end
    "step0_prune_experiences": #DONE
    {
        "call_id": "step0_prune_experiences",
        "payload_in": {
            "model": DEFAULT_MODEL,
            "system": "",
            "stream": False,
            "temperature": CONFIG["MODELS"]["TEMPERATURE"]
        },
        "format": {
            "experiences": "",
            "job_description": ""
        },
        "prompt_in": 
"""**REQUEST:START**
Given the all experiences across 3 resume sections (Volunteering and Leadership, Work Experience, and Projects) and a job description, select up to 5 experiences based on the job description. When selecting:
- If the total number of experiences/roles is less than or equal to 5, return all of them.
- If the total number of experiences/roles is greater than or equal to 5 before selection: Select the most relevant 5 experiences/roles based on the job description.
- Do not change the name of the experiences/roles.
- Prioritize projects that match relevant skills and experience present in the job description.
- It is okay to not select any experiences from a given section if none are relevant. Remember that [R], [J], and [P] indicate the section they belong to (R is Volunteering and Leadership, J is Work Experience, and P is Projects).
- While filling out the output format, do not change the role/job title/project title text, and do not include any text before [R], [J], or [P] or after the role/job title/project title text.
- Return the requested information, strictly filling out the OUTPUT FORMAT and following the included OUTPUT EXAMPLES.
**REQUEST:END**
**OUTPUT FORMAT:START**
[X]Role/Job Title/Project Title 1
...
[X]Role/Job Title/Project Title 5
Where [X] indicates the type of experience:
- [R] Role belongs to Volunteering and Leadership
- [J] Job Title belongs to Work Experience
- [P] Project Title belongs to Projects
**OUTPUT FORMAT:END**
**EXAMPLE:START**
EXAMPLE OUTPUT 1(NUMBER OF EXPERIENCES = 3):
[R]Volunteer at Tech4Kids
[J]Senior Software Engineer
[R]University of Michigan Hackaton Leader
EXAMPLE OUTPUT 2(NUMBER OF EXPERIENCES = 7; CHOSE 5 BEST):
[R]Civil Engineering Ambassador at the University of Colorado 
[J]Full-Stack Engineer
[J]Java Engineer
[P]TuneMax Song Streaming Search Engine
[P]Beer Fetching Robot
**EXAMPLE:END**
**INPUT:START**
INPUT job description:
{job_description}

INPUT 3 resume sections (Volunteering and Leadership, Work Experience, and Projects):
{experiences}
**INPUT:END**
""",
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["flexible", "cap_letters", "[P]", "[J]", "[R]"]
    },
    "summarize_section": #DONE
    {
        "call_id": "summarize_section",
        "payload_in": {
            "model": DEFAULT_MODEL,
            "system": "",
            "stream": False,
            "temperature": CONFIG["MODELS"]["TEMPERATURE"]
        },
        "format": {
            "section": "",
            "section_name": ""
        },
        "prompt_in": 
"""**REQUEST:START**
Given a section from a resume, summarize the sections in a wholistic manner while following these guidelines:
- Be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
- Include all information, competencies, achievements, and skills, this is a wholistic summary of the candidate's qualifications.
- Return the summarized information as a single continuous string of text, following the output format strictly. 
- Do not forget to include the "[S]{section_name} Section Summary:" text at the start of the output.
- Return the requested information, strictly filling out the OUTPUT FORMAT and following the included OUTPUT EXAMPLES.
**REQUEST:END**
**OUTPUT FORMAT:START**
[S]{section_name} Summary: Wholistic summary of the section's information.
**OUTPUT FORMAT:END**
**EXAMPLE:START**
EXAMPLE INPUT 1:
[0]Education:
[1]Degree: B.Sc. Computer Science
[1]University: Springfield University
[1]Location: Springfield, USA
[1]Duration: 2012/09 - 2016/06
[1]Courses: Algorithms, Data Structures, Operating Systems, Databases
[1]Degree: M.Sc. Software Engineering
[1]University: Capital Tech
[1]Location: Capital City, USA
[1]Duration: 2016/09 - 2018/06
[1]Courses: Cloud Computing, Distributed Systems, Advanced Programming
EXAMPLE OUTPUT 1:
[S]Education Section Summary: This candidate holds a Bachelor of Science in Computer Science from Springfield University (2012-2016), with courses in Algorithms, Data Structures, Operating Systems, and Databases. They then pursued a Master of Science in Software Engineering at Capital Tech (2016-2018), focusing on Cloud Computing, Distributed Systems, and Advanced Programming.
**EXAMPLE:END**
**INPUT:START**
INPUT section from a resume:
{section}

**INPUT:END**
""",
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["strict", "cap_letters", "[S]"]
    },
    "summarize_general_info": #DONE
    {
        "call_id": "summarize_general_info",
        "payload_in": {
            "model": DEFAULT_MODEL,
            "system": "",
            "stream": False,
            "temperature": CONFIG["MODELS"]["TEMPERATURE"]
        },
        "format": {
            "general_info_text": ""
        },
        "prompt_in": 
"""**REQUEST:START**
Given the general information from a resume, summarize it in a wholistic manner; be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
Since this is a summary of a resume's general information, you need to include the candidate's Name, Contact Information, Title, and Languages Spoken.
Return the requested information, strictly filling out the OUTPUT FORMAT and following the included OUTPUT EXAMPLES (do not forget to include the "[S]General Information Summary:" text at the start of the output).
**REQUEST:END**
**OUTPUT FORMAT:START**
[S]General Information Summary: Brief and concise summary of the resume's general information, presented as a single continuous string of text.
**OUTPUT FORMAT:END**
**EXAMPLE:START**
EXAMPLE INPUT 1:
[0]Name: Jane Doe
[0]Contact Information:
[1]Address: 123 Main St, Springfield, USA
[1]Phone: +1-555-123-4567
[1]Email: jane.doe@email.com
[1]LinkedIn: linkedin.com/in/janedoe
[1]Github: github.com/janedoe
[1]Portfolio: janedoe.dev
[0]Title: Senior Software Engineer
[0]Languages: English, Spanish, French
EXAMPLE OUTPUT 1:
[S]General Information Summary: Jane Doe is a Senior Software Engineer with contact details including an address at 123 Main St, Springfield, USA, phone number +1-555-123-4567, email jane.doe@email.com, LinkedIn linkedin.com/in/janedoe, Github github.com/janedoe, and Portfolio janedoe.dev. Jane speaks English, Spanish, and French fluently.
**EXAMPLE:END**
**INPUT:START**
INPUT general information from a resume:
{general_info_text}

**INPUT:END**
""",
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["strict", "cap_letters", "[S]General Information Summary:"]
    },
    "summarize_skills":#DONE
    {
        "call_id": "summarize_skills",
        "payload_in": {
            "model": DEFAULT_MODEL,
            "system": "",
            "stream": False,
            "temperature": CONFIG["MODELS"]["TEMPERATURE"]
        },
        "format": {
            "skill_section": ""
        },
        "prompt_in": 
"""**REQUEST:START**
Given a "Skills" section from a resume, summarize the skills section of a resume in a wholistic manner; be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
Return the requested information, strictly filling out the OUTPUT FORMAT and following the included OUTPUT EXAMPLES (do not forget to include the "[S]Skills Summary:" text at the start of the output).
**REQUEST:END**
**OUTPUT FORMAT:START**
[S]Skills Summary: Brief and concise wholistic summary of the resume's skills, presented as a single continuous string of text.
**OUTPUT FORMAT:END**
**EXAMPLE:START**
INPUT EXAMPLE 1:
[0]Skills:
[1]Programming Languages: Programming Language 1, Python, JavaScript
[1]Technical Skills: REST APIs, Web Development, API Development, Cloud Setup
[1]Soft Skills: Collaboration, Communication, Leadership, Teamwork
OUTPUT EXAMPLE 1:
[S]Skills Summary: Proficient in Python, and JavaScript. Experienced with REST APIs, web development, and API development. Additionally, skilled in cloud setup and possess strong collaboration, communication, leadership, and teamwork abilities.
**EXAMPLE:END**
**INPUT:START**
INPUT "Skills" section from a resume:
{skill_section}

**INPUT:END**
""",
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["strict", "cap_letters", "[S]Skills Summary:"]
    },
    "step1_tailor_summary": #DONE
    {
        "call_id": "step1_tailor_summary",
        "payload_in": {
            "model": DEFAULT_MODEL,
            "system": "",
            "stream": False,
            "temperature": CONFIG["MODELS"]["TEMPERATURE"]
        },
        "format": {
            "prev_summary": "",
            "job_description": ""
        },
        "prompt_in": 
"""**REQUEST:START**
Given a wholistic summary of a resume and a job description, tailor a Summary section for a resume to best match the job description; follow these guidelines:
- Write the tailored summary section as the candidate, not as an external observer.
- The summary mustn't exceed 100 words.
- Do not line break the summary section, it should be a continuous block of text.
- When mentioning specific skills or experiences, these must be relevant to the job description; give preference to those that appear on both the resume and the job description, particularly those which demonstrate the candidate's technical expertise.
- In the format below, do not include any text before "[0]" or after the requested information.
- Return only the revised summary and strictly follow the output format, filling in the parts that have **fill-in:"text"**
- Return the requested information, strictly filling out the OUTPUT FORMAT and following the included OUTPUT EXAMPLES.
**REQUEST:END**
**OUTPUT FORMAT:START**
[0]Summary: Despite limited work experience, I bring strong work ethic, adaptability and curiosity. Experienced in **fill-in:"specific skills thanks to certain experiences"**. Now seeking a position that offers growth and learning opportunities.
**OUTPUT FORMAT:END**
**EXAMPLE:START**
EXAMPLE INPUT 1:
[0]Summary:Jane Doe, Senior Software Engineer | +1-555-123-4567 | jane.doe@email.com | linkedin.com/in/janedoe | github.com/janedoe | janedoe.dev | Fluent in English, Spanish, and French.Certifications: AWS Certified Solutions Architect (2019), Scrum Master (2020).Education:Bachelor of Science in Computer Science from Springfield University (2012-2016) - courses in Algorithms, Data Structures, Operating Systems, and Databases.Master of Science in Software Engineering at Capital Tech (2016-2018) - focus on Cloud Computing, Distributed Systems, and Advanced Programming.Projects: Real-time analytics dashboard using Python, incorporating role-based access controls and security features to protect sensitive data, solidifying proficiency in Data Visualization, WebSockets, and communication.Work Experience:Senior Software Engineer at WebApps Inc. - RESTful API development, optimizing database queries, and microservices; delivered significant improvements in application performance by 30%.Volunteering & Leadership:Coding Bootcamp Mentor at CodeSpring (2020-2022) - mentoring and leadership skills.Hackathon Organizer at TechFest (2018-2019) - event planning, teamwork, and problem-solving.Skills: Proficient in Microsoft Office Suite, Google Workspace tools, Asana, Trello; strong problem-solving skills and ability to work effectively in a fast-paced environment.
EXAMPLE OUTPUT 1:
[0]Summary: Despite limited work experience, I bring strong work ethic, adaptability and curiosity. Experienced in Python development, data visualization, and communication through projects like the real-time analytics dashboard and mentoring at CodeSpring. Now seeking a position that offers growth and learning opportunities.
**EXAMPLE:END**
**INPUT:START**
INPUT wholistic summary of a resume:
{prev_summary}

INPUTjob description:
{job_description}

**INPUT:END**
""",
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["strict", "digits", "[0]Summary:"]
    },
    "tailor_skills": #DONE
    {
        "call_id": "tailor_skills",
        "payload_in": {
            "model": DEFAULT_MODEL,
            "system": "",
            "stream": False,
            "temperature": CONFIG["MODELS"]["TEMPERATURE"]
        },
        "format": {
            "cv_data": "",
            "job_description": ""
        },
        "prompt_in": 
"""**REQUEST:START**
Given a list of "Programming Languages", "Technical Skills" and "Soft Skills" considered to be relevant for a paticular job description, and said job description:
Prune the following 'Skills' section from a resume to best match the job description , following the guidelines below:
- Return 3 MAXIMUM entries under "Programming Languages" (MINIMUM 0 entries)
- Return 5 MAXIMUM entries under "Technical Skills" (MINIMUM 0 entries)
- Return 4 MAXIMUM entries under "Soft Skills" (MINIMUM 0 entries)
- Prioritize skills that are explicitly mentioned in the job description.
- For Soft Skills (only), prioritize skills mentioned in the job description, and if these skills are less than 4, fill the remaining slots with other relevant skills from the CV.
- Do not line break any line containing the relevant skills, it should follow the format below strictly.
- If either the "Programming Languages", "Technical Skills", or "Soft Skills" sections are empty, return them as an empty section.
- Aside from the information requested, do not include any additional text or explanations.
- Return the requested information, strictly filling out the OUTPUT FORMAT and following the included OUTPUT EXAMPLES.
**REQUEST:END**
**OUTPUT FORMAT:START**
[0]Skills:
[1]Programming Languages: Programming Language 1, Programming Language 2, Programming Language 3
[1]Technical Skills: Technical Skill 1, Technical Skill 2, Technical Skill 3, Technical Skill 4, Technical Skill 5
[1]Soft Skills: Soft Skill 1, Soft Skill 2, Soft Skill 3, Soft Skill 4
**OUTPUT FORMAT:END**
**EXAMPLE:START**
OUTPUT EXAMPLE 1:
[0]Skills:
[1]Programming Languages: Python, JavaScript
[1]Technical Skills: REST APIs, Web Development, API Development, Cloud Setup
[1]Soft Skills: Collaboration, Communication, Leadership, Teamwork
**EXAMPLE:END**
**INPUT:START**
INPUT list of "Programming Languages", "Technical Skills" and "Soft Skills" considered to be relevant for a paticular job description:
{cv_data}

INPUT job description:
{job_description}

**INPUT:END**
""",
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["strict", "digits", "[0]Skills:","[1]Programming Languages:","[1]Technical Skills:","[1]Soft Skills:"]
    },
    "new_vs_old_section": #DONE
    {
        "call_id": "new_vs_old_section",
        "payload_in": {
            "model": DEFAULT_MODEL,
            "system": "",
            "stream": False,
            "temperature": CONFIG["MODELS"]["TEMPERATURE"]
        },
        "format": {
            "old_resume_s_txt": "",
            "new_resume_s_txt": "",
            "section_name": ""
        },
        "prompt_in": 
"""**REQUEST:START**
Given a raw untailored resume section and and its counterpart from an already tailored resume, compare the two resume sections and:
- Confirm that the tailored section does not contain any made-up information.
- Verify that all information in the tailored section is present in the raw section, even if paraphrased.
- Identify any contradictions between the two sections.
- Identify any contradictions within the tailored section (with itself).
- Return the requested information, strictly filling out the OUTPUT FORMAT and following the included OUTPUT EXAMPLES.
**REQUEST:END**
**OUTPUT FORMAT:START**
[0]{section_name} Analysis: Analysis of the tailored resume section vs the raw section, as a single line of text.
**OUTPUT FORMAT:END**
**EXAMPLE:START**
EXAMPLE OUTPUT 1:
[0] Volunteering_and_Leadershio Analysis: The tailored version of the section presents one inconsistency with the raw section, the role "Team Lead at the 2024 IBM Datathon" does not exit in the raw resume. Aside from that, everything else is consistent.
**EXAMPLE:END**
**INPUT:START**
INPUT raw untailored resume section:
{old_resume_s_txt}

INPUT already tailored resumesection:
{new_resume_s_txt}

**INPUT:END**
""",
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["strict", "digits", "[0]"]
    },
    "make_cover_letter_text": #DONE
    {
        "call_id": "make_cover_letter_text",
        "payload_in": {
            "model": DEFAULT_MODEL,
            "system": "",
            "stream": False,
            "temperature": CONFIG["MODELS"]["TEMPERATURE"]
        },
        "format": {
            "cv_data": "",
            "job_description": ""
        },
        "prompt_in": 
"""**REQUEST:START**
Given a wholistic summary of a resume, and the summary of the job description it has been tailored to, write a cover letter tailored to the job description, following the guidelines below:
- It should highlight the most relevant skills and experiences from the resume that match the job description.
- It should be written in a professional tone.
- Do not invent information or experiences, only include what is present in the resume.
- Do not make use of run-on sentences.
- The only line breaks allowed are those that separate paragraphs, as per the format below.
- Only 4 paragraphs are allowed, each starting with "[1]New ParagraphX: " and then the text of the new paragraph; X starts at 0 and goes up to 3.
- Total word count must not exceed 400 words. This is a hard limit, so be concise and to the point.
- Write the cover letter as the candidate, not as an external observer.
- Return the requested information, strictly filling out the OUTPUT FORMAT and following the included OUTPUT EXAMPLES.
**REQUEST:END**
**OUTPUT FORMAT:START**
[0]Cover Letter: 
[1]New Paragraph0: Cover Letter introduction, mentioning the job title and company, as well as the candidate's enthusiasm for the role.
[1]New Paragraph1: Explain why the candidate is a good fit for the role, briefly mentioning the most relevant information from the resume that matches the job description.
[1]New Paragraph2: Provide further information about the candidate's qualifications and how they align with the job requirements. Make use of specific examples and metrics to demonstrate impact (if applicable).
[1]New Paragraph3: Closing statement, thanking the employer for their time and consideration. Invite them to contact the candidate for further discussion, providing email address.
**OUTPUT FORMAT:END**
**EXAMPLE:START**
EXAMPLE OUTPUT 1:
[0]Cover Letter:
[1]New Paragraph0: I am excited to apply for the Software Engineer, New Grad role at Sentry, a position that aligns perfectly with my skills and passion for software development. As a seasoned Senior Software Engineer, I am confident in my ability to make a meaningful contribution to your team.
[1]New Paragraph1: With my strong educational foundation in M.Sc. Software Engineering and B.Sc. Computer Science, I possess the technical skills required for this role. My proficiency in Python and JavaScript, as well as my experience developing microservices and collaborating with cross-functional teams, make me a strong fit for this position.
[1]New Paragraph2: As a leader, I have demonstrated exceptional mentorship as a Coding Bootcamp Mentor at CodeSpring, resulting in high completion rates and job placement improvement. This experience has honed my ability to communicate effectively with teams and stakeholders, which is essential for this role. Additionally, my portfolio showcases the creation of a real-time analytics dashboard using Python, featuring role-based access controls and security features for sensitive data protection.
[1]New Paragraph3: Thank you for considering my application. I am excited about the opportunity to discuss how my skills and experience align with the requirements of this role. Please feel free to contact me at jane.doe@email.com or via LinkedIn.
**EXAMPLE:END**
**INPUT:START**
INPUT wholistic summary of a resume:
{cv_data}

INPUT summary of the job description it has been tailored to:
{job_description}

**INPUT:END**
""",
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["strict", "digits", "[0]Cover Letter:", "[1]New Paragraph0:", "[1]New Paragraph1:", "[1]New Paragraph2:", "[1]New Paragraph3:"]
    },
    "consistency_checker_vs_job_desc_cv": #DONE
    {
        "call_id": "consistency_checker_vs_job_desc_cv",
        "payload_in": {
            "model": DEFAULT_MODEL,
            "system": "",
            "stream": False,
            "temperature": CONFIG["MODELS"]["TEMPERATURE"]
        },
        "format": {
            "cv_data": "",
            "job_description": ""
        },
        "prompt_in": 
"""**REQUEST:START**
Given the a summary of a resume and the job description the aforementioned resume has been tailored to, perform a consistency check on the tailored resume against the job description. This consistency check will check if the resume is consistent with the job description, meaning that all skills and experiences mentioned in the resume should be relevant to the job description.
Follow these guidelines:
- Be mindful not to include any line breaks in the content of any of the sections/subsections.
- Be as objective as possible, and do not make any assumptions about the data.
- Do not create nor imagine any data that is not present in the original data.
- When filling out the output format, include the numbers "[0]", "[1]", and do not modify the format.
- Return the requested information, strictly filling out the OUTPUT FORMAT and following the included OUTPUT EXAMPLES.
**REQUEST:END**
**OUTPUT FORMAT:START**
[0]Consistency Checker Vs Job Description:
[1]Inconsistencies With Job Description: Number of inconsistencies found (return 'None' if no inconsistencies). List of inconsistencies found, if any, must be a continuous block of text, composed of sentences separated by ";", not line breaks.
[1]Suggestions for Improvement: List of suggestions for improvement, if any (return 'None' if no suggestions). must be a continuous block of text, composed of sentences separated by ";", not line breaks.
**OUTPUT FORMAT:END**
**EXAMPLE:START**
EXAMPLE OUTPUT 1:
[0]Consistency Checker Vs Job Description:
[1]Inconsistencies With Job Description: None.
[1]Suggestions for Improvement: None.
EXAMPLE OUTPUT 2:
[0]Consistency Checker Vs Job Description:
[1]Inconsistencies With Job Description: 1 inconsistency found. The position "Secretary at WayCom" is irrelevant to the job description with job title "Senior VXF Animator" because of the mismatch in skillsets required. 
[1]Suggestions for Improvement: Correct the above inconsistencies; The skill "VFX Software" is missing from the resume summary, it would be wise to include it if the candiate has it.
**EXAMPLE:END**
**INPUT:START**
INPUT summary of a resume tailored to a particular job description:
{cv_data}
INPUT job description the aforementioned resume has been tailored to:
{job_description}
**INPUT:END**
""",
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["strict", "digits", "[0]Consistency Checker Vs Job Description:", "[1]Inconsistencies With Job Description:", "[1]Suggestions for Improvement:"]
    },
    "consistency_checker_vs_job_desc_cl": #DONE
    {
        "call_id": "consistency_checker_vs_job_desc_cl",
        "payload_in": {
            "model": DEFAULT_MODEL,
            "system": "",
            "stream": False,
            "temperature": CONFIG["MODELS"]["TEMPERATURE"]
        },
        "format": {
            "cv_data": "",
            "job_description": ""
        },
        "prompt_in": 
"""**REQUEST:START**
Given a cover letter and the job description the aforementioned cover letter has been tailored to, perform a consistency check on the tailored cover letter against the job description. This consistency check will check if the cover letter is consistent with the job description, meaning that all skills and experiences mentioned in the cover letter should be relevant to the job description.
Follow these guidelines:
- Be mindful not to include any line breaks in  the content of any of the sections/subsections.
- Be as objective as possible, and do not make any assumptions about the data.
- Do not create nor imagine any data that is not present in the original data.
- When filling out the output format, include the numbers "[0]", "[1]", and do not modify the format.
- Return the requested information, strictly filling out the OUTPUT FORMAT and following the included OUTPUT EXAMPLES.
**REQUEST:END**
**OUTPUT FORMAT:START**
[0]Consistency Checker Vs Job Description:
[1]Inconsistencies With Job Description: Number of inconsistencies found (return 'None' if no inconsistencies). List of inconsistencies found, if any, must be a continuous block of text, composed of sentences separated by ";", not line breaks.
[1]Suggestions for Improvement: List of suggestions for improvement, if any (return 'None' if no suggestions). must be a continuous block of text, composed of sentences separated by ";", not line breaks.
**OUTPUT FORMAT:END**
**EXAMPLE:START**
EXAMPLE OUTPUT 1:
[0]Consistency Checker Vs Job Description:
[1]Inconsistencies With Job Description: None.
[1]Suggestions for Improvement: None.
EXAMPLE OUTPUT 2:
[0]Consistency Checker Vs Job Description:
[1]Inconsistencies With Job Description: 2 inconsistencies found. The position the cover letter is referring to is incorrect, it should be "Junior Engineer at GTY" not "Senior Software Engineer at GTY"; The email address has field has been left as a placeholder.
[1]Suggestions for Improvement: Correct the above inconsistencies; Consider not mentioning irrelevant positions, such as "Ice Cream Machine Operator" or "Zoo Ticket Salesman"
**EXAMPLE:END**
**INPUT:START**
INPUT cover letter tailored to a particular job description:
{cv_data}
INPUT job description the aforementioned resume has been tailored to:
{job_description}
**INPUT:END**
""",
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["strict", "digits", "[0]Consistency Checker Vs Job Description:", "[1]Inconsistencies With Job Description:", "[1]Suggestions for Improvement:"]
    },
    "tailor_courses": #DONE
    {
        "call_id": "tailor_courses",
        "payload_in": {
            "model": DEFAULT_MODEL,
            "system": "",
            "stream": False,
            "temperature": CONFIG["MODELS"]["TEMPERATURE"]
        },
        "format": {
            "courses": "",
            "job_description": ""
        },
        "prompt_in": 
"""**REQUEST:START**
Given a list of courses taken on a given program and a job description, extract the 5 most relevant courses that match the skills and requirements outlined in the job description.
Follow these guidelines when extracting courses and returning them:
- Do not include any courses not present in the original courses list.
- Do not use line breaks inside any subsection.
- Courses must be comma-separated and follow the format below.
- Include the prefix [1] at the start of each line (as seen in the format below).
- Return the requested information, strictly filling out the OUTPUT FORMAT and following the included OUTPUT EXAMPLES.
- Be mindful that courses may or may not have a course code (represented by "XXX001" in the OUTPUT FORMAT section)
**REQUEST:END**
**OUTPUT FORMAT:START**
[1]Courses: XXX001 Course Name1, XXX002 Course Name2, XXX003 Course Name3...
**OUTPUT FORMAT:END**
**EXAMPLE:START**
[1]Courses: CSC101 Computer Science I, ECE201 Introduction to Electronics, CIV301 Advanced Civil Engineering, MAT 323 Applied Advanced Calculus
**EXAMPLE:END**
**INPUT:START**
INPUT list of courses taken on a given program:
{courses}

INPUT job description:
{job_description}

**INPUT:END**
""",
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["strict", "digits", "[1]Courses:"]
    },
    # NON-STANDARD CALLS
    "batch_summarize_sections": {
        "call_id": "batch_summarize_sections",
        "payload_in": {
            "model": DEFAULT_MODEL,
            "system": "",
            "stream": False,
            "temperature": CONFIG["MODELS"]["TEMPERATURE"]
        },
        "format": {
            "sections": [],
            "section_names": []
        },
        "prompt_in": 
"""Given the following sections from a resume:
{sections_text}
Summarize the sections in a wholistic manner while following these guidelines:
- Be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
- Include all information, competencies, achievements, and skills, this is a wholistic summary of the candidate's qualifications.
- Keep in mind that these summaries will be used in a "Sliding Window" approach to summarize the entire resume effectively, so include information that is relevant for the overall context of the resume.
Return the summarized information as a single continuous string of text, following this format strictly:
""",
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["flexible", "cap_letters", "[S]"]
    },
    ##similar start
    "tailor_volunteering_and_leadership": #DONE
    {
        "call_id": "tailor_volunteering_and_leadership", 
        "payload_in": {"model": DEFAULT_MODEL,
                       "system": "",
                       "stream": False,
                         "temperature": CONFIG["MODELS"]["TEMPERATURE"]}, 
        "format": {
            "raw_cv_data": "",
            "job_description_summary": "",
            "section": "volunteering_and_leadership",
            "reference_dct": {},
            "systems": ["", ""],
            "standard_calls": ["step0_volunteering_and_leadership","step3_volunteering_and_leadership"]
            }, 
        "prompt_in": "", 
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["flexible", "digits", "[0]", "[1]"]
    },
    "tailor_work_experience": #DONE
    {
        "call_id": "tailor_work_experience", 
        "payload_in": {"model": DEFAULT_MODEL,
                       "system": "",
                       "stream": False,
                         "temperature": CONFIG["MODELS"]["TEMPERATURE"]}, 
        "format": {
            "raw_cv_data": "",
            "job_description_summary": "",
            "section": "work_experience",
            "reference_dct": {},
            "systems": ["", ""],
            "standard_calls": ["step0_work_experience","step3_work_experience"]
            }, 
        "prompt_in": "", 
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["flexible", "digits", "[0]", "[1]"]
    },
    "tailor_projects": #DONE
    {
        "call_id": "tailor_projects", 
        "payload_in": {"model": DEFAULT_MODEL,
                       "system": "",
                       "stream": False,
                       "temperature": CONFIG["MODELS"]["TEMPERATURE"]}, 
        "format": {
            "raw_cv_data": "",
            "job_description_summary": "",
            "section": "projects",
            "reference_dct": {},
            "systems": ["", ""],
            "standard_calls": ["step0_projects","step3_projects"]
            }, 
        "prompt_in": "", 
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["flexible", "digits", "[0]", "[1]"]
    },
    ##similar end
    ##similar start
    "sliding_window_two_sections": #DONE
    {
        "call_id": "sliding_window_two_sections", 
        "payload_in": {
            "model": DEFAULT_MODEL,
            "system": "",
            "stream": False,
            "temperature": CONFIG["MODELS"]["TEMPERATURE"]}, 
        "format": {
            "sections" : ["", ""],
            "section_names":  ["", ""],
            "systems": ["", ""],
            "candidate_name": "",
            "candidate_title":"",
            "mode": "single", 
            "standard_calls": ["summarize_section"],
            "non_standard_calls":["batch_summarize_sections"],
            "async_calls": ["standard_ollama_call_async"]
            }, 
        "prompt_in": 
"""**REQUEST:START**
Given 2 resume section summaries, create a new summary that incorporates all two summaries, following these guidelines:
- Be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
- Include ALL information, competencies, achievements, and skills, for this is a wholistic summary of the candidate's qualifications. Do not miss any skills.
- When referring to the candidate, use their name: {candidate_name} or their title: {candidate_title}
- Return the requested information, strictly filling out the OUTPUT FORMAT and following the included OUTPUT EXAMPLES.
**REQUEST:END**
**OUTPUT FORMAT:START**
[S]{section1_name} + {section2_name} Sections Summary: Wholistic summary of the sections' information, competencies, achievements, and skills.
**OUTPUT FORMAT:END**
**EXAMPLE:START**
EXAMPLE INPUT 1 (candidate name is Jane Doe and her Title is Software Engineer):
[S]awards_and_scholarships Section Summary: Achieved Dean's List at Springfield University (2015/06) and received Tech Innovation Scholarship from Capital Tech (2017/09), demonstrating academic excellence and innovation skills.
[S]volunteering_and_leadership Section Summary: As a Coding Bootcamp Mentor at CodeSpring (2020/01-2022/12),  developed curriculum modules and workshops on Python, REST APIs, and cloud integration (Python, Javascript); As a Hackathon Organizer at TechFest (2018/03-2019/03), managed large-scale events (hackathon) and fostered a culture of innovation and collaboration for creative problem solving (Strong Leadership, Organizational and Communication skills).
EXAMPLE OUTPUT 1:
[S]awards_and_scholarships + volunteering_and_leadership Sections Summary: Jane Doe is a prolific Software Engineer, having achieved Dean's List at Springfield University (2015/06) and received Tech Innovation Scholarship from Capital Tech (2017/09), demonstrating academic excellence and innovation skills. As a Coding Bootcamp Mentor at CodeSpring (2020/01-2022/12),  she developed curriculum modules and workshops on Python, REST APIs, and cloud integration (Python, Javascript); As a Hackathon Organizer at TechFest (2018/03-2019/03), she managed large-scale events (hackathon) and fostered a culture of innovation and collaboration for creative problem solving (Strong Leadership, Organizational and Communication skills).
**INPUT:START**
INPUT {section1_name} section summary:
{summary1}

INPUT {section2_name} section summary:
{summary2}

**INPUT:END**
""", #Set at runtime
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["strict", "cap_letters", "[S]"]#Might lead to error, check later
    },
    "sliding_window_three_sections": #DONE
    {
        "call_id": "sliding_window_three_sections", 
        "payload_in": {
            "model": DEFAULT_MODEL,
            "system": "",
            "stream": False,
            "temperature": CONFIG["MODELS"]["TEMPERATURE"]}, 
        "format": {
            "sections" : ["", "", ""],
            "section_names":  ["", "", ""],
            "systems": ["", "", ""],
            "candidate_name": "",
            "candidate_title":"",
            "mode": "single", 
            "standard_calls": ["summarize_section"],
            "non_standard_calls":["batch_summarize_sections"],
            "async_calls": ["standard_ollama_call_async"]
            }, 
        "prompt_in": 
"""**REQUEST:START**
Given 3 resume section summaries, create a new summary that incorporates all two summaries, following these guidelines:
- Be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
- Include ALL information, competencies, achievements, and skills, for this is a wholistic summary of the candidate's qualifications. Do not miss any skills.
- When referring to the candidate, use their name: {candidate_name} or their title: {candidate_title}
- Return the requested information, strictly filling out the OUTPUT FORMAT and following the included OUTPUT EXAMPLES.
**REQUEST:END**
**OUTPUT FORMAT:START**
[S]{section1_name} + {section2_name} + {section3_name} Sections Summary: Wholistic summary of the sections' information, competencies, achievements, and skills.
**OUTPUT FORMAT:END**
**EXAMPLE:START**
EXAMPLE INPUT 1 (candidate name is Jane Doe and her Title is Software Engineer):
[S]education Section Summary: This candidate holds a Bachelor of Science in Computer Science from Springfield University (2012-2016), with courses in Algorithms, Data Structures, Operating Systems, and Databases. They then pursued a Master of Science in Software Engineering at Capital Tech (2016-2018), focusing on Cloud Computing, Distributed Systems, and Advanced Programming.
[S]certifications Section Summary: This candidate is certified as an AWS Certified Solutions Architect (2019) and holds the Scrum Master certification from the Scrum Alliance (2020).
[S]awards_and_scholarships Section Summary: Achieved Dean's List at Springfield University (2015/06) and received Tech Innovation Scholarship from Capital Tech (2017/09), demonstrating academic excellence and innovation skills.
EXAMPLE OUTPUT 1:
[S]education + certifications + awards_and_scholarships Sections Summary:As a highly skilled Senior Software Engineer, Jane Doe holds a Bachelor of Science in Computer Science from Springfield University (2012-2016), with courses in Algorithms, Data Structures, Operating Systems, and Databases. She then pursued a Master of Science in Software Engineering at Capital Tech (2016-2018), focusing on Cloud Computing, Distributed Systems, and Advanced Programming. Additionally, Jane Doe is certified as an AWS Certified Solutions Architect (2019) and holds the Scrum Master certification from the Scrum Alliance (2020). Her academic achievements include achieving Dean's List at Springfield University (2015/06) and receiving Tech Innovation Scholarship from Capital Tech (2017/09), demonstrating academic excellence and innovation skills.
**INPUT:START**
INPUT {section1_name} section summary:
{summary1}

INPUT {section2_name} section summary:
{summary2}

INPUT {section3_name} section summary:
{summary3}

**INPUT:END**
""", #Set at runtime
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["strict", "cap_letters", "[S]"]#Might lead to error, check later
    },
    "sliding_window_four_sections": #DONE
    {
        "call_id": "sliding_window_four_sections", 
        "payload_in": {
            "model": DEFAULT_MODEL,
            "system": "",
            "stream": False,
            "temperature": CONFIG["MODELS"]["TEMPERATURE"]}, 
        "format": {
            "sections" : ["", "", "", ""],
            "section_names":  ["", "", "", ""],
            "systems": ["", "", "", ""],
            "candidate_name": "",
            "candidate_title":"",
            "mode": "single", 
            "standard_calls": ["summarize_section"],
            "non_standard_calls":["batch_summarize_sections"],
            "async_calls": ["standard_ollama_call_async"]
            }, 
        "prompt_in": 
"""**REQUEST:START**
Given 4 resume section summaries, create a new summary that incorporates all two summaries, following these guidelines:
- Be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
- Include ALL information, competencies, achievements, and skills, for this is a wholistic summary of the candidate's qualifications. Do not miss any skills.
- When referring to the candidate, use their name: {candidate_name} or their title: {candidate_title}
- Return the requested information, strictly filling out the OUTPUT FORMAT and following the included OUTPUT EXAMPLES.
**REQUEST:END**
**OUTPUT FORMAT:START**
[S]{section1_name} + {section2_name} + {section3_name} + {section4_name} Sections Summary: Wholistic summary of the sections' information, competencies, achievements, and skills.
**OUTPUT FORMAT:END**
**EXAMPLE:START**
EXAMPLE INPUT 1 (candidate name is Jane Doe and her Title is Software Engineer):
[S]education Section Summary: This candidate holds a Bachelor of Science in Computer Science from Springfield University (2012-2016), with courses in Algorithms, Data Structures, Operating Systems, and Databases. They then pursued a Master of Science in Software Engineering at Capital Tech (2016-2018), focusing on Cloud Computing, Distributed Systems, and Advanced Programming.
[S]certifications Section Summary: This candidate is certified as an AWS Certified Solutions Architect (2019) and holds the Scrum Master certification from the Scrum Alliance (2020).
[S]awards_and_scholarships Section Summary: Achieved Dean's List at Springfield University (2015/06) and received Tech Innovation Scholarship from Capital Tech (2017/09), demonstrating academic excellence and innovation skills.
[S]volunteering_and_leadership Section Summary: Developed strong leadership, mentoring, and organizational skills through roles as Coding Bootcamp Mentor at CodeSpring (2020/01-2022/12) and Hackathon Organizer at TechFest (2018/03-2019/03), fostering innovation, collaboration, and creativity while utilizing problem-solving skills.
EXAMPLE OUTPUT 1:
[S]education + certifications + awards_and_scholarships + volunteering_and_leadership Sections Summary:As a highly skilled Senior Software Engineer, Jane Doe holds a Bachelor of Science in Computer Science from Springfield University (2012-2016), with courses in Algorithms, Data Structures, Operating Systems, and Databases. She then pursued a Master of Science in Software Engineering at Capital Tech (2016-2018), focusing on Cloud Computing, Distributed Systems, and Advanced Programming. Additionally, Jane Doe is certified as an AWS Certified Solutions Architect (2019) and holds the Scrum Master certification from the Scrum Alliance (2020). Her academic achievements include achieving Dean's List at Springfield University (2015/06) and receiving Tech Innovation Scholarship from Capital Tech (2017/09), demonstrating academic excellence and innovation skills. With strong leadership, mentoring, and organizational skills, Jane Doe has developed a reputation as a leader through roles such as Coding Bootcamp Mentor at CodeSpring (2020/01-2022/12) and Hackathon Organizer at TechFest (2018/03-2019/03), fostering innovation, collaboration, and creativity while utilizing problem-solving skills.
**INPUT:START**
INPUT {section1_name} section summary:
{summary1}

INPUT {section2_name} section summary:
{summary2}

INPUT {section3_name} section summary:
{summary3}

INPUT {section4_name} section summary:
{summary4}

**INPUT:END**
""", #Set at runtime
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["strict", "cap_letters", "[S]"]#Might lead to error, check later
    },
    ##similar end
    "prune_experiences": #DONE
    {
        "call_id": "prune_experiences", 
        "payload_in": {"model": DEFAULT_MODEL,
                       "system": "",
                       "stream": False,
                       "temperature": CONFIG["MODELS"]["TEMPERATURE"]}, 
        "format": {
            "experiences": "",
            "job_description_summary": "",
            "section": "vl_w_p",
            "reference_dct": {}, #provide system through payload_in
            "standard_calls": ["step0_prune_experiences"]
            }, 
        "prompt_in": "", #Empty
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["flexible", "digits", "[0]", "[1]"]#Might lead to error, check later
    },
    "slide_summary": #DONE
    {
        "call_id": "slide_summary", 
        "payload_in": {"model": DEFAULT_MODEL, #model=DEFAULT_MODEL,
                        "system": "", # #system="",
                        "stream": False,
                        "temperature": CONFIG["MODELS"]["TEMPERATURE"]}, 
        "format": {
            "sections_dct_list" : [], #sections_dct_list=[]
            "systems": [], #(min size: 3) system1="", system2="", system3="", system4="", system_s="",
            "skill_section": False, #skill_section=False,
            "windows":2, #windows=2,
            "mode": "single", #mode="single"
            "standard_calls": ["summarize_general_info", "summarize_skills"],
            "non_standard_calls": ["sliding_window_two_sections",
                                    "sliding_window_three_sections",
                                    "sliding_window_four_sections"],
        }, 
        "prompt_in": "", #Empty
        "ollama_url": DEFAULT_URL, #ollama_url=DEFAULT_URL,
        "sample_starts": [] #Empty
    },
    "step0_tailor_summary": #DONE
    {
        "call_id": "step0_tailor_summary", 
        "payload_in": {"model": DEFAULT_MODEL, #model=DEFAULT_MODEL,
                        "system": "", # #system="",
                        "stream": False,
                        "temperature": CONFIG["MODELS"]["TEMPERATURE"]}, 
        "format": {
            "raw_cv_data" : "", #raw_cv_data = ""
            "systems": [], #(min size: 4) , system0 = "", system1 = "", system2 = "", system3 = "", system4 = "",system_s = ""
            "skill_section": False, #skill_section=False,
            "windows":2, #windows=2,
            "mode": "single", #mode="single"
            "standard_calls": [],
            "non_standard_calls": ["slide_summary"],
        }, 
        "prompt_in": 
"""**REQUEST:START**
Given all summarized sections of a resume, create a wholistic summary of all of them, following these guidelines:
- Include the candidate's contact information, as well as their title and name.
- Include any certifications or qualifications.
- Include all education.
- Include all projects, work experience, and volunteering and leadership roles.
- Include all information, competencies, achievements, and skills, this is a wholistic summary of the candidate's qualifications.
- Maintain the context and flow between the sections.
- Be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
- When filling out the output format, do not forget to include the "[0]Summary:" text before the actual summary.
- Return the requested information, strictly filling out the OUTPUT FORMAT and following the included OUTPUT EXAMPLES.
**REQUEST:END**
**OUTPUT FORMAT:START**
[0]Summary: Wholistic summary of all sections, presented as a single continuous string of text.
**OUTPUT FORMAT:END**
**EXAMPLE:START**
EXAMPLE INPUT 1:
INPUT summarized sections of a resume:
[S]General Information Summary: Jane Doe is a Senior Software Engineer with contact details including an address at 123 Main St, Springfield, USA, phone number +1-555-123-4567, email jane.doe@email.com, LinkedIn linkedin.com/in/janedoe, Github github.com/janedoe, and Portfolio janedoe.dev. Jane speaks English, Spanish, and French fluently.
[S]Education + Certifications + Awards_and_Scholarships + Volunteering_and_Leadership Sections Summary:As a highly skilled Senior Software Engineer, Jane Doe holds a Bachelor of Science in Computer Science from Springfield University (2012-2016), with courses in Algorithms, Data Structures, Operating Systems, and Databases. She then pursued a Master of Science in Software Engineering at Capital Tech (2016-2018), focusing on Cloud Computing, Distributed Systems, and Advanced Programming. Additionally, Jane Doe is certified as an AWS Certified Solutions Architect (2019) and holds the Scrum Master certification from the Scrum Alliance (2020). Her academic achievements include achieving Dean's List at Springfield University (2015/06) and receiving Tech Innovation Scholarship from Capital Tech (2017/09), demonstrating academic excellence and innovation skills. With strong leadership, mentoring, and organizational skills, Jane Doe has developed a reputation as a leader through roles such as Coding Bootcamp Mentor at CodeSpring (2020/01-2022/12) and Hackathon Organizer at TechFest (2018/03-2019/03), fostering innovation, collaboration, and creativity while utilizing problem-solving skills.
[S]Certifications + Awards_and_Scholarships + Volunteering_and_Leadership + Work_Experience Sections Summary: As a seasoned Senior Software Engineer Jane Doe, distinguished by certifications in AWS Certified Solutions Architect (Amazon Web Services, 2019) and Scrum Master (Scrum Alliance, 2020), demonstrating expertise in cloud architecture and agile methodologies. Notably, academic excellence is showcased through Dean's List at Springfield University (2015) and Tech Innovation Scholarship from Capital Tech (2017). As a dedicated mentor and organizer, Jane excels in Python, REST APIs, cloud integration, event planning, and teamwork, driving high completion rates, improving job placement, and delivering high-quality events. Proficient in mentoring, communication, leadership, problem-solving, and innovation. With a strong background in Python, JavaScript, API development, microservices, Docker, and Kubernetes, Jane consistently improves application performance, collaborates with cross-functional teams, and contributes to technology adoption.
[S]Awards_and_Scholarships + Volunteering_and_Leadership + Work_Experience + Projects Sections Summary: Senior Software Engineer Jane Doe is a highly accomplished professional with exceptional academic and professional achievements. With a strong foundation in innovation, demonstrated through Dean's List at Springfield University (2015) and Tech Innovation Scholarship at Capital Tech (2017), Jane has leveraged her expertise to excel in software engineering, leadership, and mentoring. As a seasoned engineer at WebApps Inc., she has honed skills in RESTful API development, optimizing database queries, and microservices, delivering significant improvements in application performance by 30%. Outside of work, Jane has demonstrated exceptional leadership as Coding Bootcamp Mentor at CodeSpring (2020-2022) and Hackathon Organizer at TechFest (2018-2019), showcasing expertise in programming languages, technical skills, and soft skills like mentoring, communication, teamwork, problem-solving. Notably, Jane successfully led the creation of a real-time analytics dashboard using Python, incorporating role-based access controls and security features to protect sensitive data, solidifying her proficiency in Data Visualization, WebSockets, and communication.
[S]Skills Summary: Proficient in Microsoft Office Suite including Word, Excel, PowerPoint, and Outlook. Strong understanding of Google Workspace tools such as Gmail, Drive, Docs, Sheets, and Slides. Experience with project management using Asana and Trello. Possesses strong problem-solving skills and ability to work effectively in a fast-paced environment.
EXAMPLE OUTPUT 1:
[0]Summary:Jane Doe, Senior Software Engineer | +1-555-123-4567 | jane.doe@email.com | linkedin.com/in/janedoe | github.com/janedoe | janedoe.dev | Fluent in English, Spanish, and French.Certifications: AWS Certified Solutions Architect (2019), Scrum Master (2020).Education:Bachelor of Science in Computer Science from Springfield University (2012-2016) - courses in Algorithms, Data Structures, Operating Systems, and Databases.Master of Science in Software Engineering at Capital Tech (2016-2018) - focus on Cloud Computing, Distributed Systems, and Advanced Programming.Projects: Real-time analytics dashboard using Python, incorporating role-based access controls and security features to protect sensitive data, solidifying proficiency in Data Visualization, WebSockets, and communication.Work Experience:Senior Software Engineer at WebApps Inc. - RESTful API development, optimizing database queries, and microservices; delivered significant improvements in application performance by 30%.Volunteering & Leadership:Coding Bootcamp Mentor at CodeSpring (2020-2022) - mentoring and leadership skills.Hackathon Organizer at TechFest (2018-2019) - event planning, teamwork, and problem-solving.Skills: Proficient in Microsoft Office Suite, Google Workspace tools, Asana, Trello; strong problem-solving skills and ability to work effectively in a fast-paced environment.
**EXAMPLE:END**
**INPUT:START**
INPUT summarized sections of a resume:
{slides_txt}
**INPUT:END**
""",
        "ollama_url": DEFAULT_URL, #ollama_url=DEFAULT_URL,
        "sample_starts": ["strict", "digits", "[0]Summary:"]
    },
    "tailor_summary": #DONE
    {
        "call_id": "tailor_summary", 
        "payload_in": {"model": DEFAULT_MODEL, #model=DEFAULT_MODEL,
                        "system": "", # #system="",
                        "stream": False,
                        "temperature": CONFIG["MODELS"]["TEMPERATURE"]}, 
        "format": {
            "raw_cv_data" : "", #raw_cv_data = ""
            "systems": [], # system0="",system1="", system2="", system3="", system4="", system_s="",
                                        #system00="",system01="", (min 6)
            "skill_section": False, #skill_section=False,
            "job_description": "",
            "windows":2, #windows=2,
            "mode": "single", #mode="single"
            "standard_calls": ["step1_tailor_summary"],
            "non_standard_calls": ["step0_tailor_summary"],
        }, 
        "prompt_in": "",#Empty
        "ollama_url": DEFAULT_URL, #ollama_url=DEFAULT_URL,
        "sample_starts": ["strict", "digits", "[0]Summary:"]
    },
    "new_vs_old_resume": #DONE
    {
        "call_id": "new_vs_old_resume", 
        "payload_in": {"model": DEFAULT_MODEL, #model=DEFAULT_MODEL,
                        "system": "", # #system="",
                        "stream": False,
                        "temperature": CONFIG["MODELS"]["TEMPERATURE"]}, 
        "format": {
            "old_resume_txt" : "", #old_resume_txt = ""
            "new_resume_txt": "", # new_resume_txt = ""
            "standard_calls": ["new_vs_old_section"],
            "non_standard_calls": [],
        }, 
        "prompt_in": "",#Empty
        "ollama_url": DEFAULT_URL, #ollama_url=DEFAULT_URL,
        "sample_starts": ["flexible", "digits", "[0]"]
    },
    "consistency_checker_vs_cv_cv": #DONE
    {
        "call_id": "consistency_checker_vs_cv_cv", 
        "payload_in": {"model": DEFAULT_MODEL, #model=DEFAULT_MODEL,
                        "system": "", # #system="",
                        "stream": False,
                        "temperature": CONFIG["MODELS"]["TEMPERATURE"]}, 
        "format": {
            "cv_data" : "", #old_resume_txt = ""
            "cv_data_orig": "", # new_resume_txt = ""
            "system_s": "",
            "standard_calls": [],
            "non_standard_calls": ["new_vs_old_resume"],
        }, 
        "prompt_in": 
"""**REQUEST:START**
Given a list containing a per-section analysis of a two resumes, comparing the synthesized data in the new resume (which has been tailored to a particular job description) against the original, synthesize a report which extracts the following data from the list of analyses:
- Whether the new resume is consistent with the original resume, meaning that all information in the new resume is present in the original resume, even if paraphrased.
- Whether the new resume is consistent with itself, meaning that there should be no contradictions or inconsistencies in the information provided.
The report should follow these guidelines:
- Be mindful not to include any line breaks in  the content of any of the sections/subsections.
- Be as objective as possible, and if you must make assumptions, make very conservative assumptions
- Do not create nor imagine any data that is not present in the original data.
- When filling out the output format, include the numbers "[0]", "[1]", and do not modify the format.
- Return the requested information, strictly filling out the OUTPUT FORMAT and following the included OUTPUT EXAMPLES.
**REQUEST:END**
**OUTPUT FORMAT:START**
[0]Consistency Checker Vs Original Resume:
[1]Inconsistencies With Original Resume: Number of inconsistencies found (return 'None' if no inconsistencies). List of inconsistencies found, if any, must be a continuous block of text, composed of sentences separated by ";", not line breaks.
[1]Inconsistencies With Self: Number of inconsistencies found (return 'None' if no inconsistencies). List of inconsistencies found, if any, must be a continuous block of text, composed of sentences separated by ";", not line breaks.
[1]Suggestions for Improvement: List of suggestions for improvement, if any (return 'None' if no suggestions). must be a continuous block of text, composed of sentences separated by ";", not line breaks.
**OUTPUT FORMAT:END**
**EXAMPLE:START**
EXAMPLE OUTPUT 1:
[0]Consistency Checker Vs Original Resume:
[1]Inconsistencies With Original Resume: None.
[1]Inconsistencies With Self: None.
[1]Suggestions for Improvement: None.
EXAMPLE OUTPUT 2:
[0]Consistency Checker Vs Original Resume:
[1]Inconsistencies With Original Resume: 3 inconsistencies found with Original Resume. Position "Senior Engineer at AMD" found in tailored resume, missing in original; Wrong start date for position "Junior Engineer at NVidia", should be 10/2013 not 5/2024; URL for project "IoT at home" found in tailored resume, missing in original.
[1]Inconsistencies With Self: 1 inconsistency found. "Summary" section mentions a position not present under "Work Experience" (or any other section for that matter). 
[1]Suggestions for Improvement: Correct the above inconsistencies; Avoid the use of run-on sentences.
**EXAMPLE:END**
**INPUT:START**
INPUT list containing a per-section analysis of the resumes, comparing the synthesized data in the new resume against the original:
{all_analysis}
**INPUT:END**
""",
        "ollama_url": DEFAULT_URL, #ollama_url=DEFAULT_URL,
        "sample_starts": ["strict", "digits", "[0]Consistency Checker VS Original Resume:","[1]Inconsistencies With Original Resume:","[1]Inconsistencies With Self:", "[1]Suggestions for Improvement:"]
    },
    "compose_cover_letter_dictionary": #DONE
    {
        "call_id": "compose_cover_letter_dictionary", 
        "payload_in": {"model": DEFAULT_MODEL, #model=DEFAULT_MODEL,
                        "system": "", # #Empty
                        "stream": False,
                        "temperature": CONFIG["MODELS"]["TEMPERATURE"]}, 
        "format": {
            "cv_text_summary":"",
            "cv_text":"",
            "job_description":"",
            "standard_calls": ["make_cover_letter_text"],
            "non_standard_calls": [],
        }, 
        "prompt_in": "",#Empty
        "ollama_url": DEFAULT_URL, #ollama_url=DEFAULT_URL,
        "sample_starts": ["flexible", "digits", "[0]","[1]"]
    },
    #ASYNC
    "standard_ollama_call_async": #DONE
    {
        "call_id": "standard_ollama_call_async", 
        "payload_in": {
            "model": DEFAULT_MODEL,
            "system": "",
            "stream": False,
            "temperature": CONFIG["MODELS"]["TEMPERATURE"]}, 
        "format": {

            }, 
        "prompt_in": "", #Set at runtime
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["flexible", "cap_letters"]#Might lead to error, check later
    }

}
STANDARD= [
    "summarize_job_description",
    "step0_volunteering_and_leadership",
    "step3_volunteering_and_leadership",
    "step0_work_experience",
    "step3_work_experience",
    "step0_projects",
    "step3_projects",
    "step0_prune_experiences",
    "summarize_section",
    "summarize_general_info",
    "summarize_skills",
    "step1_tailor_summary",
    "tailor_skills",
    "new_vs_old_section",
    "make_cover_letter_text",
    "consistency_checker_vs_job_desc_cv",
    "consistency_checker_vs_job_desc_cl",
    "tailor_courses",
    "consistency_checker_vs_cv_cl"
]
ASYNC = [
    "standard_ollama_call_async"
]