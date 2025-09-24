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

[REQUEST]

[OUTPUT FORMAT]

[INPUT]

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
                       "Consistency Checker Vs Resume:":"[0]",
                       "Inconsistencies With Resume:":"[1]",
                       "Inconsistencies With Self:":"[1]",
                       "Suggestions for Improvement:":"[1]",
                       "Dummy:":"[BIG DUMMY]"
                   }  
                   },
        "prompt_in": 
"""[REQUEST]
Given a cover letter and a wholistic summary of a resume (both part of the same job application):
Perform a consistency check on the tailored cover letter against the resume. This consistency check should include:
- Whether the cover letter is consistent with the resume, meaning that all skills and experiences mentioned in the cover letter should be present in the resume.
- Whether the cover letter is consistent with itself, meaning that there should be no contradictions or inconsistencies in the information provided.
The report should follow these guidelines:
- Be mindful not to include any line breaks in  the content of any of the sections/subsections.
- Be as objective as possible, and if you must make assumptions, make very conservative assumptions
- Do not create nor imagine any data that is not present in the original data.
- When filling out the output format, include the numbers "[0]", "[1]", and do not modify the format.
- Return the requested information, strictly filling out the OUTPUT FORMAT.

[OUTPUT FORMAT]
Consistency Checker Vs Resume:
Inconsistencies With Resume: Number of inconsistencies found (return 'None' if no inconsistencies). List of inconsistencies found, if any, must be a continuous block of text, composed of sentences separated by ";", not line breaks.
Inconsistencies With Self: Number of inconsistencies found (return 'None' if no inconsistencies). List of inconsistencies found, if any, must be a continuous block of text, composed of sentences separated by ";", not line breaks.
Suggestions for Improvement: List of suggestions for improvement, if any (return 'None' if no suggestions). must be a continuous block of text, composed of sentences separated by ";", not line breaks.
Dummy: No output needed for this field. Its purpouse is to serve as an output delimiter

[INPUT]
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
                   "job_description": "" 
                   },
        "prompt_in": 
"""[REQUEST]
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
- Return the requested information, strictly filling out the OUTPUT FORMAT.

[OUTPUT FORMAT]
[0]Company Name: Company Name
[0]Job Title: Position Name
[0]Key responsibilities: List of key responsabilities as a single block of text separated by ";"
[0]Requirements: List of basic requirements as a single block of text separated by ";"
[0]Programming Languages: List of programming languages required, presented as a single block of text separated by ";"
[0]Technical Skills: List of technical skills required, presented as a single block of text separated by ";"
[0]Soft Skills:Soft List of soft skills required, presented as a single block of text separated by ";"
[0]Other Skills:Other List of other skills required, presented as a single block of text separated by ";"

[INPUT]
INPUT job description:
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
"""[REQUEST]
Given a "Volunteering and Leadership" resume section and a job description, select up to 5 roles based on the job description. When selecting:
- If the total number of roles is less than or equal to 5, return all of them.
- If the total number of roles is greater than or equal to 5 before selection: Select the most relevant 5 roles based on the job description.
- Do not change the name of the roles.
- Prioritize roles that match relevant skills and experience present in the job description.
- It is okay to not select any roles if none are relevant.
- Display the Role Titles explicitly; do not write "Role Title:" before the Role Title
- When filling out the output format,  you may not change the role title text, do not include any text before [R] or after the role title text.
- Return the requested information, strictly filling out the OUTPUT FORMAT.

[OUTPUT FORMAT]
[R]Role Title 1
[R]Role Title 2
[R]Role Title 3
[R]Role Title 4
[R]Role Title 5

[INPUT]
INPUT "Volunteering and Leadership" resume section:
{raw_cv_data}
INPUT job description:
{job_description}

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
"""[REQUEST]
Given the "Description" and "Skills" attributes of a role belonging to the "Volunteering and Leadership" section of a resume and a job description, rewrite the experience to best match the job description, following these guidelines:
- Do not include any information not present in the original experience.
- In the Description subsection, rewrite to highlight achievements and relevant skills for the job, using up to 2 sentences (max 20 words each), as a single block of text.
- In the Skills subsection, include up to 6 relevant skills (Programming Languages, Technical Skills, Soft Skills). Every skill category should be present, even if empty.
- Do not use line breaks inside any subsection. Do not use the ":" character in the Description.
- Skills must be comma-separated and follow the format below. 
- If there are no skills in a given category, use " ", then follow up as the format below indicates 
    - For example: Programming Languages: ; Technical Skills: ; Soft Skills: Communication, Teamwork
