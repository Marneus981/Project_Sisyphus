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

REQUEST:

OUTPUT FORMAT:

INPUT:

- Return the requested information, strictly filling out the OUTPUT FORMAT.
field mode (digits/cap_letters) will be vestigial in next commit.


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
                   "cv_data_orig": "",
                   "prefix_dict": {
                       "Consistency Checker Vs Resume:":["[0]",False],
                       "Inconsistencies With Resume:":["[1]",True],
                       "Inconsistencies With Self:":["[1]",True],
                       "Suggestions for Improvement:":["[1]",True],
                       "Dummy:":["[BIG DUMMY]"]
                   }  
                   },
        "prompt_in": 
"""REQUEST:
Given a cover letter and a wholistic summary of a resume (both part of the same job application):
Perform a consistency check on the tailored cover letter against the resume. This consistency check should include:
- Whether the cover letter is consistent with the resume, meaning that all skills and experiences mentioned in the cover letter should be present in the resume.
- Whether the cover letter is consistent with itself, meaning that there should be no contradictions or inconsistencies in the information provided.
The report should follow these guidelines:
- Be mindful not to include any line breaks in  the content of any of the sections/subsections.
- Be as objective as possible, and if you must make assumptions, make very conservative assumptions
- Do not create nor imagine any data that is not present in the original data.
- Do not modify the output format.
- Return the requested information, strictly filling out the OUTPUT FORMAT.
- Do not forget to include the field names at the start of each line, as per the OUTPUT FORMAT.

OUTPUT FORMAT:
Consistency Checker Vs Resume:
Inconsistencies With Resume: Number of inconsistencies found (return 'None.' if no inconsistencies). List of inconsistencies found, if any, must be a continuous block of text, composed of sentences separated by ";", not line breaks.
Inconsistencies With Self: Number of inconsistencies found (return 'None.' if no inconsistencies). List of inconsistencies found, if any, must be a continuous block of text, composed of sentences separated by ";", not line breaks.
Suggestions for Improvement: List of suggestions for improvement, if any (return 'None.' if no suggestions). must be a continuous block of text, composed of sentences separated by ";", not line breaks.


INPUT:
INPUT cover letter:
{cv_data}

INPUT wholistic summary of the resume meant to accompany the above cover letter on a job application:
{cv_data_orig}

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
                   "job_description": "",
                   "prefix_dict": {
                       "Company Name:":["[0]",True],
                       "Job Title:":["[0]",True],
                       "Responsibilities:":["[0]",True],
                       "Requirements:":["[0]",True],
                       "Programming Languages:":["[0]",True],
                       "Technical Skills:":["[0]",True],
                       "Soft Skills:":["[0]",True],
                       "Keywords":["[0]",True],
                       "Dummy:":["[BIG DUMMY]"]
                   } 
                   },
        "prompt_in": 
"""REQUEST:
Summarize the input job description by extracting the following information in the format specified under the OUTPUT FORMAT section:
-Company Name
-Job Title
-Responsibilities
-Requirements
-Programming Languages
-Technical Skills
-Soft Skills
-Keywords
When filling out the OUTPUT FORMAT, follow these guidelines:
- Do not modify the format.
- Do not add any information not present in the provided job description, your goal is to extract information and summarize.
- Use simple and concise language when possible, but do use specific keywords.
- Return the requested information, strictly filling out the OUTPUT FORMAT.
- Do not forget to include the field names at the start of each line, as per the OUTPUT FORMAT.
On the "Keywords" section of the OUTPUT FORMAT, you have to include the following as single words or small phrases (less than 3 words long each):
- The job position (e.g. the job title)
- The name of technologies required (e.g. object oriented programming, etc)
- The specific name of programming languages required (e.g. java, etc) 
- Education required/preferred (e.g. bachelors of engineering)
- Soft skills preferred (e.g. good communication)
- Words abbreviated as capitalized acronyms (e.g. RMT, OOP, etc) 

OUTPUT FORMAT:
Company Name: Company Name
Job Title: Position Name
Responsibilities: List of responsabilities that come as part of the job, presented as a single line of text separated by ";"
Requirements: List of basic requirements, such as availability, education and required knowledge, presented as a single line of text separated by ";"
Programming Languages: List of required programming languages required for the position, presented as a single line of text separated by commas
Technical Skills: List of required technical required for the position skills, presented as a single line of text separated by commas. These are defined as all skills other than Soft Skills and Programming Languages needed
Soft Skills: List of required soft skills required for the position, presented as a single line of text separated by commas.
Keywords: List of keywords present in the job description, presented as a single line of lowercase text separated by ",". These keywords can be single words or small phrases (less than 3 words long) such as "good communication skills". 

INPUT:
INPUT job description:
{job_description}

""",
        "ollama_url": DEFAULT_URL, #Set at runtime
        "sample_starts": ["strict","digits", "[0]Company Name:","[0]Job Title:","[0]Responsibilities:","[0]Requirements:","[0]Programming Languages:","[0]Technical Skills:","[0]Soft Skills:","[0]Keywords:"] #[type, sample starts]
    },
    ##similar start
    "tailor_experience": #DONE
    {
        "call_id": "tailor_experience", 
        "payload_in": {
                       "model": DEFAULT_MODEL, #Set at runtime
                       "system": "",  #Set at runtime
                       "stream": False,
                       "temperature": CONFIG["MODELS"]["TEMPERATURE"]
                       },
        "format": {#Set at runtime
                   "job_keywords": "",
                   "experience": "",
                   "prefix_dict": {
                       "Description:":["[1]",True],
                       "Dummy:":["[BIG DUMMY]"]
                   } 
                   },
        "prompt_in": 
"""REQUEST:
Given a set of keywords and a "Description" subsection of a resume experience, rewrite the "Description" subsection following these guidelines:
- Rewrite the "Description" subsection to highlight the role description as achievements.
- Use 2 sentences (max 15 words each) as a single line of text separated by "." to fill the "Description" subsection; this is a hard requirement.
- From the list of keywords provided as INPUT, use those that are already present in the provided "Description" subsection. Do NOT use those that are not already present in the provided INPUT "Description" subsection.
- Do NOT use line breaks inside the text of any subsection. 
- Do NOT forget to include the field name "Description:" at the start of its respective lines, as per the OUTPUT FORMAT.
- Do NOT include any information not present in the "Description" subsection. 
- Return the requested information, strictly filling out the OUTPUT FORMAT below.

