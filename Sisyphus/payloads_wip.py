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
    "summarize_job_description": {
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
"""Summarize the following job description by extracting key responsibilities, requirements, and highlighting needed skills, both technical and soft.
Don't forget to also include the Company Name and the Job Title.
Job Description:
{job_description}
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
    "summarize_section": {
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
"""Given the following section from a resume:
{section}
Summarize the sections in a wholistic manner while following these guidelines:
- Be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
- Include all information, competencies, achievements, and skills, this is a wholistic summary of the candidate's qualifications.
Return the summarized information as a single continuous string of text, following this format strictly (do not forget to include the "[S]{section_name} Section Summary:" text at the start of the output):
[S]{section_name} Section Summary: Wholistic summary of the section's information.
""",
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["strict", "cap_letters", "[S]"]
    },
    "summarize_general_info": {
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
"""Given the following general information from a resume:
{general_info_text}
Summarize the general information section of a resume in a wholistic manner; be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
Since this is a summary of a resume's general information, you need to include the candidate's Name, Contact Information, Title, and Languages Spoken.
Return the summarized general information as follows (do not forget to include the "[S]General Information Summary:" text at the start of the output):
[S]General Information Summary: Brief and concise summary of the resume's general information, presented as a single continuous string of text.
""",
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["strict", "cap_letters", "[S]General Information Summary:"]
    },
    "summarize_skills": {
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
"""Given the following skills information from a resume:
{skill_section}
Summarize the skills section of a resume in a wholistic manner; be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
Return the summarized skills information as follows (do not forget to include the "[S]Skills Summary:" text at the start of the output):
[S]Skills Summary: Brief and concise wholistic summary of the resume's skills, presented as a single continuous string of text.
""",
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["strict", "cap_letters", "[S]Skills Summary:"]
    },
    "step1_tailor_summary": {
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
"""Given the following wholistic summary of a resume:
{prev_summary}
And the following job description:
{job_description}
Tailor a Summary section for a resume to best match the job description; follow these guidelines:
- Write the tailored summary section as the candidate, not as an external observer.
- The summary mustn't exceed 100 words.
- Do not line break the summary section, it should be a continuous block of text.
- When mentioning specific skills or experiences, these must be relevant to the job description; give preference to those that appear on both the resume and the job description, particularly those which demonstrate the candidate's technical expertise.
- In the format below, do not include any text before "[0]" or after the requested information.
Return only the revised section and strictly follow the format below, filling in the parts that have **fill-in:"text"**:
[0]Summary: Despite limited work experience, I bring strong work ethic, adaptability and curiosity. Experienced in **fill-in:"specific skills thanks to certain experiences"**. Now seeking a position that offers growth and learning opportunities.
""",
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["strict", "digits", "[0]Summary:"]
    },
    "tailor_skills": {
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
"""Given the following list of "Programming Languages", "Technical Skills" and "Soft Skills" considered to be relevant for the job description below them:
{cv_data}
And the following job description:
{job_description}
Prune the following 'Skills' section from a resume to best match the job description , following the guidelines below:
- Return 3 MAXIMUM entries under "Programming Languages" (MINIMUM 0 entries)
- Return 5 MAXIMUM entries under "Technical Skills" (MINIMUM 0 entries)
- Return 4 MAXIMUM entries under "Soft Skills" (MINIMUM 0 entries)
- Prioritize skills that are explicitly mentioned in the job description.
- For Soft Skills (only), prioritize skills mentioned in the job description, and if these skills are less than 4, fill the remaining slots with other relevant skills from the CV.
- Do not line break any line containing the relevant skills, it should follow the format below strictly.
- If either the "Programming Languages", "Technical Skills", or "Soft Skills" sections are empty, return them as an empty section.
- Aside from the information requested, do not include any additional text or explanations.
Return the revised information strictly following the format:
[0]Skills:
[1]Programming Languages: Programming Language 1, Programming Language 2, Programming Language 3
[1]Technical Skills: Technical Skill 1, Technical Skill 2, Technical Skill 3, Technical Skill 4, Technical Skill 5
[1]Soft Skills: Soft Skill 1, Soft Skill 2, Soft Skill 3, Soft Skill 4
""",
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["strict", "digits", "[0]Skills:","[1]Programming Languages:","[1]Technical Skills:","[1]Soft Skills:"]
    },
    "new_vs_old_section": {
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
"""Given the following raw untailored resume section:
{old_resume_s_txt}
And the following tailored resume section:
{new_resume_s_txt}
Compare the two resume sections and:
- Confirm that the tailored section does not contain any made-up information.
- Verify that all information in the tailored section is present in the raw section, even if paraphrased.
- Identify any contradictions between the two sections.
- Identify any contradictions within the tailored section (with itself).
Output your analysis as a single continuous string of text, strictly following the format below:
[0]{section_name} Analysis: Analysis of the tailored resume section vs the raw section.
""",
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["strict", "digits", "[0]"]
    },
    "make_cover_letter_text": {
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
"""Given the following wholistic summary of a resume:
{cv_data}
And the following summary of the job description it has been tailored to:
{job_description}
Write a cover letter tailored to the job description, following the guidelines below:
- It should highlight the most relevant skills and experiences from the resume that match the job description.
- It should be written in a professional tone.
- Do not invent information or experiences, only include what is present in the resume.
- Do not make use of run-on sentences.
- The only line breaks allowed are those that separate paragraphs, as per the format below.
- Only 4 paragraphs are allowed, each starting with "[1]New ParagraphX: " and then the text of the new paragraph; X starts at 0 and goes up to 3.
- Total word count must not exceed 400 words. This is a hard limit, so be concise and to the point.
- Write the cover letter as the candidate, not as an external observer.
Strictly follow the format:
[0]Cover Letter: 
[1]New Paragraph0: Cover Letter introduction, mentioning the job title and company, as well as the candidate's enthusiasm for the role.
[1]New Paragraph1: Explain why the candidate is a good fit for the role, briefly mentioning the most relevant information from the resume that matches the job description.
[1]New Paragraph2: Provide further information about the candidate's qualifications and how they align with the job requirements. Make use of specific examples and metrics to demonstrate impact (if applicable).
[1]New Paragraph3: Closing statement, thanking the employer for their time and consideration. Invite them to contact the candidate for further discussion, providing email address.
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
    "tailor_courses": {
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
"""Given the following courses taken on a given program:
{courses}
And the following job description:
{job_description}
Extract the 5 most relevant courses that match the skills and requirements outlined in the job description.
Follow these guidelines when extracting courses and returning them:
- Do not include any courses not present in the original courses list.
- Do not use line breaks inside any subsection.
- Courses must be comma-separated and follow the format below.
- Include the prefix [1] at the start of each line (as seen in the format below).
Return the list of courses in a single comma-separated line, strictly following the format below:
[1]Courses: XXX001 Course Name1, XXX002 Course Name2, XXX003 Course Name3...
Example output:
[1]Courses: CSC101 Computer Science I, ECE201 Introduction to Electronics, CIV301 Advanced Civil Engineering...
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
    "sliding_window_two_sections": {
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
"""Given the following resume section summaries:
{summary1}
{summary2}
Create a new summary that incorporates all two summaries, following these guidelines:
- Be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
- Include all information, competencies, achievements, and skills, this is a wholistic summary of the candidate's qualifications.
- Maintain the context and flow between the two sections.
- When referring to the candidate, use their name: {candidate_name} or their title: {candidate_title}
Return the summarized information as a single continuous string of text, following the format below strictly (do not forget to include the "[S] {section1_name} + {section2_name} Sections Summary:" text at the start of the output):
[S]{section1_name} + {section2_name} Sections Summary: Wholistic summary of the sections' information, competencies, achievements, and key skills.
""", #Set at runtime
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["strict", "cap_letters", "[S]"]#Might lead to error, check later
    },
    "sliding_window_three_sections": {
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
"""Given the following resume section summaries:
{summary1}
{summary2}
{summary3}
Create a new summary that incorporates all three summaries, following these guidelines:
- Be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
- Include all information, competencies, achievements, and skills, this is a wholistic summary of the candidate's qualifications.
- Maintain the context and flow between the three sections.
- When referring to the candidate, use their name: {candidate_name} or their title: {candidate_title}
Return the summarized information as a single continuous string of text, following the format below strictly (do not forget to include the "[S] {section1_name} + {section2_name} + {section3_name} Sections Summary:" text at the start of the output):
[S]{section1_name} + {section2_name} + {section3_name} Sections Summary: Wholistic summary of the sections' information, competencies, achievements, and key skills.
""", #Set at runtime
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["strict", "cap_letters", "[S]"]#Might lead to error, check later
    },
    "sliding_window_four_sections": {
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
"""Given the following resume section summaries:
{summary1}
{summary2}
{summary3}
{summary4}
Create a new summary that incorporates all four summaries, following these guidelines:
- Be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
- Include all information, competencies, achievements, and skills, this is a wholistic summary of the candidate's qualifications.
- Maintain the context and flow between the four sections.
- When referring to the candidate, use their name: {candidate_name} or their title: {candidate_title}
Return the summarized information as a single continuous string of text, following the format below strictly (do not forget to include the "[S] {section1_name} + {section2_name} + {section3_name} + {section4_name} Sections Summary:" text at the start of the output):
[S]{section1_name} + {section2_name} + {section3_name} + {section4_name} Sections Summary: Wholistic summary of the sections' information, competencies, achievements, and key skills.
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
    "step0_tailor_summary": {
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
**REQUEST:END**
**OUTPUT FORMAT:START**
[0]Summary: Wholistic summary of all sections, presented as a single continuous string of text.
**OUTPUT FORMAT:END**
**EXAMPLE:START**
EXAMPLE OUTPUT 1:
[0]Summary:
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