- Include the prefix [1] at the start of each line (as seen in the format below).
- Return the requested information, strictly filling out the OUTPUT FORMAT.

[OUTPUT FORMAT]
[1]Description: Brief role description.
[1]Skills: Programming Languages: ...; Technical Skills: ...; Soft Skills: ...

[INPUT]
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
            "job_description": ""
        },
        "prompt_in": 
"""[REQUEST]
Given a "Work Experience" resume section and a job description, select up to 5 jobs based on the job description. When selecting:
- If the total number of jobs is less than or equal to 5, return all of them.
- If the total number of jobs is greater than or equal to 5 before selection: Select the most relevant 5 jobs based on the job description.
- Do not change the name of the jobs.
- Prioritize jobs that match relevant skills and experience present in the job description.
- It is okay to not select any jobs if none are relevant.
- Display the Job Titles explicitly; do not write "Job Title:" before the Job Title
- When filling out the output format,  you may not change the job title text, do not include any text before [J] or after the job title text.
- Return the requested information, strictly filling out the OUTPUT FORMAT.

[OUTPUT FORMAT]
[J]Job Title 1
[J]Job Title 2
[J]Job Title 3
[J]Job Title 4
[J]Job Title 5

[INPUT]
INPUT "Work Experience" resume section:
{raw_cv_data}

INPUT job description:
{job_description}

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
"""[REQUEST]
Given the "Description" and "Skills" subsections of a role belonging to the "Work Experience" section of a resume and a job description, rewrite the experience to best match the job description, following these guidelines:
- Do not include any information not present in the original experience.
- In the Description subsection, rewrite to highlight achievements and relevant skills for the job, using up to 2 sentences (max 20 words each), as a single block of text.
- In the Skills subsection, include up to 6 relevant skills (Programming Languages, Technical Skills, Soft Skills). Every skill category should be present, even if empty.
- Do not use line breaks inside any subsection. Do not use the ":" character in the Description.
- Skills must be comma-separated and follow the format below. 
- If there are no skills in a given category, use " ", then follow up as the format below indicates 
    - For example: Programming Languages: ; Technical Skills: ; Soft Skills: Communication, Teamwork
- Include the prefix [1] at the start of each line (as seen in the format below).
- Return the requested information, strictly filling out the OUTPUT FORMAT.

[OUTPUT FORMAT]
[1]Description: Brief role description.
[1]Skills: Programming Languages: ...; Technical Skills: ...; Soft Skills: ...

[INPUT]
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
            "job_description": ""
        },
        "prompt_in": 
"""[REQUEST]
Given a "Projects" resume section and a job description, select up to 5 projects based on the job description. When selecting:
- If the total number of projects is less than or equal to 5, return all of them.
- If the total number of projects is greater than or equal to 5 before selection: Select the most relevant 5 projects based on the job description.
- Do not change the name of the projects.
- Prioritize projects that match relevant skills and experience present in the job description.
- It is okay to not select any projects if none are relevant.
- Display the Project Titles explicitly; do not write "Project Title:" before the Project Title
- When filling out the output format,  you may not change the project title text, do not include any text before [P] or after the project title text.
- Return the requested information, strictly filling out the OUTPUT FORMAT.

[OUTPUT FORMAT]
[P]Project Title 1
[P]Project Title 2
[P]Project Title 3
[P]Project Title 4
[P]Project Title 5

[INPUT]
INPUT "Projects" resume section:
{raw_cv_data}

INPUT job description:
{job_description}

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
"""[REQUEST]
Given the "Description" and "Skills" subsections of a project belonging to the "Projects" section of a resume and a job description, rewrite the experience to best match the job description, following these guidelines:
- Do not include any information not present in the original experience.
- In the Description subsection, rewrite to highlight achievements and relevant skills for the job, using up to 2 sentences (max 20 words each), as a single block of text.
- In the Skills subsection, include up to 6 relevant skills (Programming Languages, Technical Skills, Soft Skills). Every skill category should be present, even if empty.
- Do not use line breaks inside any subsection. Do not use the ":" character in the Description.
- Skills must be comma-separated and follow the format below. 
- If there are no skills in a given category, use " ", then follow up as the format below indicates 
    - For example: Programming Languages: ; Technical Skills: ; Soft Skills: Communication, Teamwork