OUTPUT FORMAT:
Description: Brief role description, described as achievements meant to concisely provide recruiters with incentives to hire the candidate; written as a single line of text, with sentences separated by a "." character.

INPUT:
INPUT job description keywords:
{job_keywords}

INPUT "Description" subsection of a resume experience:
{experience}

""",
        "ollama_url": DEFAULT_URL, #Set at runtime
        "sample_starts": ["strict", "digits", "[1]Description:"]
    },
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
                   "job_description": "",
                    "prefix_dict": {
                        "Experience:" : ["[R]",True],
                        "Dummy:" : ["[BIG DUMMY]"]
                    }
                   },
        "prompt_in": 
"""REQUEST:
Given a "Volunteering and Leadership" resume section and a job description, select up to 5 roles based on the job description. When selecting:
- If the total number of roles is less than or equal to 5, return all of them.
- If the total number of roles is greater than or equal to 5 before selection: Select the most relevant 5 roles based on the job description.
- Do not change the name of the roles.
- Prioritize roles that match relevant skills and experience present in the job description.
- It is okay to not select any roles if none are relevant.
- Display the Role Titles explicitly and without changing them.
- When filling out the output format  you may not change the role title text, and do not include any text before or after the role title text.
- Return the requested information, strictly filling out the OUTPUT FORMAT.
- Do not forget to include the field names at the start of each line, as per the OUTPUT FORMAT.

OUTPUT FORMAT:
Experience:Role Title 1
Experience:Role Title 2
Experience:Role Title 3
Experience:Role Title 4
Experience:Role Title 5


INPUT:
INPUT "Volunteering and Leadership" resume section:
{raw_cv_data}
INPUT job description:
{job_description}

""",
        "ollama_url": DEFAULT_URL, #Set at runtime
        "sample_starts": ["flexible", "cap_letters", "[R]Experience:"]
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
                   "job_description": "",
                   "prefix_dict": {
                       "Description:":["[1]",True],
                       "Skills:":["[1]",True],
                       "Dummy:":["[BIG DUMMY]"]
                   } 
                   },
        "prompt_in": 
"""REQUEST:
Given the "Description" and "Skills" subsections of a role belonging to the "Volunteering and Leadership" section of a resume and a job description, rewrite the "Description" and "Skills" subsections following these guidelines:
- In the "Description" subsection:
    - Rewrite to highlight achievements and relevant skills, using up to 2 sentences (max 20 words each), as a single line of text.
- In the "Skills" subsection:
    - Select up to 6 skills relevant to the job description (Programming Languages, Technical Skills, Soft Skills). Every skill category should be present, even if empty.
    - Skills must be comma-separated and follow the format below.
    - If there are no skills in a given category, use " ", then follow up as the format below indicates 
        - For example: Programming Languages: ; Technical Skills: ; Soft Skills: Communication, Teamwork
- Prioritize using keywords found in both the job description and the "Description" and "Skills" sections (do not use keywords present solely in the job description since that would be a lie).
- Do NOT use line breaks inside the text of any subsection. 
- Do NOT forget to include the field names "Description:" and "Skills:" at the start of their respective lines, as per the OUTPUT FORMAT.
- Do NOT include any information not present in the "Description" and "Skills" subsections. 
- DO NOT include information that is present solely in the job description.
- Return the requested information, strictly filling out the OUTPUT FORMAT below

OUTPUT FORMAT:
Description: Brief role description.
Skills: Programming Languages: ...; Technical Skills: ...; Soft Skills: ...


INPUT:
INPUT job description:
{job_description}

INPUT "Description" and "Skills" attributes of a role belonging to the "Volunteering and Leadership" section of a resume:
{experience}

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
            "job_description": "",
            "prefix_dict": {
                "Experience:" : ["[J]",True],
                "Dummy:" : ["[BIG DUMMY]"]
            }
        },
        "prompt_in": 
"""REQUEST:
Given a "Work Experience" resume section and a job description, select up to 5 jobs based on the job description. When selecting:
- If the total number of jobs is less than or equal to 5, return all of them.
- If the total number of jobs is greater than or equal to 5 before selection: Select the most relevant 5 jobs based on the job description.
- Do not change the name of the jobs.
- Prioritize jobs that match relevant skills and experience present in the job description.
- It is okay to not select any jobs if none are relevant.
- Display the Job Titles explicitly and without changing them.
- When filling out the output format  you may not change the job title text, and do not include any text before or after the job title text.
- Return the requested information, strictly filling out the OUTPUT FORMAT.
- Do not forget to include the field names at the start of each line, as per the OUTPUT FORMAT.

OUTPUT FORMAT:
Experience:Job Title 1
Experience:Job Title 2
Experience:Job Title 3
Experience:Job Title 4
Experience:Job Title 5


INPUT:
INPUT "Work Experience" resume section:
{raw_cv_data}

INPUT job description:
{job_description}

""",
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["flexible", "cap_letters", "[J]Experience:"]
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
            "job_description": "",
            "prefix_dict": {
                       "Description:":["[1]",True],
                       "Skills:":["[1]",True],
                       "Dummy:":["[BIG DUMMY]"]
                   } 
        },
        "prompt_in": 
