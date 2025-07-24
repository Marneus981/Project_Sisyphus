import requests
from Sisyphus import helpers
from Sisyphus import parsers
DEFAULT_MODEL = "llama3:8b"
DEFAULT_URL = "http://localhost:11434"


def tailor_volunteering_and_leadership(model=DEFAULT_MODEL, system="", ollama_url=DEFAULT_URL, cv_data="", job_description="", section="Volunteering and Leadership"):
    
    # - Volunteering and Leadership (Choose Which To Include Based on Job Description)
    # - Volunteering X
        # - Role
        # - Organization
        # - Location
        # - Duration
        # - Description
        # - Skills (Choose Which To Include Based on Job Description)
            # - Programming Languages
            # - Technical Skills
            # - Soft Skills
    
    prompt = f"""
    Given the following section on all volunteering and leadership experiences for a resume:
    {cv_data}
    And the following job description:
    {job_description}
    Tailor a '{section}' section for a resume to best match the job description; 
    make sure to rank the experiences and their respective skills from most relevant to least 
    (ordering them in descending order will sufice, no need for explicitly saying the ranking). 
    Return only the revised section and strictly follow the format:

    [0]Volunteering and Leadership:
    [1]Role: Role Name 1
    [1]Organization: Organization Name 1
    [1]Location: Location Name 1
    [1]Duration: Start Year 1/Start Month 1 - End Year 1/End Month 1
    [1]Description: Brief description of the role and responsibilities for Role 1.
    [1]Skills: Programming Languages: Programming Language 1, Programming Language 2; Technical Skills: Technical Skill 1, Techincal Skill 2; Soft Skills: Soft Skill 1, Soft Skill 2
    [1]Role: Role Name 2
    [1]Organization: Organization Name 2
    [1]Location: Location Name 2
    [1]Duration: Start Year 2/Start Month 2 - End Year 2/End Month 2
    [1]Description: Brief description of the role and responsibilities for Role 2.
    [1]Skills: Programming Languages: Programming Language 3, Programming Language 4; Technical Skills: Technical Skill 3, Techincal Skill 4; Soft Skills: Soft Skill 3, Soft Skill 4
    
    Be mindful not to include any line breaks in any of the sections.
    Do note that the section may not exist in the CV, in which case you should return an empty section.
    The description section should be a continuous block of text, without line breaks, composed of 1 or 2 sentences that concisely highlight the achievements and relevant skills attained at each role.
    The description section should not include the ":" character.
    """
    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        return result.get("response", "")
    except Exception:
        print("Ollama response was not valid JSON:")
        print(response.text)
        return "Error: Ollama response was not valid JSON."

def tailor_work_experience(model=DEFAULT_MODEL, system="", ollama_url=DEFAULT_URL, cv_data="", job_description="", section="Work Experience"):
    
    # - Work Experience
    # - Work Experience X (Choose Which To Include Based on Job Description)
        # - Job Title
        # - Company
        # - Location
        # - Duration
        # - Description
        # - Skills (Choose Which To Include Based on Job Description)
            # - Programming Languages
            # - Technical Skills
            # - Soft Skills

    """
    Tailors the work experience section based on the job description using Ollama.
    """
    prompt = f"""
    Given the following section on all work experiences for a resume:
    {cv_data}
    And the following job description:
    {job_description}
    Tailor a '{section}' section for a resume to best match the job description;
    make sure to rank the experiences and their respective skills from most relevant to least
    (ordering them in descending order will suffice, no need for explicitly saying the ranking).
    Return only the revised section and strictly follow the format:

    [0]Work Experience:
    [1]Job Title: Job Title 1
    [1]Company: Company 1
    [1]Location: Location Name 1
    [1]Duration: Start Year 1/Start Month 1 - End Year 1/End Month 1
    [1]Description: Brief description of the role and responsibilities for Role 1.
    [1]Skills: Programming Languages: Programming Language 1, Programming Language 2; Technical Skills: Technical Skill 1, Techincal Skill 2; Soft Skills: Soft Skill 1, Soft Skill 2
    [1]Job Title: Job Title 2
    [1]Company: Company 2
    [1]Location: Location Name 2
    [1]Duration: Start Year 2/Start Month 2 - End Year 2/End Month 2
    [1]Description: Brief description of the role and responsibilities for Role 2.
    [1]Skills: Programming Languages: Programming Language 3, Programming Language 4; Technical Skills: Technical Skill 3, Techincal Skill 4; Soft Skills: Soft Skill 3, Soft Skill 4

    Be mindful not to include any line breaks in any of the sections.
    Do note that the section may not exist in the CV, in which case you should return an empty section.
    The description section should be a continuous block of text, without line breaks, composed of 1 or 2 sentences that concisely highlight the achievements and relevant skills attained at each role.
    The description section should not include the ":" character.
    """
    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        return result.get("response", "")
    except Exception:
        print("Ollama response was not valid JSON:")
        print(response.text)
        return "Error: Ollama response was not valid JSON."