- Include the prefix [1] at the start of each line (as seen in the format below).
- Return the requested information, strictly filling out the OUTPUT FORMAT.

[OUTPUT FORMAT]
[1]Description: Brief project description.
[1]Skills: Programming Languages: ...; Technical Skills: ...; Soft Skills: ....

[INPUT]
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
            "job_description": ""
        },
        "prompt_in": 
"""[REQUEST]
Given the all experiences across 3 resume sections (Volunteering and Leadership, Work Experience, and Projects) and a job description, select up to 5 experiences based on the job description. When selecting:
- If the total number of experiences/roles is less than or equal to 5, return all of them.
- If the total number of experiences/roles is greater than or equal to 5 before selection: Select the most relevant 5 experiences/roles based on the job description.
- Do not change the name of the experiences/roles.
- Prioritize projects that match relevant skills and experience present in the job description.
- It is okay to not select any experiences from a given section if none are relevant. Remember that [R], [J], and [P] indicate the section they belong to (R is Volunteering and Leadership, J is Work Experience, and P is Projects).
- While filling out the output format, do not change the role/job title/project title text, and do not include any text before [R], [J], or [P] or after the role/job title/project title text.
- Return the requested information, strictly filling out the OUTPUT FORMAT.

[OUTPUT FORMAT]
[R]Volunteering and Leadership Role 1
[J]Work Experience Job Title 1
[P]Projects Project Title 1
Where the letter R/J/P inside "[]" indicates the type of experience:
- [R]Role belongs to Volunteering and Leadership
- [J]Job Title belongs to Work Experience
- [P]Project Title belongs to Projects

[INPUT]
INPUT job description:
{job_description}

INPUT 3 resume sections (Volunteering and Leadership, Work Experience, and Projects):
{experiences}

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
"""[REQUEST]
Given a section from a resume, summarize the sections in a wholistic manner while following these guidelines:
- Be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
- Include all information, competencies, achievements, and skills, this is a wholistic summary of the candidate's qualifications.
- Return the summarized information as a single continuous string of text, following the output format strictly. 
- Do not forget to include the "[S]{section_name} Section Summary:" text at the start of the output.
- Return the requested information, strictly filling out the OUTPUT FORMAT.

[OUTPUT FORMAT]
[S]{section_name} Summary: Wholistic summary of the section's information.

[INPUT]
INPUT section from a resume:
{section}


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
"""[REQUEST]
Given the general information from a resume, summarize it in a wholistic manner; be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
Since this is a summary of a resume's general information, you need to include the candidate's Name, Contact Information, Title, and Languages Spoken.
Return the requested information, strictly filling out the OUTPUT FORMAT. (do not forget to include the "[S]General Information Summary:" text at the start of the output).

[OUTPUT FORMAT]
[S]General Information Summary: Brief and concise summary of the resume's general information, presented as a single continuous string of text.

[INPUT]
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
            "skill_section": ""
        },
        "prompt_in": 
"""[REQUEST]
Given a "Skills" section from a resume, summarize the skills section of a resume in a wholistic manner; be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
Return the requested information, strictly filling out the OUTPUT FORMAT. (do not forget to include the "[S]Skills Summary:" text at the start of the output).

[OUTPUT FORMAT]
[S]Skills Summary: Brief and concise wholistic summary of the resume's skills, presented as a single continuous string of text.

[INPUT]
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
            "job_description": ""
        },
        "prompt_in": 