"""REQUEST:
Given the "Description" and "Skills" subsections of a role belonging to the "Work Experience" section of a resume and a job description, rewrite the "Description" and "Skills" subsections following these guidelines:
- In the "Description" subsection:
    - Rewrite to highlight achievements and relevant skills, using up to 2 sentences (max 20 words each), as a single line of text.
- In the "Skills" subsection:
    - Select up to 6 skills relevant to the job description (Programming Languages, Technical Skills, Soft Skills). Every skill category should be present, even if empty.
    - Skills must be comma-separated and follow the format below.
    - If there are no skills in a given category, use " ", then follow up as the format below indicates 
        - For example: Programming Languages: ; Technical Skills: ; Soft Skills: Communication, Teamwork
- Prioritize using keywords found in both the job description and the "Description" and "Skills" sections (do not use keywords present solely in the job description since that would be a lie).
- Do NOT use line breaks inside the text of any subsection. 
- Do NOT forget to include the field names "Description:" and "Skills:" at the start of their respective lines, as per the OUTPUT FORMAT.
- Do NOT include any information not present in the "Description" and "Skills" subsections. 
- DO NOT include information that is present solely in the job description.
- Return the requested information, strictly filling out the OUTPUT FORMAT below

OUTPUT FORMAT:
Description: Brief role description.
Skills: Programming Languages: ...; Technical Skills: ...; Soft Skills: ...


INPUT:
INPUT job description:
{job_description}

INPUT "Description" and "Skills" subsections of a role belonging to the "Work Experience" section of a resume:
{experience}

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
            "job_description": "",
            "prefix_dict": {
                "Experience:" : ["[P]",True],
                "Dummy:" : ["[BIG DUMMY]"]
            }
        },
        "prompt_in": 
"""REQUEST:
Given a "Projects" resume section and a job description, select up to 5 projects based on the job description. When selecting:
- If the total number of projects is less than or equal to 5, return all of them.
- If the total number of projects is greater than or equal to 5 before selection: Select the most relevant 5 projects based on the job description.
- Do not change the name of the projects.
- Prioritize projects that match relevant skills and experience present in the job description.
- It is okay to not select any projects if none are relevant.
- Display the Project Titles explicitly and without changing them.
- When filling out the output format  you may not change the project title text, and do not include any text before or after the project title text.
- Return the requested information, strictly filling out the OUTPUT FORMAT.
- Do not forget to include the field names at the start of each line, as per the OUTPUT FORMAT.

OUTPUT FORMAT:
Experience:Project Title 1
Experience:Project Title 2
Experience:Project Title 3
Experience:Project Title 4
Experience:Project Title 5


INPUT:
INPUT "Projects" resume section:
{raw_cv_data}

INPUT job description:
{job_description}

""",
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["flexible", "cap_letters", "[P]Experience:"]
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
            "job_description": "",
            "prefix_dict": {
                       "Description:":["[1]",True],
                       "Skills:":["[1]",True],
                       "Dummy:":["[BIG DUMMY]"]
                   } 
        },
        "prompt_in": 
"""REQUEST:
Given the "Description" and "Skills" subsections of a role belonging to the "Projects" section of a resume and a job description, rewrite the "Description" and "Skills" subsections following these guidelines:
- In the "Description" subsection:
    - Rewrite to highlight achievements and relevant skills, using up to 2 sentences (max 20 words each), as a single line of text.
- In the "Skills" subsection:
    - Select up to 6 skills relevant to the job description (Programming Languages, Technical Skills, Soft Skills). Every skill category should be present, even if empty.
    - Skills must be comma-separated and follow the format below.
    - If there are no skills in a given category, use " ", then follow up as the format below indicates 
        - For example: Programming Languages: ; Technical Skills: ; Soft Skills: Communication, Teamwork
- Prioritize using keywords found in both the job description and the "Description" and "Skills" sections (do not use keywords present solely in the job description since that would be a lie).
- Do NOT use line breaks inside the text of any subsection. 
- Do NOT forget to include the field names "Description:" and "Skills:" at the start of their respective lines, as per the OUTPUT FORMAT.
- Do NOT include any information not present in the "Description" and "Skills" subsections. 
- DO NOT include information that is present solely in the job description.
- Return the requested information, strictly filling out the OUTPUT FORMAT below

OUTPUT FORMAT:
Description: Brief role description.
Skills: Programming Languages: ...; Technical Skills: ...; Soft Skills: ...


INPUT:
INPUT job description:
{job_description}

INPUT "Description" and "Skills" subsections of a project belonging to the "Projects" section of a resume:
{experience}

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
            "job_description": "",
            "prefix_dict": {
                "Experience:" : ["[E]",True],
                "Dummy:" : ["[BIG DUMMY]"]
            }
        },
        "prompt_in": 
"""REQUEST:
Given the all experiences across 3 resume sections (Volunteering and Leadership, Work Experience, and Projects) and a job description, select up to 5 experiences based on the job description. When selecting:
- If the total number of experiences/roles is less than or equal to 5, return all of them.
- If the total number of experiences/roles is greater than or equal to 5 before selection: 
    - Select the most relevant 5 experiences/roles based on the job description (you still must return exactly 5).
- Do not change the name of the experiences/roles.
- Prioritize Projects that match relevant skills and experience present in the job description.
- While filling out the output format, do not change the experience text, and do not include any text before or after the experience title text.
- Return the requested information, strictly filling out the OUTPUT FORMAT.
- Do not forget to include the field names at the start of each line, as per the OUTPUT FORMAT.

OUTPUT FORMAT:
Experience:Experience Title 1
Experience:Experience Title 2
Experience:Experience Title 3
Experience:Experience Title 4
Experience: Experience Title 5


INPUT:
INPUT job description:
{job_description}

INPUT experiences from 3 resume sections (Volunteering and Leadership, Work Experience, and Projects):
{experiences}

""",
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["flexible", "cap_letters", "[E]Experience:"]
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
            "section_name": "",
            "prefix_dict": {
                "Section Summary:" : ["[S]",True],
                "Dummy:" : ["[BIG DUMMY]"]
            }
        },
        "prompt_in": 
