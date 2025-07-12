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
    Given the following section on all volunteering and leadership experiences:
    {cv_data}
    And the following job description:
    {job_description}
    Tailor a '{section}' section for a resume to best match the job description; 
    make sure to rank the experiences and their respective skills from most relevant to least 
    (ordering them in descending order will sufice, no need for explicitly saying the ranking). 
    Return only the revised section.
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
    Given the following section on all work experiences:
    {cv_data}
    And the following job description:
    {job_description}
    Tailor a '{section}' section for a resume to best match the job description;
    make sure to rank the experiences and their respective skills from most relevant to least
    (ordering them in descending order will suffice, no need for explicitly saying the ranking).
    Return only the revised section.
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
    Given the following section on all projects:
    {cv_data}
    And the following job description:
    {job_description}
    Tailor a '{section}' section for a resume to best match the job description;
    make sure to rank the projects and their respective skills from most relevant to least
    (ordering them in descending order will suffice, no need for explicitly saying the ranking).
    Return only the revised section.
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
    Return only the revised section.
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