"""[REQUEST]
Given a wholistic summary of a resume and a job description, tailor a Summary section for a resume to best match the job description; follow these guidelines:
- Write the tailored summary section as the candidate, not as an external observer.
- The summary mustn't exceed 100 words.
- Do not line break the summary section, it should be a continuous block of text.
- When mentioning specific skills or experiences, these must be relevant to the job description; give preference to those that appear on both the resume and the job description, particularly those which demonstrate the candidate's technical expertise.
- In the format below, do not include any text before "[0]" or after the requested information.
- Return only the revised summary and strictly follow the output format, filling in the parts that have **fill-in:"text"**
- Return the requested information, strictly filling out the OUTPUT FORMAT.

[OUTPUT FORMAT]
[0]Summary: Despite limited work experience, I bring strong work ethic, adaptability and curiosity. Experienced in **fill-in:"specific skills thanks to certain experiences"**. Now seeking a position that offers growth and learning opportunities.

[INPUT]
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
            "job_description": ""
        },
        "prompt_in": 
"""[REQUEST]
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
- Return the requested information, strictly filling out the OUTPUT FORMAT.

[OUTPUT FORMAT]
[0]Skills:
[1]Programming Languages: Programming Language 1, Programming Language 2, Programming Language 3
[1]Technical Skills: Technical Skill 1, Technical Skill 2, Technical Skill 3, Technical Skill 4, Technical Skill 5
[1]Soft Skills: Soft Skill 1, Soft Skill 2, Soft Skill 3, Soft Skill 4

[INPUT]
INPUT list of "Programming Languages", "Technical Skills" and "Soft Skills" considered to be relevant for a paticular job description:
{cv_data}

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
            "section_name": ""
        },
        "prompt_in": 
"""[REQUEST]
Given a raw untailored resume section and and its counterpart from an already tailored resume, compare the two resume sections and:
- Confirm that the tailored section does not contain any made-up information.
- Verify that all information in the tailored section is present in the raw section, even if paraphrased.
- Identify any contradictions between the two sections.
- Identify any contradictions within the tailored section (with itself).
- Return the requested information, strictly filling out the OUTPUT FORMAT.

[OUTPUT FORMAT]
[0]{section_name} Analysis: Analysis of the tailored resume section vs the raw section, as a single line of text.

[INPUT]
INPUT raw untailored resume section:
{old_resume_s_txt}

INPUT already tailored resumesection:
{new_resume_s_txt}


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
"""[REQUEST]
Given a wholistic summary of a resume, and the summary of the job description it has been tailored to, write a cover letter tailored to the job description, following the guidelines below:
- It should highlight the most relevant skills and experiences from the resume that match the job description.
- It should be written in a professional tone.
- Do not invent information or experiences, only include what is present in the resume.
- Do not make use of run-on sentences.
- The only line breaks allowed are those that separate paragraphs, as per the format below.
- Only 4 paragraphs are allowed, each starting with "[1]New ParagraphX: " and then the text of the new paragraph; X starts at 0 and goes up to 3.
- Total word count must not exceed 400 words. This is a hard limit, so be concise and to the point.
- Write the cover letter as the candidate, not as an external observer.
- Return the requested information, strictly filling out the OUTPUT FORMAT.

[OUTPUT FORMAT]
[0]Cover Letter: 
[1]New Paragraph0: Cover Letter introduction, mentioning the job title and company, as well as the candidate's enthusiasm for the role.
[1]New Paragraph1: Explain why the candidate is a good fit for the role, briefly mentioning the most relevant information from the resume that matches the job description.
[1]New Paragraph2: Provide further information about the candidate's qualifications and how they align with the job requirements. Make use of specific examples and metrics to demonstrate impact (if applicable).
[1]New Paragraph3: Closing statement, thanking the employer for their time and consideration. Invite them to contact the candidate for further discussion, providing email address.

[INPUT]
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
            "job_description": ""
        },
        "prompt_in": 