"""REQUEST:
Given a section from a resume, summarize the sections in a wholistic manner while following these guidelines:
- Be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
- Include all information, competencies, achievements, and skills, this is a wholistic summary of the candidate's qualifications.
- Return the summarized information as a single continuous string of text, following the output format strictly. 
- Do not forget to include the field names at the start of each line, as per the OUTPUT FORMAT.
- Return the requested information, strictly filling out the OUTPUT FORMAT.

OUTPUT FORMAT:
Section Summary: {section_name} Summary; Wholistic summary of the section's information.


INPUT:
INPUT section from a resume:
{section}


""",
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["strict", "cap_letters", "[S]Section Summary:"]
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
            "general_info_text": "",
            "prefix_dict": {
                "General Information Summary:":["[S]",True],
                "Dummy:" : ["[BIG DUMMY]"]
            }
        },
        "prompt_in": 
"""REQUEST:
Given the general information from a resume, summarize it in a wholistic manner; be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
Since this is a summary of a resume's general information, you need to include the candidate's Name, Contact Information, Title, and Languages Spoken.
Return the requested information, strictly filling out the OUTPUT FORMAT. (do not forget to include the "General Information Summary:" text at the start of the output).
Also, do not forget to include the field names at the start of each line, as per the OUTPUT FORMAT.

OUTPUT FORMAT:
General Information Summary: Brief and concise summary of the resume's general information, presented as a single continuous string of text.


INPUT:
INPUT general information from a resume:
{general_info_text}


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
            "skill_section": "",
            "prefix_dict": {
                "Skills Summary:":["[S]",True],
                "Dummy:" : ["[BIG DUMMY]"]
            }
        },
        "prompt_in": 
"""REQUEST:
Given a "Skills" section from a resume, summarize the skills section of a resume in a wholistic manner; be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
Return the requested information, strictly filling out the OUTPUT FORMAT. (do not forget to include the "Skills Summary:" text at the start of the output).
Also, do not forget to include the field names at the start of each line, as per the OUTPUT FORMAT.

OUTPUT FORMAT:
Skills Summary: Wholistic summary of the resume's skills, presented as a single continuous string of text.


INPUT:
INPUT "Skills" section from a resume:
{skill_section}


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
            "job_description": "",
            "prefix_dict":{
                "Summary:": ["[0]",True],
                "Dummy:" : ["[BIG DUMMY]"]
            }
        },
        "prompt_in": 
"""REQUEST:
Given a wholistic summary of a resume and a job description, tailor a Summary section for a resume to best match the job description; follow these guidelines:
- Write the tailored summary section as the candidate, not as an external observer.
- The summary mustn't exceed 100 words.
- Do not line break the summary section, it should be a continuous block of text.
- When mentioning specific qualifications, these must be relevant to the job description:
    -  Preferably mention qualifications and keywords that appear on both the resume and the job description, particularly those which demonstrate the candidate's technical expertise.
- Return only the revised summary and strictly follow the output format, filling in the parts that have **fill-in:"text"**
- Return the requested information, strictly filling out the OUTPUT FORMAT.
- Do not forget to include the field name "Summary:", as per the OUTPUT FORMAT.

OUTPUT FORMAT:
Summary: Despite limited work experience, I bring strong work ethic, adaptability and curiosity. Experienced in **fill-in specific relevant technical skills"**. Now seeking a position that offers growth and learning opportunities.


INPUT:
INPUT wholistic summary of a resume:
{prev_summary}

INPUTjob description:
{job_description}


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
            "job_description": "",
            "no_skills":12,
            "no_prog":3,
            "no_tech":5,
            "no_soft":4,
            "prefix_dict": {
                "Programming Languages:":["[1]", True],
                "Technical Skills:":["[1]", True],
                "Soft Skills:":["[1]", True],
                "Skills:":["[0]", False],
                "Dummy:" : ["[BIG DUMMY]"]

            }
        },
        "prompt_in": 
"""REQUEST:
Given a job description:
Extract relevant "Programming Language","Technical Skills", and "Soft Skills" following the guidelines below:
- Do not line break any line containing the relevant skills, it should follow the format below strictly.
- If either the "Programming Languages", "Technical Skills", or "Soft Skills" sections are empty (which means no relevant skills of said cathegory were found), return them as an empty section (without any extra text to denote its empty status).
- Aside from the information requested, do not include any additional text or explanations.
- Return the requested information, strictly filling out the OUTPUT FORMAT.
- Do not forget to include the field names at the start of each line, as per the OUTPUT FORMAT.
- Do not break down any OUTPUT FORMAT lines into multiple instances(e.g. do not output 2 lines labeled "Technical Skills:", one is sufficient as per the format)

OUTPUT FORMAT:
Skills:
Programming Languages: comma-separated list of Programming Languages required by job description
Technical Skills: comma-separated list of Technical Skills required by job description
Soft Skills: comma-separated list of Soft Skills required by job description


INPUT:
INPUT job description:
{job_description}

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
            "section_name": "",
            "prefix_dict":{
                "Comparative Analysis:": ["[0]",True],
                "Dummy" : ["[BIG DUMMY]"]
            }
        },
        "prompt_in": 