def tailor_projects(model=DEFAULT_MODEL, system="", ollama_url=DEFAULT_URL, cv_data="", job_description="", section="Projects"):
    
    # - Projects
    # - Project X (Choose Which To Include Based on Job Description)
        # - Project Title
        # - Type (e.g., Personal, Academic, Professional)
        # - Duration
        # - Description
        # - Skills (Choose Which To Include Based on Job Description)
            # - Programming Languages
            # - Technical Skills
            # - Soft Skills

    """
    Tailors the projects section based on the job description using Ollama.
    """
    prompt = f"""
    Given the following section on all projects for a resume:
    {cv_data}
    And the following job description:
    {job_description}
    Tailor a '{section}' section for a resume to best match the job description;
    make sure to rank the projects and their respective skills from most relevant to least
    (ordering them in descending order will suffice, no need for explicitly saying the ranking).
    Return only the revised section and strictly follow the format:

    [0]Projects:
    [1]Project Title: Project Title 1
    [1]Type: Type of Project 1 (e.g., Personal, Academic, Professional)
    [1]Duration: Start Year 1/Start Month 1 - End Year 1/End Month 1
    [1]Description: Brief description of the role and responsibilities for Role 1.
    [1]Skills: Programming Languages: Programming Language 1, Programming Language 2; Technical Skills: Technical Skill 1, Techincal Skill 2; Soft Skills: Soft Skill 1, Soft Skill 2
    [1]Project Title: Project Title 2
    [1]Type: Type of Project 2 (e.g., Personal, Academic, Professional)
    [1]Duration: Start Year 2/Start Month 2 - End Year 2/End Month 2
    [1]Description: Brief description of the role and responsibilities for Role 2.
    [1]Skills: Programming Languages: Programming Language 3, Programming Language 4; Technical Skills: Technical Skill 3, Techincal Skill 4; Soft Skills: Soft Skill 3, Soft Skill 4

    Be mindful not to include any line breaks in any of the sections.
    Do note that the section may not exist in the CV, in which case you should return an empty section.
    The description section should be a continuous block of text, without line breaks, composed of 1 or 2 sentences that concisely highlight the achievements and relevant skills attained at each role.
    The description section should not include the ":" character.
    """
    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        return result.get("response", "")
    except Exception:
        print("Ollama response was not valid JSON:")
        print(response.text)
        return "Error: Ollama response was not valid JSON."

def tailor_summary(model=DEFAULT_MODEL, system="", ollama_url=DEFAULT_URL, cv_data="", job_description="", section="Summary"):
    
    # - Summary (LAST; Based on Job Description AND Overall Resume)
    
    """
    Tailors the summary section based on the job description using Ollama.
    """
    prompt = f"""
    Given the following already tailored CV, with no summary section:
    {cv_data}
    And the following job description:
    {job_description}
    Tailor a '{section}' section for a resume to best match the job description;
    Make sure to mention the most relevant skills and experiences from the CV that match the job description, as well as the amount of languages known.
    Return only the revised section and strictly follow the format:

    [0]Summary: Brief summary of the candidate's qualifications, skills, and experiences relevant to the job description.
    
    Do not line break the summary section, it should be a continuous block of text.
    Do note that the section may not exist in the CV, in which case you should return an empty section. Lastly, I reiterate that you will only return the tailored section, no explanations or additional text.
    """
    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        return result.get("response", "")
    except Exception:
        print("Ollama response was not valid JSON:")
        print(response.text)
        return "Error: Ollama response was not valid JSON."