"""[REQUEST]
Given the a summary of a resume and the job description the aforementioned resume has been tailored to, perform a consistency check on the tailored resume against the job description. This consistency check will check if the resume is consistent with the job description, meaning that all skills and experiences mentioned in the resume should be relevant to the job description.
Follow these guidelines:
- Be mindful not to include any line breaks in the content of any of the sections/subsections.
- Be as objective as possible, and do not make any assumptions about the data.
- Do not create nor imagine any data that is not present in the original data.
- When filling out the output format, include the numbers "[0]", "[1]", and do not modify the format.
- Return the requested information, strictly filling out the OUTPUT FORMAT.

[OUTPUT FORMAT]
[0]Consistency Checker Vs Job Description:
[1]Inconsistencies With Job Description: Number of inconsistencies found (return 'None' if no inconsistencies). List of inconsistencies found, if any, must be a continuous block of text, composed of sentences separated by ";", not line breaks.
[1]Suggestions for Improvement: List of suggestions for improvement, if any (return 'None' if no suggestions). must be a continuous block of text, composed of sentences separated by ";", not line breaks.

[INPUT]
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
            "job_description": ""
        },
        "prompt_in": 
"""[REQUEST]
Given a cover letter and the job description the aforementioned cover letter has been tailored to, perform a consistency check on the tailored cover letter against the job description. This consistency check will check if the cover letter is consistent with the job description, meaning that all skills and experiences mentioned in the cover letter should be relevant to the job description.
Follow these guidelines:
- Be mindful not to include any line breaks in  the content of any of the sections/subsections.
- Be as objective as possible, and do not make any assumptions about the data.
- Do not create nor imagine any data that is not present in the original data.
- When filling out the output format, include the numbers "[0]", "[1]", and do not modify the format.
- Return the requested information, strictly filling out the OUTPUT FORMAT.

[OUTPUT FORMAT]
[0]Consistency Checker Vs Job Description:
[1]Inconsistencies With Job Description: Number of inconsistencies found (return 'None' if no inconsistencies). List of inconsistencies found, if any, must be a continuous block of text, composed of sentences separated by ";", not line breaks.
[1]Suggestions for Improvement: List of suggestions for improvement, if any (return 'None' if no suggestions). must be a continuous block of text, composed of sentences separated by ";", not line breaks.

[INPUT]
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
            "job_description": ""
        },
        "prompt_in": 
"""[REQUEST]
Given a list of courses taken on a given program and a job description, extract the 5 most relevant courses that match the skills and requirements outlined in the job description.
Follow these guidelines when extracting courses and returning them:
- Do not include any courses not present in the original courses list.
- Do not use line breaks inside any subsection.
- Courses must be comma-separated and follow the format below.
- Include the prefix [1] at the start of each line (as seen in the format below).
- Return the requested information, strictly filling out the OUTPUT FORMAT.
- Be mindful that courses may or may not have a course code (represented by "XXX001" in the OUTPUT FORMAT section)

[OUTPUT FORMAT]
[1]Courses: XXX001 Course Name1, XXX002 Course Name2, XXX003 Course Name3...

[INPUT]
INPUT list of courses taken on a given program:
{courses}

INPUT job description:
{job_description}


""",
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["strict", "digits", "[1]Courses:"]
    },
    # NON-STANDARD CALLS
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

[INPUT]
INPUT sections from a resume:
{sections_text}


"""
        },
        "prompt_in":
"""[REQUEST]
Given a number of sections from a resume, summarize the sections in a wholistic manner while following these guidelines:
- Be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
- Include all information, competencies, achievements, and skills, this is a wholistic summary of the candidate's qualifications.
- Keep in mind that these summaries will be used in a "Sliding Window" approach to summarize the entire resume effectively, so include information that is relevant for the overall context of the resume.
- Return the requested information, strictly filling out the OUTPUT FORMAT.