"""REQUEST:
Given a raw untailored resume section and and its counterpart from an already tailored resume, compare the two resume sections and:
- Confirm that the tailored section does not contain any made-up information.
- Verify that all information in the tailored section is present in the raw section, even if paraphrased.
- Identify any contradictions between the two sections.
- Identify any contradictions within the tailored section (with itself).
- Do not forget to include the field names at the start of each line, as per the OUTPUT FORMAT.
- Return the requested information, strictly filling out the OUTPUT FORMAT.

OUTPUT FORMAT:
Comparative Analysis: {section_name} Section; Analysis of the tailored resume section vs the raw section, as a single line of text.


INPUT:
INPUT raw untailored resume section:
{old_resume_s_txt}

INPUT already tailored resumesection:
{new_resume_s_txt}


""",
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["strict", "digits", "[0]Comparative Analysis:"]
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
            "job_description": "",
            "prefix_dict":{
                "Cover Letter:":["[0]",False],
                "New Paragraph0:":["[1]",True],
                "New Paragraph2:":["[1]",True],
                "New Paragraph3:":["[1]",True],
                "New Paragraph1:":["[1]",True],
                "Dummy:" : ["[BIG DUMMY]"]
            }
        },
        "prompt_in": 
"""REQUEST:
Given a wholistic summary of a resume, and the summary of the job description it has been tailored to, write a cover letter tailored to the job description, following the guidelines below:
- It should highlight the most relevant skills and experiences from the resume that match the job description.
- It should be written in a professional tone.
- Do not invent information or experiences, only include what is present in the resume.
- Do not make use of run-on sentences.
- The only line breaks allowed are those that separate paragraphs, as per the format below.
- Only 4 paragraphs are allowed, each starting with "New ParagraphX: " and then the text of the new paragraph; X starts at 0 and goes up to 3.
- Total word count must not exceed 400 words. This is a hard limit, so be concise and to the point.
- Write the cover letter as the candidate, not as an external observer.
- Do not forget to include the field names at the start of each line, as per the OUTPUT FORMAT.
- Return the requested information, strictly filling out the OUTPUT FORMAT.

OUTPUT FORMAT:
Cover Letter: 
New Paragraph0: Cover Letter introduction, mentioning the job title and company, as well as the candidate's enthusiasm for the role.
New Paragraph1: Explain why the candidate is a good fit for the role, briefly mentioning the most relevant information from the resume that matches the job description.
New Paragraph2: Provide further information about the candidate's qualifications and how they align with the job requirements. Make use of specific examples and metrics to demonstrate impact (if applicable).
New Paragraph3: Closing statement, thanking the employer for their time and consideration. Invite them to contact the candidate for further discussion, providing email address.


INPUT:
INPUT wholistic summary of a resume:
{cv_data}

INPUT summary of the job description it has been tailored to:
{job_description}


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
            "job_description": "",
            "prefix_dict" : {
                "Consistency Checker Vs Job Description:":["[0]",False],
                "Inconsistencies With Job Description:":["[1]",True],
                "Suggestions for Improvement:":["[1]",True],
                "Dummy:" : ["[BIG DUMMY]"]
            }
        },
        "prompt_in": 
"""REQUEST:
Given the a summary of a resume and the job description the aforementioned resume has been tailored to, perform a consistency check on the tailored resume against the job description. This consistency check will check if the resume is consistent with the job description, meaning that all skills and experiences mentioned in the resume should be relevant to the job description.
Follow these guidelines:
- Be mindful not to include any line breaks in the content of any of the sections/subsections.
- Be as objective as possible, and do not make any assumptions about the data.
- Do not create nor imagine any data that is not present in the original data.
- Do not modify the OUTPUT FORMAT.
- Return the requested information, strictly filling out the OUTPUT FORMAT.
- Do not forget to include the field names at the start of each line, as per the OUTPUT FORMAT.

OUTPUT FORMAT:
Consistency Checker Vs Job Description:
Inconsistencies With Job Description: Number of inconsistencies found (return 'None' if no inconsistencies). List of inconsistencies found, if any, must be a continuous block of text, composed of sentences separated by ";", not line breaks.
Suggestions for Improvement: List of suggestions for improvement, if any (return 'None' if no suggestions). must be a continuous block of text, composed of sentences separated by ";", not line breaks.


INPUT:
INPUT summary of a resume tailored to a particular job description:
{cv_data}
INPUT job description the aforementioned resume has been tailored to:
{job_description}

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
            "job_description": "",
            "prefix_dict" : {
                "Consistency Checker Vs Job Description:":["[0]",False],
                "Inconsistencies With Job Description:":["[1]",True],
                "Suggestions for Improvement:":["[1]",True],
                "Dummy:" : ["[BIG DUMMY]"]
            }
        },
        "prompt_in": 
"""REQUEST:
Given a cover letter and the job description the aforementioned cover letter has been tailored to, perform a consistency check on the tailored cover letter against the job description. This consistency check will check if the cover letter is consistent with the job description, meaning that all skills and experiences mentioned in the cover letter should be relevant to the job description.
Follow these guidelines:
- Be mindful not to include any line breaks in  the content of any of the sections/subsections.
- Be as objective as possible, and do not make any assumptions about the data.
- Do not create nor imagine any data that is not present in the original data.
- Do not modify the OUTPUT FORMAT.
- Return the requested information, strictly filling out the OUTPUT FORMAT.
- Do not forget to include the field names at the start of each line, as per the OUTPUT FORMAT.

OUTPUT FORMAT:
Consistency Checker Vs Job Description:
Inconsistencies With Job Description: Number of inconsistencies found (return 'None' if no inconsistencies). List of inconsistencies found, if any, must be a continuous block of text, composed of sentences separated by ";", not line breaks.
Suggestions for Improvement: List of suggestions for improvement, if any (return 'None' if no suggestions). must be a continuous block of text, composed of sentences separated by ";", not line breaks.


INPUT:
INPUT cover letter tailored to a particular job description:
{cv_data}
INPUT job description the aforementioned resume has been tailored to:
{job_description}

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
            "job_description": "",
            "no_courses": 5,
            "prefix_dict" : {
                "Courses:":["[1]",True],
                "Dummy:" : ["[BIG DUMMY]"]
            }
        },
        "prompt_in": 
"""REQUEST:
Given a list of courses taken on a given program and a job description, extract the {no_courses} most relevant courses that match the skills and requirements outlined in the job description.
Follow these guidelines when extracting courses and returning them:
- Do not include any courses not present in the original courses list.
- Do not use line breaks inside any subsection.
- Courses must be comma-separated and follow the format below.
- Return the requested information, strictly filling out the OUTPUT FORMAT.
- Be mindful that courses may or may not have a course code (represented by "XXX001" in the OUTPUT FORMAT section)
- Do not forget to include the field names at the start of each line, as per the OUTPUT FORMAT.