def return_text_with_skills(cv_text):
    #Note: text: comma separated skills, dict: section to subsections to lists
    return_list = []
    programming_skills = []
    technical_skills = []
    soft_skills = []

    lines = cv_text.splitlines()
    for line in lines:
        if line.startswith("[1]Skills: "):
            parts = line.split("; ")
            part0 = parts[0].split(": ")
            #[1]Skills
            #Programming Languages
            #Programming Language N1, ..., Programming Language NN
            part0_prog = part0[2]
            part0_prog_splt = part0_prog.split(", ")
            programming_skills += part0_prog_splt

            part1 = parts[1].split(": ")
            #Technical Skills
            #Technical Skill N1, ..., Techincal Skill NN
            part1_tech = part1[1]
            part1_tech_splt = part1_tech.split(", ")
            technical_skills += part1_tech_splt

            part2 = parts[2].split(": ")
            #Soft Skills
            #Soft Skill N1, ..., Soft Skill NN
            part2_soft = part2[1]
            part2_soft_splt = part2_soft.split(", ")
            soft_skills += part2_soft_splt
        else:
            return_list.append(line)

    #Join return list into a line break separated string
    return_text = "\n".join(return_list)
    #Remove duplicate entries, sort alphabetically, make final lines
    skill = "[0]Skills:"
    prog_list = list(dict.fromkeys(programming_skills))
    prog_list.sort()
    prog = "[1]Programming Languages: " + ", ".join(prog_list)
    tech_list = list(dict.fromkeys(technical_skills))
    tech_list.sort()
    tech = "[1]Technical Skills: " + ", ".join(tech_list)
    soft_list = list(dict.fromkeys(soft_skills))
    soft_list.sort()
    soft = "[1]Soft Skills: " + ", ".join(soft_list)

    return "\n".join([return_text,skill,prog,tech,soft])

def tailor_skills(model=DEFAULT_MODEL, system="", ollama_url=DEFAULT_URL, cv_data="", job_description="", section="Skills"):
    """
    Given a cv_data containing text pertaining to all the skills considered 
    to be relevant in the previous steps of the resume-generating algorithm,
    and a job description: Return a pruned "Skills" description with:
        3 MAX entries in "Programming Languages"
        5 MAX entries in "Technical Skills"
        4 MAX entries in "Soft Skills"
    """

    prompt = f"""
    Given the following list of "Programming Languages", "Technical Skills" and "Soft Skills" considered to be relevant for the job description below them:
    {cv_data}
    And the following job description:
    {job_description}
    Prune a '{section}' section to best match the job description , following the guidelines below:
        Return 3 MAXIMUM entries under "Programming Languages" (MINIMUM 0 entries)
        Return 5 MAXIMUM entries under "Technical Skills" (MINIMUM 0 entries)
        Return 4 MAXIMUM entries under "Soft Skills" (MINIMUM 0 entries)
        Do not line break any line containing the relevant skills, it should follow the format below strictly.
        Do note that the section may not exist in the CV, in which case you should return an empty section. 
        Lastly, I reiterate that you will only return the tailored section, no explanations or additional text.
        Return only the revised section and strictly follow the format:

        [0]Skills:
        [1]Programming Languages: Programming Language 1, Programming Language 2, Programming Language 3
        [1]Technical Skills: Technical Skill 1, Technical Skill 2, Technical Skill 3, Technical Skill 4, Technical Skill 5
        [1]Soft Skills: Soft Skill 1, Soft Skill 2, Soft Skill 3, Soft Skill 4
    """
    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        return result.get("response", "")
    except Exception:
        print("Ollama response was not valid JSON:")
        print(response.text)
        return "Error: Ollama response was not valid JSON."
    
