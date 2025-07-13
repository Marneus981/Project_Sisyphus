import requests
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
    [1]Duration: Start Year 1 - End Year 1
    [1]Description: Brief description of the role and responsibilities for Role 1.
    [1]Skills: Programming Languages: Programming Language 1, Programming Language 2; Technical Skills: Event Technical Skill 1, Techincal Skill 2; Soft Skills: Soft Skill 1, Soft Skill 2
    [1]Role: Role Name 2
    [1]Organization: Organization Name 2
    [1]Location: Location Name 2
    [1]Duration: Start Year 2 - End Year 2
    [1]Description: Brief description of the role and responsibilities for Role 2.
    [1]Skills: Programming Languages: Programming Language 3, Programming Language 4; Technical Skills: Event Technical Skill 3, Techincal Skill 4; Soft Skills: Soft Skill 3, Soft Skill 4
    
    Be mindful not to include any line breaks in any of the sections.
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
    [1]Duration: Start Year 1 - End Year 1
    [1]Description: Brief description of the role and responsibilities for Role 1.
    [1]Skills: Programming Languages: Programming Language 1, Programming Language 2; Technical Skills: Event Technical Skill 1, Techincal Skill 2; Soft Skills: Soft Skill 1, Soft Skill 2
    [1]Job Title: Job Title 2
    [1]Company: Company 2
    [1]Location: Location Name 2
    [1]Duration: Start Year 2 - End Year 2
    [1]Description: Brief description of the role and responsibilities for Role 2.
    [1]Skills: Programming Languages: Programming Language 3, Programming Language 4; Technical Skills: Event Technical Skill 3, Techincal Skill 4; Soft Skills: Soft Skill 3, Soft Skill 4

    Be mindful not to include any line breaks in any of the sections.
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
    [1]Duration: Start Year 1 - End Year 1
    [1]Description: Brief description of the role and responsibilities for Role 1.
    [1]Skills: Programming Languages: Programming Language 1, Programming Language 2; Technical Skills: Event Technical Skill 1, Techincal Skill 2; Soft Skills: Soft Skill 1, Soft Skill 2
    [1]Project Title: Project Title 2
    [1]Type: Type of Project 2 (e.g., Personal, Academic, Professional)
    [1]Duration: Start Year 2 - End Year 2
    [1]Description: Brief description of the role and responsibilities for Role 2.
    [1]Skills: Programming Languages: Programming Language 3, Programming Language 4; Technical Skills: Event Technical Skill 3, Techincal Skill 4; Soft Skills: Soft Skill 3, Soft Skill 4

    Be mindful not to include any line breaks in any of the sections.
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