OUTPUT FORMAT:
Courses: XXX001 Course Name1, XXX002 Course Name2, XXX003 Course Name3...


INPUT:
INPUT list of courses taken on a given program:
{courses}

INPUT job description:
{job_description}


""",
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["strict", "digits", "[1]Courses:"]
    },

    # NON-STANDARD CALLS
    "tailor_courses_robust": #DONE (NO NEED FOR prefix_dict SINCE NO filter_output calls are made inside the function, instead we skip final filtering)
    {
        "call_id": "tailor_courses_robust", 
        "payload_in": {"model": DEFAULT_MODEL,
                       "system": "",
                       "stream": False,
                        "temperature": CONFIG["MODELS"]["TEMPERATURE"]}, 
        "format": {
            "courses": "",
            "job_description": "",
            "prefix_dict" : {
                "Courses:":["[1]",True],
                "Dummy:" : ["[BIG DUMMY]"]
            }   
        },
        "prompt_in": "", 
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["strict", "digits", "[1]Courses:"]
    },
    "batch_summarize_sections": #DONE
    {
        "call_id": "batch_summarize_sections",
        "payload_in": {
            "model": DEFAULT_MODEL,
            "system": "",
            "stream": False,
            "temperature": CONFIG["MODELS"]["TEMPERATURE"]
        },
        "format": {
            "sections": [],
            "section_names": [],
            "second_half": """

INPUT:
INPUT sections from a resume:
{sections_text}


""",
            "prefix_dict": {
                "Section Summary:" : ["[S]", True],
                "Dummy:" : ["[BIG DUMMY]"]
            }
        },
        "prompt_in":
"""REQUEST:
Given a number of sections from a resume, summarize the sections in a wholistic manner while following these guidelines:
- Be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
- Include all information, competencies, achievements, and skills, this is a wholistic summary of the candidate's qualifications.
- Keep in mind that these summaries will be used in a "Sliding Window" approach to summarize the entire resume effectively, so include information that is relevant for the overall context of the resume.
- Return the requested information, strictly filling out the OUTPUT FORMAT.
- Do not forget to include the field names at the start of each line, as per the OUTPUT FORMAT.
- The only field name allowed is "Section Summary:", do NOT include a separate "Summary:" section as this will result in an error.
- There must be 1 "Section Summary:" per section given, in this case the sections given are {no_sections}:
    - {section_names}
""",
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["flexible", "cap_letters", "[S]Section Summary:"]
    },
    "tailor_skills_robust": #DONE (NO NEED FOR prefix_dict SINCE NO filter_output calls are made inside the function, instead we skip final filtering)
    {
        "call_id": "tailor_skills_robust", 
        "payload_in": {"model": DEFAULT_MODEL,
                       "system": "",
                       "stream": False,
                        "temperature": CONFIG["MODELS"]["TEMPERATURE"]}, 
        "format": {
            "cv_data": "",
            "job_description": "",
            "no_skills":12,
            "no_prog":3,
            "no_tech":5,
            "no_soft":4,
            "prefix_dict": {
                "Programming Languages:":["[1]", True],
                "Technical Skills:":["[1]", True],
                "Soft Skills:":["[1]", True],
                "Skills:":["[0]", False],
                "Dummy:" : ["[BIG DUMMY]"]

            },
            "standard_calls": ["tailor_skills"]    
        },
        "prompt_in": "", 
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["strict", "digits", "[0]Skills:","[1]Programming Languages:","[1]Technical Skills:","[1]Soft Skills:"]
    },
    ##similar start
    "tailor_volunteering_and_leadership": #DONE (NO NEED FOR prefix_dict SINCE NO filter_output calls are made inside the function, instead we skip final filtering)
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
            "standard_calls": ["step0_volunteering_and_leadership","step3_volunteering_and_leadership"],
            "prefix_dict" : {}
            }, 
        "prompt_in": "", 
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["flexible", "digits", "[0]Volunteering and Leadership:",
                           "[1]Role:","[1]Organization:","[1]Location:","[1]Duration:","[1]Description:","[1]Skills:"]
    },
    "tailor_work_experience": #DONE (NO NEED FOR prefix_dict SINCE NO filter_output calls are made inside the function, instead we skip final filtering)
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
            "standard_calls": ["step0_work_experience","step3_work_experience"],
            "prefix_dict" : {}
            }, 
        "prompt_in": "", 
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["flexible", "digits", "[0]Work Experience:", "[1]Job Title:","[1]Company:", "[1]Location:", "[1]Duration:", "[1]Description:","[1]Skills:"]
    },
    "tailor_projects": #DONE (NO NEED FOR prefix_dict SINCE NO filter_output calls are made inside the function, instead we skip final filtering)
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
            "standard_calls": ["step0_projects","step3_projects"],
            "prefix_dict" : {}
            }, 
        "prompt_in": "", 
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["flexible", "digits", "[0]Projects:", "[1]Project Title:","[1]URL:", "[1]Type:", "[1]Duration:", "[1]Description:", "[1]Skills:"]
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
            "async_calls": ["standard_ollama_call_async"],
            "prefix_dict": {
                "Sections Summary:" : ["[S]",True],
                "Dummy:" : ["[BIG DUMMY]"]
            }
            }, 
        "prompt_in": 
"""REQUEST:
Given 2 resume section summaries, create a new summary that incorporates all two summaries, following these guidelines:
- Be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
- Include ALL information, competencies, achievements, and skills, for this is a wholistic summary of the candidate's qualifications. Do not miss any skills.
- When referring to the candidate, use their name: {candidate_name} or their title: {candidate_title}
- Return the requested information, strictly filling out the OUTPUT FORMAT.
- Do not forget to include the field names at the start of each line, as per the OUTPUT FORMAT.
- You must include "Sections Summary: This is a summary of the {section1_name} and {section2_name} sections:" as per the OUTPUT FORMAT BELOW