[OUTPUT FORMAT]
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
"""[REQUEST]
Given 2 resume section summaries, create a new summary that incorporates all two summaries, following these guidelines:
- Be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
- Include ALL information, competencies, achievements, and skills, for this is a wholistic summary of the candidate's qualifications. Do not miss any skills.
- When referring to the candidate, use their name: {candidate_name} or their title: {candidate_title}
- Return the requested information, strictly filling out the OUTPUT FORMAT.

[OUTPUT FORMAT]
[S]{section1_name} + {section2_name} Sections Summary: Wholistic summary of the sections' information, competencies, achievements, and skills.

[INPUT]
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
            "async_calls": ["standard_ollama_call_async"]
            }, 
        "prompt_in": 
"""[REQUEST]
Given 3 resume section summaries, create a new summary that incorporates all two summaries, following these guidelines:
- Be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
- Include ALL information, competencies, achievements, and skills, for this is a wholistic summary of the candidate's qualifications. Do not miss any skills.
- When referring to the candidate, use their name: {candidate_name} or their title: {candidate_title}
- Return the requested information, strictly filling out the OUTPUT FORMAT.

[OUTPUT FORMAT]
[S]{section1_name} + {section2_name} + {section3_name} Sections Summary: Wholistic summary of the sections' information, competencies, achievements, and skills.

[INPUT]
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
            "async_calls": ["standard_ollama_call_async"]
            }, 
        "prompt_in": 
"""[REQUEST]
Given 4 resume section summaries, create a new summary that incorporates all two summaries, following these guidelines:
- Be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
- Include ALL information, competencies, achievements, and skills, for this is a wholistic summary of the candidate's qualifications. Do not miss any skills.
- When referring to the candidate, use their name: {candidate_name} or their title: {candidate_title}
- Return the requested information, strictly filling out the OUTPUT FORMAT.

[OUTPUT FORMAT]
[S]{section1_name} + {section2_name} + {section3_name} + {section4_name} Sections Summary: Wholistic summary of the sections' information, competencies, achievements, and skills.

[INPUT]
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
"""[REQUEST]
Given all summarized sections of a resume, create a wholistic summary of all of them, following these guidelines:
- Include the candidate's contact information, as well as their title and name.
- Include any certifications or qualifications.
- Include all education.
- Include all projects, work experience, and volunteering and leadership roles.
- Include all information, competencies, achievements, and skills, this is a wholistic summary of the candidate's qualifications.
- Maintain the context and flow between the sections.
- Be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
- When filling out the output format, do not forget to include the "[0]Summary:" text before the actual summary.
- Return the requested information, strictly filling out the OUTPUT FORMAT.

[OUTPUT FORMAT]
[0]Summary: Wholistic summary of all sections, presented as a single continuous string of text.

[INPUT]
INPUT summarized sections of a resume:
{slides_txt}

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
"""[REQUEST]
Given a list containing a per-section analysis of a two resumes, comparing the synthesized data in the new resume (which has been tailored to a particular job description) against the original, synthesize a report which extracts the following data from the list of analyses:
- Whether the new resume is consistent with the original resume, meaning that all information in the new resume is present in the original resume, even if paraphrased.
- Whether the new resume is consistent with itself, meaning that there should be no contradictions or inconsistencies in the information provided.
The report should follow these guidelines:
- Be mindful not to include any line breaks in  the content of any of the sections/subsections.
- Be as objective as possible, and if you must make assumptions, make very conservative assumptions
- Do not create nor imagine any data that is not present in the original data.
- When filling out the output format, include the numbers "[0]", "[1]", and do not modify the format.
- Return the requested information, strictly filling out the OUTPUT FORMAT.

[OUTPUT FORMAT]
[0]Consistency Checker Vs Original Resume:
[1]Inconsistencies With Original Resume: Number of inconsistencies found (return 'None' if no inconsistencies). List of inconsistencies found, if any, must be a continuous block of text, composed of sentences separated by ";", not line breaks.
[1]Inconsistencies With Self: Number of inconsistencies found (return 'None' if no inconsistencies). List of inconsistencies found, if any, must be a continuous block of text, composed of sentences separated by ";", not line breaks.
[1]Suggestions for Improvement: List of suggestions for improvement, if any (return 'None' if no suggestions). must be a continuous block of text, composed of sentences separated by ";", not line breaks.

[INPUT]
INPUT list containing a per-section analysis of the resumes, comparing the synthesized data in the new resume against the original:
{all_analysis}

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