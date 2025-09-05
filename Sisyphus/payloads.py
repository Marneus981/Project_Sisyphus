from config import CONFIG
DEFAULT_MODEL = "llama3:8b"
DEFAULT_URL = "http://localhost:11434"
PAYLOADS= {
    # STANDARD CALLS
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
        "prompt_in": """Summarize the following job description by extracting key responsibilities, requirements, and highlighting needed skills, both technical and soft.
                        Don't forget to also include the Company Name and the Job Title.
                        Job Description:
                        {job_description}
                    """,
        "ollama_url": DEFAULT_URL, #Set at runtime
        "sample_starts": [] #[type, sample starts]
    },
    "step0_volunteering_and_leadership": {
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
        "prompt_in": """Given the following "Volunteering and Leadership" resume section:
                        {raw_cv_data}
                        And the following job description:
                        {job_description}
                        Select up to 5 roles based on the job description. When selecting:
                        - If the total number of roles is less than or equal to 5, return all of them.
                        - If the total number of roles is greater than or equal to 5 before selection: Select the most relevant 5 roles based on the job description.
                        - Do not change the name of the roles.
                        - Prioritize roles that match relevant skills and experience present in the job description.
                        - It is okay to not select any roles if none are relevant.
                        - Display the Role Titles explicitly; do not write "Role Title:" before the Role Title
                        Output the selected roles strictly in the following format, without changing the role title text (do not include any text before [R] or after the role title text):
                        [R]Role Title 1
                        [R]Role Title 2
                        [R]Role Title 3
                        [R]Role Title 4
                        [R]Role Title 5
                    """,
        "ollama_url": DEFAULT_URL, #Set at runtime
        "sample_starts": ["flexible", "cap_letters", "[R]"]
    },
    "step3_volunteering_and_leadership": {
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
        "prompt_in": """Given the "Description" and "Skills" subsections of a role belonging to the "Volunteering and Leadership" section of a resume:
                        {experience}
                        And the following job description:
                        {job_description}
                        Rewrite the experience to best match the job description, following these guidelines:
                        - Do not include any information not present in the original experience.
                        - In the Description subsection, rewrite to highlight achievements and relevant skills for the job, using up to 2 sentences (max 20 words each), as a single block of text.
                        - In the Skills subsection, include up to 6 relevant skills (Programming Languages, Technical Skills, Soft Skills). Every skill category should be present, even if empty.
                        - Do not use line breaks inside any subsection. Do not use the ":" character in the Description.
                        - Skills must be comma-separated and follow the format below. 
                        - If there are no skills in a given category, use " ", then follow up as the format below indicates 
                            - For example: Programming Languages: ; Technical Skills: ; Soft Skills: Communication, Teamwork
                        - Include the prefix [1] at the start of each line (as seen in the format below).
                        Return only the revised section in the following format:
                        [1]Description: Brief description for Role 1.
                        [1]Skills: Programming Languages: ...; Technical Skills: ...; Soft Skills: ...
                    """,
        "ollama_url": DEFAULT_URL, #Set at runtime
        "sample_starts": ["strict", "digits", "[1]Description:", "[1]Skills:"]
    },
    "step0_work_experience": {
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
        "prompt_in": """Given the following "Work Experience" resume section:
                        {raw_cv_data}
                        And the following job description:
                        {job_description}
                        Select up to 5 jobs based on the job description. When selecting:
                        - If the total number of jobs is less than or equal to 5, return all of them.
                        - If the total number of jobs is greater than or equal to 5 before selection: Select the most relevant 5 jobs based on the job description.
                        - Do not change the name of the jobs.
                        - Prioritize jobs that match relevant skills and experience present in the job description.
                        - It is okay to not select any jobs if none are relevant.
                        - Display the Job Titles explicitly; do not write "Job Title:" before the Job Title
                        Output the selected jobs strictly in the following format, without changing the job title text (do not include any text before [J] or after the job title text):
                        [J]Job Title 1
                        [J]Job Title 2
                        [J]Job Title 3
                        [J]Job Title 4
                        [J]Job Title 5
                    """,
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["flexible", "cap_letters", "[J]"]
    },
    "step3_work_experience": {
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
        "prompt_in": """Given the "Description" and "Skills" subsections of a role belonging to the "Work Experience" section of a resume:
                        {experience}
                        And the following job description:
                        {job_description}
                        Rewrite the experience to best match the job description, following these guidelines:
                        - Do not include any information not present in the original experience.
                        - In the Description subsection, rewrite to highlight achievements and relevant skills for the job, using up to 2 sentences (max 20 words each), as a single block of text.
                        - In the Skills subsection, include up to 6 relevant skills (Programming Languages, Technical Skills, Soft Skills). Every skill category should be present, even if empty.
                        - Do not use line breaks inside any subsection. Do not use the ":" character in the Description.
                        - Skills must be comma-separated and follow the format below. 
                        - If there are no skills in a given category, use " ", then follow up as the format below indicates 
                            - For example: Programming Languages: ; Technical Skills: ; Soft Skills: Communication, Teamwork
                        - Include the prefix [1] at the start of each line (as seen in the format below).
                        Return only the revised section in the following format:
                        [1]Description: Brief description for Role 1.
                        [1]Skills: Programming Languages: ...; Technical Skills: ...; Soft Skills: ...
                    """,
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["strict", "digits" ,"[1]Description:", "[1]Skills:"]
    },
    "step0_projects": {
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
        "prompt_in": """Given the following "Projects" resume section:
                        {raw_cv_data}
                        And the following job description:
                        {job_description}
                        Select up to 5 projects based on the job description. When selecting:
                        - If the total number of projects is less than or equal to 5, return all of them.
                        - If the total number of projects is greater than or equal to 5 before selection: Select the most relevant 5 projects based on the job description.
                        - Do not change the name of the projects.
                        - Prioritize projects that match relevant skills and experience present in the job description.
                        - It is okay to not select any projects if none are relevant.
                        - Display the Project Titles explicitly; do not write "Project Title:" before the Project Title
                        Output the selected projects strictly in the following format, without changing the project title text (do not include any text before [P] or after the project title text):
                        [P]Project Title 1
                        [P]Project Title 2
                        [P]Project Title 3
                        [P]Project Title 4
                        [P]Project Title 5
                    """,
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["flexible", "cap_letters", "[P]"]
    },
    "step3_projects": {
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
        "prompt_in": """Given the "Description" and "Skills" subsections of a project belonging to the "Projects" section of a resume:
                        {experience}
                        And the following job description:
                        {job_description}
                        Rewrite the experience to best match the job description, following these guidelines:
                        - Do not include any information not present in the original experience.
                        - In the Description subsection, rewrite to highlight achievements and relevant skills for the job, using up to 2 sentences (max 20 words each), as a single block of text.
                        - In the Skills subsection, include up to 6 relevant skills (Programming Languages, Technical Skills, Soft Skills). Every skill category should be present, even if empty.
                        - Do not use line breaks inside any subsection. Do not use the ":" character in the Description.
                        - Skills must be comma-separated and follow the format below. 
                        - If there are no skills in a given category, use " ", then follow up as the format below indicates 
                            - For example: Programming Languages: ; Technical Skills: ; Soft Skills: Communication, Teamwork
                        - Include the prefix [1] at the start of each line (as seen in the format below).
                        Return only the revised section in the following format:
                        [1]Description: Brief description for Project 1.
                        [1]Skills: Programming Languages: ...; Technical Skills: ...; Soft Skills: ...
                    """,
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["strict", "digits", "[1]Description:", "[1]Skills:"]
    },
    "step0_prune_experiences": {
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
        "prompt_in": """Given the following experiences across 3 resume sections (Volunteering and Leadership, Work Experience, and Projects):
                        {experiences}
                        And the following job description:
                        {job_description}
                        Select up to 5 experiences based on the job description. When selecting:
                        - If the total number of experiences/roles is less than or equal to 5, return all of them.
                        - If the total number of experiences/roles is greater than or equal to 5 before selection: Select the most relevant 5 experiences/roles based on the job description.
                        - Do not change the name of the experiences/roles.
                        - Prioritize projects that match relevant skills and experience present in the job description.
                        - It is okay to not select any experiences from a given section if none are relevant. Remember that [R], [J], and [P] indicate the section they belong to (R is Volunteering and Leadership, J is Work Experience, and P is Projects).
                        Return your response strictly in the following format, without changing the role/job title/project title text (also do not include any text before [R], [J], or [P] or after the role/job title/project title text):
                        [X]Role/Job Title/Project Title 1
                        ...
                        [X]Role/Job Title/Project Title 5
                        Where [X] indicates the type of experience:
                        - [R] Role belongs to Volunteering and Leadership
                        - [J] Job Title belongs to Work Experience
                        - [P] Project Title belongs to Projects
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
        "prompt_in": """Given the following section from a resume:
                        {section}
                        Summarize the sections in a wholistic manner while following these guidelines:
                        - Be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
                        - Include all information, competencies, achievements, and skills, this is a wholistic summary of the candidate's qualifications.
                        Return the summarized information as a single continuous string of text, following this format strictly:
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
        "prompt_in": """Given the following general information from a resume:
                        {general_info_text}
                        Summarize the general information section of a resume in a wholistic manner; be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
                        Since this is a summary of a resume's general information, you need to include the candidate's Name, Contact Information, Title, and Languages Spoken.
                        Return the summarized general information as follows:
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
        "prompt_in": """Given the following skills information from a resume:
                        {skill_section}
                        Summarize the skills section of a resume in a wholistic manner; be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
                        Return the summarized skills information as follows:
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
        "prompt_in": """Given the following wholistic summary of a resume:
                        {prev_summary}
                        And the following job description:
                        {job_description}
                        Tailor a Summary section for a resume to best match the job description; follow these guidelines:
                        - Write the tailored summary section as the candidate, not as an external observer.
                        - The summary mustn't exceed 100 words.
                        - Do not line break the summary section, it should be a continuous block of text.
                        - When mentioning specific skills or experiences, these must be relevant to the job description; give preference to those that appear on both the resume and the job description, particularly those which demonstrate the candidate's technical expertise.
                        - In the format below, do not include any text before "[0]" or after the requested information.
                        Return only the revised section and strictly follow the format below, filling in the parts that have [fill-in:"text"]:
                        [0]Summary: Despite limited work experience, I bring strong work ethic, adaptability and curiosity. Experienced in [fill-in:"specific skills thanks to certain experiences"]. Now seeking a position that offers growth and learning opportunities.
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
        "prompt_in": """Given the following list of "Programming Languages", "Technical Skills" and "Soft Skills" considered to be relevant for the job description below them:
                        {cv_data}
                        And the following job description:
                        {job_description}
                        Prune a '{section}' section to best match the job description , following the guidelines below:
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
        "prompt_in": """Given the following raw untailored resume section:
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
        "prompt_in": """Given the following wholistic summary of a resume:
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
    "consistency_checker_vs_job_desc_cv": {
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
        "prompt_in": """Given the following summary of a resume:
                        {cv_data}
                        And the job description the aforementioned resume has been tailored to:
                        {job_description}
                        Perform a consistency check on the tailored resume against the job description. This consistency check will check if the resume is consistent with the job description, meaning that all skills and experiences mentioned in the resume should be relevant to the job description.
                        Follow these guidelines:
                        - Be mindful not to include any line breaks in the content of any of the sections/subsections.
                        - Be as objective as possible, and do not make any assumptions about the data.
                        - Do not create nor imagine any data that is not present in the original data.
                        The consistency check should be returned strictly in the following format (include the numbers "[0]", "[1]", do not modify the format):
                        [0]Consistency Checker Vs Job Description:
                        [1]Inconsistencies With Job Description: [Yes/No]; [List of inconsistencies found, if any; return 'None' if no inconsistencies; must be a continuous block of text, composed of sentences separated by ".", not line breaks]
                        [1]Suggestions for Improvement: [List of suggestions for improvement, if any; return 'None' if no suggestions; must be a continuous block of text, composed of sentences separated by ".", not line breaks]
                    """,
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["strict", "digits", "[0]Consistency Checker Vs Job Description:", "[1]Inconsistencies With Job Description:", "[1]Suggestions for Improvement:"]
    },
    "consistency_checker_vs_job_desc_cl": {
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
        "prompt_in": """Given the following cover letter:
                        {cv_data}
                        And the job description the aforementioned resume has been tailored to:
                        {job_description}
                        Perform a consistency check on the tailored cover letter against the job description. This consistency check will check if the cover letter is consistent with the job description, meaning that all skills and experiences mentioned in the cover letter should be relevant to the job description.
                        Follow these guidelines:
                        - Be mindful not to include any line breaks in  the content of any of the sections/subsections.
                        - Be as objective as possible, and do not make any assumptions about the data.
                        - Do not create nor imagine any data that is not present in the original data.
                        The consistency check should be returned strictly in the following format (include the numbers "[0]", "[1]", do not modify the format):
                        [0]Consistency Checker Vs Job Description:
                        [1]Inconsistencies With Job Description: [Yes/No]; [List of inconsistencies found, if any; return 'None' if no inconsistencies; must be a continuous block of text, composed of sentences separated by ".", not line breaks] 
                        [1]Suggestions for Improvement: [List of suggestions for improvement, if any; return 'None' if no suggestions; must be a continuous block of text, composed of sentences separated by ".", not line breaks]
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
        "prompt_in": """Given the following courses taken on a given program:
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
        "prompt_in": """Given the following sections from a resume:
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
    "tailor_volunteering_and_leadership": {
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
    "tailor_work_experience": {
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
    "tailor_projects": {
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
    "prune_experiences": {
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
            "systems": ["", ""],
            "standard_calls": ["step0_prune_experiences"]
            }, 
        "prompt_in": "", #Empty
        "ollama_url": DEFAULT_URL,
        "sample_starts": ["flexible", "digits", "[0]", "[1]"]#Might lead to error, check later
    },
    #ASYNC
    "standard_async": {
        "call_id": "standard_async", 
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
    "tailor_courses"

]
ASYNC = [
    "standard_async"
]