OUTPUT FORMAT:
Sections Summary: This is a summary of the {section1_name} and {section2_name} sections: Wholistic summary of the sections' information, competencies, achievements, and skills.


INPUT:
INPUT {section1_name} section summary:
{summary1}

INPUT {section2_name} section summary:
{summary2}


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
            "async_calls": ["standard_ollama_call_async"],
            "prefix_dict": {
                "Sections Summary:" : ["[S]",True],
                "Dummy:" : ["[BIG DUMMY]"]
            }
            }, 
        "prompt_in": 
"""REQUEST:
Given 3 resume section summaries, create a new summary that incorporates all two summaries, following these guidelines:
- Be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
- Include ALL information, competencies, achievements, and skills, for this is a wholistic summary of the candidate's qualifications. Do not miss any skills.
- When referring to the candidate, use their name: {candidate_name} or their title: {candidate_title}
- Return the requested information, strictly filling out the OUTPUT FORMAT.
- Do not forget to include the field names at the start of each line, as per the OUTPUT FORMAT.
- You must include "Sections Summary: This is a summary of the {section1_name}, {section2_name} and {section2_name} sections:" as per the OUTPUT FORMAT BELOW

OUTPUT FORMAT:
Sections Summary: This is a summary of the {section1_name}, {section2_name} and {section3_name}sections: Wholistic summary of the sections' information, competencies, achievements, and skills.

INPUT:
INPUT {section1_name} section summary:
{summary1}

INPUT {section2_name} section summary:
{summary2}

INPUT {section3_name} section summary:
{summary3}


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
            "async_calls": ["standard_ollama_call_async"],
            "prefix_dict": {
                "Sections Summary:" : ["[S]",True],
                "Dummy:" : ["[BIG DUMMY]"]
            }
            }, 
        "prompt_in": 
"""REQUEST:
Given 4 resume section summaries, create a new summary that incorporates all two summaries, following these guidelines:
- Be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
- Include ALL information, competencies, achievements, and skills, for this is a wholistic summary of the candidate's qualifications. Do not miss any skills.
- When referring to the candidate, use their name: {candidate_name} or their title: {candidate_title}
- Return the requested information, strictly filling out the OUTPUT FORMAT.
- Do not forget to include the field names at the start of each line, as per the OUTPUT FORMAT.
- You must include "Sections Summary: This is a summary of the {section1_name}, {section2_name}, {section3_name} and {section4_name} sections:" as per the OUTPUT FORMAT BELOW

OUTPUT FORMAT:
Sections Summary: This is a summary of the {section1_name}, {section2_name}, {section3_name} and {section4_name}sections: Wholistic summary of the sections' information, competencies, achievements, and skills.


INPUT:
INPUT {section1_name} section summary:
{summary1}

INPUT {section2_name} section summary:
{summary2}

INPUT {section3_name} section summary:
{summary3}

INPUT {section4_name} section summary:
{summary4}


""", #Set at runtime
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["strict", "cap_letters", "[S]"]#Might lead to error, check later
    },
    ##similar end
    "prune_experiences": #DONE (NO NEED FOR prefix_dict SINCE NO filter_output calls are made inside the function, instead we skip final filtering)
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
            "standard_calls": ["step0_prune_experiences"],
            "prefix_dict":{}
            }, 
        "prompt_in": "", #Empty
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["flexible", "digits", 
                          "[0]Volunteering and Leadership:","[1]Role:","[1]Organization:","[1]Location:","[1]Duration:","[1]Description:","[1]Skills:",
                          "[0]Work Experience:", "[1]Job Title:","[1]Company:",
                          "[0]Projects:", "[1]Project Title:","[1]URL:", "[1]Type:"]#Might lead to error, check later
    },
    "slide_summary": #DONE (NO NEED FOR prefix_dict SINCE NO filter_output calls are made inside the function, instead we skip final filtering)
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
            "prefix_dict":{}
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
            "prefix_dict" : {
                "Summary:":["[0]",True],
                "Dummy:" : ["[BIG DUMMY]"]
            }
        }, 
        "prompt_in": 
"""REQUEST:
Given all summarized sections of a resume, create a wholistic summary of all of them, following these guidelines:
- Include the candidate's contact information, as well as their title and name.
- Include any certifications or qualifications.
- Include all education.
- Include all projects, work experience, and volunteering and leadership roles.
- Include all information, competencies, achievements, and skills, this is a wholistic summary of the candidate's qualifications.
- Maintain the context and flow between the sections.
- Be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
- When filling out the output format, do not forget to include the "Summary:" text before the actual summary.
- Return the requested information, strictly filling out the OUTPUT FORMAT.
- Output must be only 1 line long and it must start with "Summary:", as per the OUTPUT FORMAT.