def consistency_checker_vs_job_desc(model=DEFAULT_MODEL, system="", ollama_url=DEFAULT_URL, cv_data="", job_description="", type="CV"):

    if type == "CV":
        prompt = f"""
        Given the following already-tailored resume:
        {cv_data}
        And the job description the aforementioned resume was tailored to:
        {job_description}
        Perform a consistency check on the tailored resume against the job description and itself. This consistency check should include:
        1. Check if the resume is consistent with the job description, meaning that all skills and experiences mentioned in the resume should be relevant to the job description.
        2. Provide suggestions for improvement.
        The consistency check should be returned strictly in the following format:

        [0]Consistency Checker Vs Job Description:
        [1]Job Description Consistency: [Yes/No]
        [1]Inconsistencies With Job Description: [List of inconsistencies found, if any; return 'None' if no inconsistencies; must be a continuous block of text, composed of sentences separated by ".", not line breaks]
        [1]Suggestions for Improvement: [List of suggestions for improvement, if any; return 'None' if no suggestions; must be a continuous block of text, composed of sentences separated by ".", not line breaks]

        Be mindful not to include any line breaks in  the content of any of the sections/subsections.
        Be as objective as possible, and do not make any assumptions about the data; this also means that you should create nor imagine any data that is not present in the original CV data.
        """
    elif type == "CL":
        prompt = f"""
        Given the following already-tailored cover letter:
        {cv_data}
        And the job description the aforementioned cover letter was tailored to:
        {job_description}
        Perform a consistency check on the tailored cover letter against the job description and itself. This consistency check should include:
        1. Check if the cover letter is consistent with the job description, meaning that all skills and experiences mentioned in the cover letter should be relevant to the job description.
        2. Provide suggestions for improvement.
        The consistency check should be returned strictly in the following format:

        [0]Consistency Checker Vs Job Description:
        [1]Job Description Consistency: [Yes/No]
        [1]Inconsistencies With Job Description: [List of inconsistencies found, if any; return 'None' if no inconsistencies; must be a continuous block of text, composed of sentences separated by ".", not line breaks]
        [1]Suggestions for Improvement: [List of suggestions for improvement, if any; return 'None' if no suggestions; must be a continuous block of text, composed of sentences separated by ".", not line breaks]

        Be mindful not to include any line breaks in  the content of any of the sections/subsections.
        Be as objective as possible, and do not make any assumptions about the data; this also means that you should create nor imagine any data that is not present in the original CV data.
        """
    
    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False
    }
    
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    
    try:
        result = response.json()
        return result.get("response", "")
    except Exception:
        print("Ollama response was not valid JSON:")
        print(response.text)
        return "Error: Ollama response was not valid JSON."
    
def consistency_checker_vs_cv(model=DEFAULT_MODEL, system="", ollama_url=DEFAULT_URL, cv_data="", cv_data_orig ="", type="CV"):
    if type == "CV":
        prompt = f"""
        Given the following already-tailored resume:
        {cv_data}
        And the original untoilored curriculum data:
        {cv_data_orig}
        Perform a consistency check on the tailored resume against the original curriculum data. This consistency check should include:
        1. Check if the resume is consistent with the original curriculum data, meaning that all skills and experiences mentioned in the resume should be present in the original CV data.
        2. Check if the resume is consistent with itself, meaning that there should be no contradictions or inconsistencies in the information provided.
        3. Provide suggestions for improvement.
        The consistency check should be returned strictly in the following format:

        [0]Consistency Checker Vs Cv:
        [1]CV Consistency: [Yes/No]
        [1]Inconsistencies With CV: [List of inconsistencies found, if any; return 'None' if no inconsistencies; must be a continuous block of text, composed of sentences separated by ".", not line breaks]
        [1]Self Consistency: [Yes/No]
        [1]Inconsistencies With Self: [List of inconsistencies found, if any; return 'None' if no inconsistencies; must be a continuous block of text, composed of sentences separated by ".", not line breaks]
        [1]Suggestions for Improvement: [List of suggestions for improvement, if any; return 'None' if no suggestions; must be a continuous block of text, composed of sentences separated by ".", not line breaks]

        Be mindful not to include any line breaks in  the content of any of the sections/subsections.
        Be as objective as possible, and do not make any assumptions about the data; this also means that you should create nor imagine any data that is not present in the original CV data.
        """
    elif type == "CL":
        prompt = f"""
        Given the following already-tailored cover letter:
        {cv_data}
        And the resume meant to accompany it on a job application:
        {cv_data_orig}
        Perform a consistency check on the tailored cover letter against the resume. This consistency check should include:
        1. Check if the cover letter is consistent with the resume, meaning that all skills and experiences mentioned in the cover letter should be present in the resume.
        2. Check if the cover letter is consistent with itself, meaning that there should be no contradictions or inconsistencies in the information provided.
        3. Provide suggestions for improvement.
        The consistency check should be returned strictly in the following format:

        [0]Consistency Checker Vs Resume:
        [1]Resume Consistency: [Yes/No]
        [1]Inconsistencies With Resume: [List of inconsistencies found, if any; return 'None' if no inconsistencies; must be a continuous block of text, composed of sentences separated by ".", not line breaks]
        [1]Self Consistency: [Yes/No]
        [1]Inconsistencies With Self: [List of inconsistencies found, if any; return 'None' if no inconsistencies; must be a continuous block of text, composed of sentences separated by ".", not line breaks]
        [1]Suggestions for Improvement: [List of suggestions for improvement, if any; return 'None' if no suggestions; must be a continuous block of text, composed of sentences separated by ".", not line breaks]

        Be mindful not to include any line breaks in  the content of any of the sections/subsections.
        Be as objective as possible, and do not make any assumptions about the data; this also means that you should create nor imagine any data that is not present in the original CV data.
        """
    
    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False
    }
    
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    
    try:
        result = response.json()
        return result.get("response", "")
    except Exception:
        print("Ollama response was not valid JSON:")
        print(response.text)
        return "Error: Ollama response was not valid JSON."
    