OUTPUT FORMAT:
Summary: Wholistic summary of all sections, presented as a single continuous string of text.


INPUT:
INPUT summarized sections of a resume:
{slides_txt}

""",
        "ollama_url": DEFAULT_URL, #ollama_url=DEFAULT_URL,
        "sample_starts": ["strict", "digits", "[0]Summary:"]
    },
    "tailor_summary": #DONE (NO NEED FOR prefix_dict SINCE NO filter_output calls are made inside the function, instead we skip final filtering)
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
            "prefix_dict":{}
        }, 
        "prompt_in": "",#Empty
        "ollama_url": DEFAULT_URL, #ollama_url=DEFAULT_URL,
        "sample_starts": ["strict", "digits", "[0]Summary:"]
    },
    "new_vs_old_resume": #DONE (NO NEED FOR prefix_dict SINCE NO filter_output calls are made inside the function, instead we skip final filtering)
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
            "prefix_dct":{}
        }, 
        "prompt_in": "",#Empty
        "ollama_url": DEFAULT_URL, #ollama_url=DEFAULT_URL,
        "sample_starts": ["flexible", "digits", "[0]Comparative Analysis:"]
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
            "prefix_dict" : {
                "Consistency Checker Vs Original Resume:":["[0]",False],
                "Inconsistencies With Original Resume:":["[1]",True],
                "Suggestions for Improvement:":["[1]",True],
                "Dummy:" : ["[BIG DUMMY]"]
            }
        }, 
        "prompt_in": 
"""REQUEST:
Given a list containing a per-section analysis of a two resumes, comparing the synthesized data in the new resume (which has been tailored to a particular job description) against the original, synthesize a report which extracts the following data from the list of analyses:
- Whether the new resume is consistent with the original resume, meaning that all information in the new resume is present in the original resume, even if paraphrased.
- Whether the new resume is consistent with itself, meaning that there should be no contradictions or inconsistencies in the information provided.
The report should follow these guidelines:
- Be mindful not to include any line breaks in  the content of any of the sections/subsections.
- Be as objective as possible, and if you must make assumptions, make very conservative assumptions
- Do not create nor imagine any data that is not present in the original data.
- Do not modify the OUTPUT FORMAT.
- Return the requested information, strictly filling out the OUTPUT FORMAT.
- Do not forget to include the field names at the start of each line, as per the OUTPUT FORMAT.

OUTPUT FORMAT:
Consistency Checker Vs Original Resume:
Inconsistencies With Original Resume: Number of inconsistencies found (return 'None' if no inconsistencies). List of inconsistencies found, if any, must be a continuous block of text, composed of sentences separated by ";", not line breaks.
Inconsistencies With Self: Number of inconsistencies found (return 'None' if no inconsistencies). List of inconsistencies found, if any, must be a continuous block of text, composed of sentences separated by ";", not line breaks.
Suggestions for Improvement: List of suggestions for improvement, if any (return 'None' if no suggestions). must be a continuous block of text, composed of sentences separated by ";", not line breaks.


INPUT:
INPUT list containing a per-section analysis of the resumes, comparing the synthesized data in the new resume against the original:
{all_analysis}

""",
        "ollama_url": DEFAULT_URL, #ollama_url=DEFAULT_URL,
        "sample_starts": ["strict", "digits", "[0]Consistency Checker VS Original Resume:","[1]Inconsistencies With Original Resume:","[1]Inconsistencies With Self:", "[1]Suggestions for Improvement:"]
    },
    "compose_cover_letter_dictionary": #DONE (NO NEED FOR prefix_dict SINCE NO filter_output calls are made inside the function, instead we skip final filtering)
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
            "prefix_dict": {}
        }, 
        "prompt_in": "",#Empty
        "ollama_url": DEFAULT_URL, #ollama_url=DEFAULT_URL,
        "sample_starts": ["strict", "digits", "[0]Name:","[0]Languages:",
                          "[0]Contact Information:","[1]Address:","[1]Phone:","[1]Email:","[1]LinkedIn:", "[1]Github:","[1]Portfolio:",
                          "[0]Cover Letter:","[1]New Paragraph0:","[1]New Paragraph1:","[1]New Paragraph2:","[1]New Paragraph3:"]
    },
    "tailor_experiences": #DONE
    {
        "call_id": "tailor_volunteering_and_leadership", 
        "payload_in": {"model": DEFAULT_MODEL,
                       "system": "",
                       "stream": False,
                         "temperature": CONFIG["MODELS"]["TEMPERATURE"]}, 
        "format": {
            "job_description_summary": "",
            "reference_dct": {},
            "standard_calls": ["tailor_experience"],
            "prefix_dict" : {}
            }, 
        "prompt_in": "", 
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["flexible", "digits", 
                          "[0]Volunteering and Leadership:","[1]Role:","[1]Organization:","[1]Location:","[1]Duration:","[1]Description:","[1]Skills:",
                          "[0]Work Experience:", "[1]Job Title:","[1]Company:",
                          "[0]Projects:", "[1]Project Title:","[1]URL:", "[1]Type:"]
    },
    #ASYNC
    "standard_ollama_call_async": #WIP
    {
        "call_id": "standard_ollama_call_async", 
        "payload_in": {
            "model": DEFAULT_MODEL,
            "system": "",
            "stream": False,
            "temperature": CONFIG["MODELS"]["TEMPERATURE"]}, 
        "format": {
            "prefix_dict": {
                "Section Summary:" : ["[S]",True],
                "Dummy:" : ["[BIG DUMMY]"]
            }
            }, 
        "prompt_in": "", #Set at runtime
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["strict", "cap_letters", "[S]Section Summary:"]#Might lead to error, check later
    }

}
STANDARD= [
    "tailor_experience",
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