def make_cover_letter_text(model=DEFAULT_MODEL, system="", ollama_url=DEFAULT_URL, cv_data="", job_description="", section="Cover Letter"):
    """
    Given a tailored resume containing education, experiences, projects and skills considered 
    to be relevant a job description: Return a cover letter tailored to the job description.
    """

    prompt = f"""
    Given the following already-tailored resume:
    {cv_data}
    And the following job description:
    {job_description}
    Write a cover letter tailored to the job description, following the guidelines below:
        2.It should highlight the most relevant skills and experiences from the CV that match the job description.
        3.It should be written in a professional tone.
        4.It should include line breaks if deemed necessary to maintain good readability.
        5.Whenever a line break occurs, it should start with "[1]New ParagraphX: " and then the text of the new paragraph; 
        X starts at 0 and goes up to 3.
        6.Strictly follow the format:

        [0]Cover Letter: 
        [1]New Paragraph0: Cover Letter introduction, mentioning the job title and company.
        [1]New Paragraph1: Briefly mention the most relevant skills and experiences from the CV that match the job description.
        [1]New Paragraph2: Additional information about the candidate's qualifications and how they align with the job requirements.
        [1]New Paragraph3: Closing statement, thanking the employer for their time and consideration.

        Note: the total words in the Cover Letter section should not exceed 400 words. This is a hard limit, so be concise and to the point.

    """
    
    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False
    }
    
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    
    try:
        result = response.json()
        return result.get("response", "")
    except Exception:
        print("Ollama response was not valid JSON:")
        print(response.text)
        return "Error: Ollama response was not valid JSON."
    
def compose_cover_letter_dictionary(model,cv_text, job_description):
    """
    Given a resume containing education, experiences, projects and skills considered 
    to be relevant a job description: Return a cover letter tailored to the job description.
    """

    

    #Extract the following sections and their subsections from the cv_text input: [0]Name, [0]Contact Information, [0]Title, [0]Languages using dict_splitter
    cv_dict = parsers.parse_cv_out(cv_text)
    split_dicts = parsers.dict_spliter(cv_dict)
    #Extract the name, contact information, title and languages from the split_dict
    name = split_dicts[0]
    title = split_dicts[2]
    languages =split_dicts[4]
    contact_info = split_dicts[1]
    #Make the cover letter text
    system = helpers.read_text_file(r"C:\CodeProjects\Sisyphus\Sisyphus\systems\system_cover_letter.txt")
    cover_letter_text = make_cover_letter_text(model = model, system=system,cv_data=cv_text,job_description=job_description)
    clean_cover_letter_text = helpers.filter_output(cover_letter_text)
    
    clean_cover_letter_dict = parsers.parse_cl(clean_cover_letter_text)
    
    #Make a list of dicts with name, title, languages, contact_info and clean_cover_letter_dict
    dict_list = [name,title,languages,contact_info,clean_cover_letter_dict]
    output_dict = parsers.dict_grafter(dict_list)
    #Return the output_dict
    return output_dict

    