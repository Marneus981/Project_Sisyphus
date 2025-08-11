from pydoc import text
import requests
from Sisyphus import helpers
from Sisyphus import parsers
import logging
DEFAULT_MODEL = "llama3:8b"
DEFAULT_URL = "http://localhost:11434"

# Set up logging
print = logging.info

def augment_output(input_text, reference_dict, type):
    allowed_types = ['volunteering_and_leadership','work_experience','projects', 'vl_w_p', ]
    if type not in allowed_types:
        raise ValueError(f"augment_output: Invalid type: {type}. Allowed types are: {allowed_types}")
    """
    Input is in format (if type is 'volunteering_and_leadership'):
    <Role Name 1>
    <Role Name 2>
    ...
    Output is in format (if type is 'volunteering_and_leadership'):
    [0]Volunteering and Leadership:
    [1]Role: <Role Name 1>
    [1]Organization: <Organization Name 1>
    [1]Location: <Location Name 1>
    [1]Duration: <Start Date 1> - <End Date 1>
    [1]Description: <Description 1>
    [1]Role: <Role Name 2>
    [1]Organization: <Organization Name 2>
    [1]Location: <Location Name 2>
    [1]Duration: <Start Date 2> - <End Date 2>
    [1]Description: <Description 2>
    ...

    Input is in format (if type is 'work_experience'):
    <Job Title 1>
    <Job Title 2>
    ...
    Output is in format (if type is 'work_experience'):
    [0]Work Experience:
    [1]Job Title: <Job Title 1>
    [1]Company: <Company Name 1>
    [1]Location: <Location Name 1>
    [1]Duration: <Start Date 1> - <End Date 1>
    [1]Description: <Description 1>
    [1]Job Title: <Job Title 2>
    [1]Company: <Company Name 2>
    [1]Location: <Location Name 2>
    [1]Duration: <Start Date 2> - <End Date 2>
    [1]Description: <Description 2>
    ...

    Input is in format (if type is 'projects'):
    <Project Title 1>
    <Project Title 2>
    ...
    Output is in format (if type is 'projects'):
    [0]Projects:
    [1]Project Title: <Project Title 1>
    [1]Type: <Type of Project 1>
    [1]Duration: <Start Date 1> - <End Date 1>
    [1]Description: <Description 1>
    [1]Project Title: <Project Title 2>
    [1]Type: <Type of Project 2>
    [1]Duration: <Start Date 2> - <End Date 2>
    [1]Description: <Description 2>
    ...

    Input is in format (if type is 'vl_w_p'):
    [V]<Volunteer Role 1>
    [J]<Job Title 1>
    [P]<Project Title 1>
    ...
    Output is in format (if type is 'vl_w_p'):
    [0]Volunteering and Leadership:
    [1]Role: <Role Name 1>
    [1]Organization: <Organization Name 1>
    [1]Location: <Location Name 1>
    [1]Duration: <Start Date 1> - <End Date 1>
    [1]Description: <Description 1>
    ...
    [0]Work Experience:
    [1]Job Title: <Job Title 1>
    [1]Company: <Company Name 1>
    [1]Location: <Location Name 1>
    [1]Duration: <Start Date 1> - <End Date 1>
    [1]Description: <Description 1>
    ...
    [0]Projects:
    [1]Project Title: <Project Title 1>
    [1]Type: <Type of Project 1>
    [1]Duration: <Start Date 1> - <End Date 1>
    [1]Description: <Description 1>

    Note:
    This assumes that the input is well-structured and follows the expected format for each type.
    It also assumes that all necessary information is provided for each entry and each role is unique.
    Ill be using a dict for easier access to the reference data.

    The goal of this function is to match the input entries with its output format.
    ...
    """
    #Split lines in input text and store them in a list of strings
    input_lines = input_text.strip().split('\n')
    
    tmp_dict = {}
    if type == 'volunteering_and_leadership':
        #Remove [R] marker at the start of each line
        input_lines = [line[3:] if line.startswith('[R]') else line for line in input_lines]
        return_list = []
        reference_list = reference_dict[type]
        for line in input_lines:
            for item in reference_list:
                if line.strip() == item['role']:
                    return_list.append(item)
                    reference_list.remove(item)
                    break
        tmp_dict[type] = return_list

    elif type == 'work_experience':
        #Remove [J] marker at the start of each line
        input_lines = [line[3:] if line.startswith('[J]') else line for line in input_lines]
        return_list = []
        reference_list = reference_dict[type]
        for line in input_lines:
            for item in reference_list:
                if line.strip() == item['job_title']:
                    return_list.append(item)
                    reference_list.remove(item)
                    break
        tmp_dict[type] = return_list

    elif type == 'projects':
        #Remove [P] marker at the start of each line
        input_lines = [line[3:] if line.startswith('[P]') else line for line in input_lines]
        return_list = []
        reference_list = reference_dict[type]
        for line in input_lines:
            for item in reference_list:
                if line.strip() == item['project_title']:
                    return_list.append(item)
                    reference_list.remove(item)
                    break
        tmp_dict[type] = return_list

    elif type == 'vl_w_p':
        # Remove [R], [J], [P] markers at the start of each line
        input_lines = [line[3:] if line.startswith(('[R]', '[J]', '[P]')) else line for line in input_lines]
        return_list = [[],[],[]]
        reference_list_vl = reference_dict['volunteering_and_leadership']
        reference_list_w = reference_dict['work_experience']
        reference_list_p = reference_dict['projects']
        for line in input_lines:
            found = False
            for item in reference_list_vl:
                if line.strip() == item['role']:
                    return_list[0].append(item)
                    reference_list_vl.remove(item)
                    found = True
                    break
            if found:
                continue
            for item in reference_list_w:
                if line.strip() == item['job_title']:
                    return_list[1].append(item)
                    reference_list_w.remove(item)
                    found = True
                    break
            if found:
                continue
            for item in reference_list_p:
                if line.strip() == item['project_title']:
                    return_list[2].append(item)
                    reference_list_p.remove(item)
                    found = True
                    break
        tmp_dict['volunteering_and_leadership'] = return_list[0]
        tmp_dict['work_experience'] = return_list[1]
        tmp_dict['projects'] = return_list[2]
    return tmp_dict

def prepare_input_text(input_text, type):
    allowed_types = ['volunteering_and_leadership','work_experience','projects', 'vl_w_p', ]
    if type not in allowed_types:
        raise ValueError(f"Invalid type: {type}. Allowed types are: {allowed_types}")
    # Split lines in input text and store them in a list of strings
    input_lines = input_text.strip().split('\n')
    return_list = []
    return_text = ''
    if type == 'volunteering_and_leadership':
        """
        Remove lines that start with:
        [0]Volunteering and Leadership:
        [1]Organization:
        [1]Location:
        [1]Duration:

        In the rest of the lines, remove [1]Role and [1]Description [1]Skills
        """
        for line in input_lines:
            if not line.startswith(("[0]Volunteering and Leadership:", "[1]Organization:", "[1]Location:", "[1]Duration:")):
                line = line.replace("[1]Role: ", "[R]").replace("[1]Description: ", "Description: ").replace("[1]Skills: ", "Skills: ").strip()
                if line:
                    return_list.append(line)
        for item in return_list:
            return_text += f"{item}\n"
        return return_text

    if type == 'work_experience':
        for line in input_lines:
            if not line.startswith(("[0]Work Experience:", "[1]Company:", "[1]Location:", "[1]Duration:")):
                line = line.replace("[1]Job Title: ", "[J]").replace("[1]Description: ", "Description: ").replace("[1]Skills: ", "Skills: ").strip()
                if line:
                    return_list.append(line)
        for item in return_list:
            return_text += f"{item}\n"
        return return_text
    if type == 'projects':
        for line in input_lines:
            if not line.startswith(("[0]Projects:", "[1]Type:", "[1]Duration:")):
                line = line.replace("[1]Project Title: ", "[P]").replace("[1]Description: ", "Description: ").replace("[1]Skills: ", "Skills: ").strip()
                if line:
                    return_list.append(line)
        for item in return_list:
            return_text += f"{item}\n"
        return return_text
    if type == 'vl_w_p':
        for line in input_lines:
            if not line.startswith(("[0]Volunteering and Leadership:", "[1]Organization:", "[1]Location:", "[1]Duration:",
                                    "[0]Work Experience:", "[1]Company:",
                                    "[0]Projects:", "[1]Type:")):
                line = line.replace("[1]Role: ", "[R]").replace("[1]Description: ", "Description: ").replace("[1]Skills: ", "Skills: ").replace("[1]Job Title: ", "[J]").replace("[1]Project Title: ", "[P]").strip()
                if line:
                    return_list.append(line)
        for item in return_list:
            return_text += f"{item}\n"
        return return_text

def clean_first_step(text):
    # Remove lines that do not start with [X] where X is a capitalized letter
    cleaned_lines = []
    for line in text.split('\n'):
        if line.startswith(("[R]", "[J]", "[P]")):
            cleaned_lines.append(line)
    return '\n'.join(cleaned_lines)  
"""
    raw text section>>>>prepare_input_text>>>Role;Description;Skills
    >>>Tailor function>>>Text list of chosen items>>>augment_output>>>tailored_dict (section)
"""
#For each main tailor function (including pruning), we need to create 3 functions
#Tailor Volunteering and Leadership
def summarize_job_description(job_description = "", system = "", ollama_url=DEFAULT_URL, model=DEFAULT_MODEL):
    # Summarize the job description by extracting key responsibilities and requirements
    # This is a placeholder implementation
    prompt = f"""
    Summarize the following job description by extracting key responsibilities and requirements.
    Also, highlight needed skills, both technical and soft.
    {job_description}
    """
    input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        response_text = result.get("response", "")
        output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        return response_text
    except Exception:
        print("Ollama response was not valid JSON:")
        print(response.text)
        return "Error: Ollama response was not valid JSON."

def step0_volunteering_and_leadership(model=DEFAULT_MODEL, system1="", ollama_url=DEFAULT_URL, 
                                       raw_cv_data="", job_description=""):
    prompt = f"""
Given the following "Volunteering and Leadership" resume section:
{raw_cv_data}
And the following job description:
{job_description}
Select up to 4 relevant experiences that best match the job description. If there are 4 or fewer experiences, include all of them. If there are no experiences, return an empty section.
Output the selected experiences strictly in the following format:
[R]Role Name 1
[R]Role Name 2
[R]Role Name 3
[R]Role Name 4
    """
    input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system1,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        response_text = result.get("response", "")
        output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        return response_text
    except Exception:
        print("Ollama response was not valid JSON:")
        print(response.text)
        return "Error: Ollama response was not valid JSON."

def step3_volunteering_and_leadership(model=DEFAULT_MODEL, system2="", ollama_url=DEFAULT_URL, 
                                       experience="", job_description=""):
    prompt = f"""
Given the following "Volunteering and Leadership" resume experience:
{experience}
And the following job description:
{job_description}
Rewrite the experience to best match the job description, following these guidelines:
- Keep all original subsections: Role, Organization, Location, Duration, Description, and Skills.
- In the Description subsection, rewrite to highlight achievements and relevant skills for the job, using up to 2 sentences (max 20 words each), as a single block of text.
- In the Skills subsection, include up to 6 relevant skills (Programming Languages, Technical Skills, Soft Skills). Every skill category should be present, even if empty.
- Do not use line breaks inside any subsection. Do not use the ":" character in the Description.
- If any subsection is missing, include it as empty.
- Skills must be comma-separated and follow the format below.
Return only the revised section in the following format:
[1]Role: Role Name 1
[1]Organization: Organization Name 1
[1]Location: Location Name 1
[1]Duration: Start Year 1/Start Month 1 - End Year 1/End Month 1
[1]Description: Brief description for Role 1.
[1]Skills: Programming Languages: ...; Technical Skills: ...; Soft Skills: ...
    """
    input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system2,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        response_text = result.get("response", "")
        output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        return response_text
    except Exception:
        print("Ollama response was not valid JSON:")
        print(response.text)
        return "Error: Ollama response was not valid JSON."

def tailor_volunteering_and_leadership(model=DEFAULT_MODEL, system1="", system2="", ollama_url=DEFAULT_URL, 
                                       raw_cv_data="", job_description_summary="", 
                                       section="volunteering_and_leadership", reference_dct={}):
    print(f"tailor_volunteering_and_leadership: raw_cv_data:\n" + raw_cv_data)
    step0 = prepare_input_text(raw_cv_data, type=section)
    print(f"tailor_volunteering_and_leadership: step0:\n" + step0)
    step1 = step0_volunteering_and_leadership(model=model, system1=system1, ollama_url=ollama_url, 
                                               raw_cv_data=step0, job_description=job_description_summary)
    print(f"tailor_volunteering_and_leadership: step1:\n" + step1)
    step1_clean = clean_first_step(step1).strip()
    print(f"tailor_volunteering_and_leadership: step1_clean:\n" + step1_clean)
    step2_dct = augment_output(step1_clean, reference_dct, type=section)
    print(f"tailor_volunteering_and_leadership: step2_dct:\n" + str(step2_dct))
    step2_text = helpers.filter_output(parsers.inv_parse_cv(step2_dct))
    print(f"tailor_volunteering_and_leadership: step2_text:\n" + step2_text)
    step3_text = []
    #Delete line that starts with [0]Volunteering and Leadership
    step2_text = step2_text.replace("[0]Volunteering and Leadership:", "")
    print(f"tailor_volunteering_and_leadership: step2_text (No [0]):\n" + step2_text)
    step2_text = helpers.filter_output(step2_text.strip())
    print(f"tailor_volunteering_and_leadership: step2_text after filtering:\n" + step2_text)
    #Split text into list of individual experiences (each experience starts with [1]Role)
    step3_text = step2_text.split("\n[1]Role: ")[1:]
    step3_text = ["[1]Role: " + exp for exp in step3_text]
    step3_list = []
    for exp in step3_text:
        print(f"tailor_volunteering_and_leadership: step3_volunteering_and_leadership: exp:\n" + exp)
        temp = step3_volunteering_and_leadership(model=model, system2=system2, ollama_url=ollama_url, experience=exp, job_description=job_description_summary)
        print(f"tailor_volunteering_and_leadership: step3_volunteering_and_leadership: temp:\n" + temp)
        temp = helpers.filter_output(temp.strip())
        print(f"tailor_volunteering_and_leadership: step3_volunteering_and_leadership: temp (filtered):\n" + temp)
        step3_list.append(temp)
    step3_text = "\n".join(step3_list)
    print(f"tailor_volunteering_and_leadership: step3_text:\n" + step3_text)
    step4_text = "[0]Volunteering and Leadership:\n" + step3_text
    print(f"tailor_volunteering_and_leadership: step4_text before filtering:\n" + step4_text)
    step4_text = helpers.filter_output(step4_text.strip())
    print(f"tailor_volunteering_and_leadership: step4_text after filtering:\n" + step4_text)
    return step4_text

# Tailor Work Experience
def step0_work_experience(model=DEFAULT_MODEL, system1="", ollama_url=DEFAULT_URL, 
                          raw_cv_data="", job_description=""):
    prompt = f"""
Given the following "Work Experience" resume section:
{raw_cv_data}
And the following job description:
{job_description}
Select up to 4 relevant experiences that best match the job description. If there are 4 or fewer experiences, include all of them. If there are no experiences, return an empty section.
Output the selected experiences strictly in the following format:
[J]Job Title 1
[J]Job Title 2
[J]Job Title 3
[J]Job Title 4
    """
    input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system1,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        response_text = result.get("response", "")
        output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        return response_text
    except Exception:
        print("Ollama response was not valid JSON:")
        print(response.text)
        return "Error: Ollama response was not valid JSON."

def step3_work_experience(model=DEFAULT_MODEL, system2="", ollama_url=DEFAULT_URL, 
                          experience="", job_description=""):
    prompt = f"""
Given the following "Work Experience" resume experience:
{experience}
And the following job description:
{job_description}
Rewrite the experience to best match the job description, following these guidelines:
- Keep all original subsections: Job Title, Company, Location, Duration, Description, and Skills.
- In the Description subsection, rewrite to highlight achievements and relevant skills for the job, using up to 2 sentences (max 20 words each), as a single block of text.
- In the Skills subsection, include up to 6 relevant skills (Programming Languages, Technical Skills, Soft Skills). Every skill category should be present, even if empty.
- Do not use line breaks inside any subsection. Do not use the ":" character in the Description.
- If any subsection is missing, include it as empty.
- Skills must be comma-separated and follow the format below.
Return only the revised section in the following format:
[1]Job Title: Job Title 1
[1]Company: Company Name 1
[1]Location: Location Name 1
[1]Duration: Start Year 1/Start Month 1 - End Year 1/End Month 1
[1]Description: Brief description for Job Title 1.
[1]Skills: Programming Languages: ...; Technical Skills: ...; Soft Skills: ...
    """
    input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system2,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        response_text = result.get("response", "")
        output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        return response_text
    except Exception:
        print("Ollama response was not valid JSON:")
        print(response.text)
        return "Error: Ollama response was not valid JSON."

def tailor_work_experience(model=DEFAULT_MODEL, system1="", system2="", ollama_url=DEFAULT_URL, 
                          raw_cv_data="", job_description_summary="", section="work_experience", reference_dct={}):
    print(f"tailor_work_experience: raw_cv_data:\n" + raw_cv_data)
    step0 = prepare_input_text(raw_cv_data, type=section)
    print(f"tailor_work_experience: step0:\n" + step0)
    step1 = step0_work_experience(model=model, system1=system1, ollama_url=ollama_url, 
                                  raw_cv_data=step0, job_description=job_description_summary)
    print(f"tailor_work_experience: step1:\n" + step1)
    step1_clean = clean_first_step(step1).strip()
    print(f"tailor_work_experience: step1_clean:\n" + step1_clean)
    step2_dct = augment_output(step1_clean, reference_dct, type=section)
    print(f"tailor_work_experience: step2_dct:\n" + str(step2_dct))
    step2_text = helpers.filter_output(parsers.inv_parse_cv(step2_dct))
    print(f"tailor_work_experience: step2_text:\n" + step2_text)
    step3_text = []
    step2_text = step2_text.replace("[0]Work Experience:", "")
    print(f"tailor_work_experience: step2_text (No [0]):\n" + step2_text)
    step2_text = helpers.filter_output(step2_text.strip())
    print(f"tailor_work_experience: step2_text after filtering:\n" + step2_text)
    step3_text = step2_text.split("\n[1]Job Title: ")[1:]
    step3_text = ["[1]Job Title: " + exp for exp in step3_text]
    step3_list = []
    for exp in step3_text:
        print(f"tailor_work_experience: step3_work_experience: exp:\n" + exp)
        temp = step3_work_experience(model=model, system2=system2, ollama_url=ollama_url, experience=exp, job_description=job_description_summary)
        print(f"tailor_work_experience: step3_work_experience: temp:\n" + temp)
        temp = helpers.filter_output(temp.strip())
        print(f"tailor_work_experience: step3_work_experience: temp (filtered):\n" + temp)
        step3_list.append(temp)
    step3_text = "\n".join(step3_list)
    print(f"tailor_work_experience: step3_text:\n" + step3_text)
    step4_text = "[0]Work Experience:\n" + step3_text
    print(f"tailor_work_experience: step4_text before filtering:\n" + step4_text)
    step4_text = helpers.filter_output(step4_text.strip())
    print(f"tailor_work_experience: step4_text after filtering:\n" + step4_text)
    return step4_text
# Tailor Projects
def step0_projects(model=DEFAULT_MODEL, system1="", ollama_url=DEFAULT_URL, 
                   raw_cv_data="", job_description=""):
    prompt = f"""
Given the following "Projects" resume section:
{raw_cv_data}
And the following job description:
{job_description}
Select up to 4 relevant projects that best match the job description. If there are 4 or fewer projects, include all of them. If there are no projects, return an empty section.
Output the selected projects strictly in the following format:
[P]Project Title 1
[P]Project Title 2
[P]Project Title 3
[P]Project Title 4
    """
    input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system1,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        response_text = result.get("response", "")
        output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        return response_text
    except Exception:
        print("Ollama response was not valid JSON:")
        print(response.text)
        return "Error: Ollama response was not valid JSON."

def step3_projects(model=DEFAULT_MODEL, system2="", ollama_url=DEFAULT_URL, 
                   experience="", job_description=""):
    prompt = f"""
Given the following "Projects" resume experience:
{experience}
And the following job description:
{job_description}
Rewrite the project to best match the job description, following these guidelines:
- Keep all original subsections: Project Title, Type, Duration, Description, and Skills.
- In the Description subsection, rewrite to highlight achievements and relevant skills for the job, using up to 2 sentences (max 20 words each), as a single block of text.
- In the Skills subsection, include up to 6 relevant skills (Programming Languages, Technical Skills, Soft Skills). Every skill category should be present, even if empty.
- Do not use line breaks inside any subsection. Do not use the ":" character in the Description.
- If any subsection is missing, include it as empty.
- Skills must be comma-separated and follow the format below.
Return only the revised section in the following format:
[1]Project Title: Project Title 1
[1]Type: Type of Project 1
[1]Duration: Start Year 1/Start Month 1 - End Year 1/End Month 1
[1]Description: Brief description for Project Title 1.
[1]Skills: Programming Languages: ...; Technical Skills: ...; Soft Skills: ...
    """
    input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system2,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        response_text = result.get("response", "")
        output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        return response_text
    except Exception:
        print("Ollama response was not valid JSON:")
        print(response.text)
        return "Error: Ollama response was not valid JSON."

def tailor_projects(model=DEFAULT_MODEL, system1="", system2="", ollama_url=DEFAULT_URL, 
                   raw_cv_data="", job_description_summary="", section="projects", reference_dct={}):
    print(f"tailor_projects: raw_cv_data:\n" + raw_cv_data)
    step0 = prepare_input_text(raw_cv_data, type=section)
    print(f"tailor_projects: step0:\n" + step0)
    step1 = step0_projects(model=model, system1=system1, ollama_url=ollama_url, 
                           raw_cv_data=step0, job_description=job_description_summary)
    print(f"tailor_projects: step1:\n" + step1)
    step1_clean = clean_first_step(step1).strip()
    print(f"tailor_projects: step1_clean:\n" + step1_clean)
    step2_dct = augment_output(step1_clean, reference_dct, type=section)
    print(f"tailor_projects: step2_dct:\n" + str(step2_dct))
    step2_text = helpers.filter_output(parsers.inv_parse_cv(step2_dct))
    print(f"tailor_projects: step2_text:\n" + step2_text)
    step3_text = []
    step2_text = step2_text.replace("[0]Projects:", "")
    print(f"tailor_projects: step2_text (No [0]):\n" + step2_text)
    step2_text = helpers.filter_output(step2_text.strip())
    print(f"tailor_projects: step2_text after filtering:\n" + step2_text)
    step3_text = step2_text.split("\n[1]Project Title: ")[1:]
    step3_text = ["[1]Project Title: " + exp for exp in step3_text]
    step3_list = []
    for exp in step3_text:
        print(f"tailor_projects: step3_projects: exp:\n" + exp)
        temp = step3_projects(model=model, system2=system2, ollama_url=ollama_url, experience=exp, job_description=job_description_summary)
        print(f"tailor_projects: step3_projects: temp:\n" + temp)
        temp = helpers.filter_output(temp.strip())
        print(f"tailor_projects: step3_projects: temp (filtered):\n" + temp)
        step3_list.append(temp)
    step3_text = "\n".join(step3_list)
    print(f"tailor_projects: step3_text:\n" + step3_text)
    step4_text = "[0]Projects:\n" + step3_text
    print(f"tailor_projects: step4_text before filtering:\n" + step4_text)
    step4_text = helpers.filter_output(step4_text.strip())
    print(f"tailor_projects: step4_text after filtering:\n" + step4_text)
    return step4_text
#Prune Experiences
def step0_prune_experiences(model = DEFAULT_MODEL, system1 = "", ollama_url = DEFAULT_URL,
                            experiences = "", job_description = ""):
    
    prompt = f"""
    Given the following experiences across 3 resume sections (Volunteering and Leadership, Work Experience, and Projects):
    {experiences}
    And the following job description:
    {job_description}
    Select 6 experiences based on the job description. When selecting:
    - If the total number of experiences/roles is less than 6, return all of them.
    - If the total number of experiences/roles is greater than or equal to 6 before selection: Select the most relevant 6 experiences/roles based on the job description.
    - If possible, select 1 experience from each section (Volunteering and Leadership, Work Experience, and Projects).
    Return your response strictly in the following format:
    [X]Role/Job Title/Project Title 1
    ...
    [X]Role/Job Title/Project Title 6
    Where [X] indicates the type of experience:
    - [R] Role: Volunteering and Leadership
    - [J] Job Title: Work Experience
    - [P] Project Title: Project
    """
    input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system1,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        response_text = result.get("response", "")
        output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        return response_text
    except Exception:
        print("Ollama response was not valid JSON:")
        print(response.text)
        return "Error: Ollama response was not valid JSON."
def prune_experiences(model=DEFAULT_MODEL, system1="", ollama_url=DEFAULT_URL, 
                   experiences="", job_description_summary="", section="vl_w_p", reference_dct={}):
    print(f"tailor_experiences: experiences:\n" + experiences)
    step0 = prepare_input_text(experiences, type=section)
    print(f"tailor_experiences: step0:\n" + step0)
    step1 = step0_prune_experiences(model=model, system1=system1, ollama_url=ollama_url, 
                           experiences=step0, job_description=job_description_summary)
    print(f"tailor_experiences: step1:\n" + step1)
    step1_clean = clean_first_step(step1).strip()
    print(f"tailor_experiences: step1_clean:\n" + step1_clean)
    step2_dct = augment_output(step1_clean, reference_dct, type=section)
    print(f"tailor_experiences: step2_dct:\n" + str(step2_dct))
    step2_text = helpers.filter_output(parsers.inv_parse_cv(step2_dct))
    print(f"tailor_experiences: step2_text:\n" + step2_text)
    return step2_text

def tailor_summary(model=DEFAULT_MODEL, system="", ollama_url=DEFAULT_URL, cv_data="", job_description="", section="Summary"):
    
    # - Summary (LAST; Based on Job Description AND Overall Resume)
    
    """
    Tailors the summary section based on the job description using Ollama.
    """
    prompt = f"""
    Given the following already tailored resume, with no summary section:
    {cv_data}
    And the following job description:
    {job_description}
    Tailor a '{section}' section for a resume to best match the job description;
    Make sure to mention the most relevant skills and experiences from the CV that match the job description, as well as the amount of languages known.
    Return only the revised section and strictly follow the format:

    [0]Summary: Brief summary of the candidate's qualifications, skills, and experiences relevant to the job description.
    
    The "Summary" section may have up to 150 words.
    Do not line break the summary section, it should be a continuous block of text.
    Do note that the section may not exist in the CV, in which case you should return an empty section. Lastly, I reiterate that you will only return the tailored section, no explanations or additional text.
    """
    input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        response_text = result.get("response", "")
        output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        return response_text
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
        if line.startswith("[1]Skills:"):
            templine = line.replace("[1]Skills:", "").strip()
            if templine != "":
                parts = line.split("; ")
                if "Programming Languages" in line:
                    part0 = parts[0].split(": ")
                    #[1]Skills
                    #Programming Languages
                    #Programming Language N1, ..., Programming Language NN
                    part0_prog = part0[2]
                    part0_prog_splt = part0_prog.split(", ")
                    programming_skills += part0_prog_splt
                else:
                    print("No Programming Languages found in Skills section")
                if "Technical Skills" in line:
                    part1 = parts[1].split(": ")
                    #Technical Skills
                    #Technical Skill N1, ..., Techincal Skill NN
                    part1_tech = part1[1]
                    part1_tech_splt = part1_tech.split(", ")
                    technical_skills += part1_tech_splt
                else:
                    print("No Technical Skills found in Skills section")
                if "Soft Skills" in line:
                    part2 = parts[2].split(": ")
                    #Soft Skills
                    #Soft Skill N1, ..., Soft Skill NN
                    part2_soft = part2[1]
                    part2_soft_splt = part2_soft.split(", ")
                    soft_skills += part2_soft_splt
                else:
                    print("No Soft Skills found in Skills section")
            else:
                print("No Skills subsection found")
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
    input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        response_text = result.get("response", "")
        output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        return response_text
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
    
    input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False
    }
    
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    
    try:
        result = response.json()
        response_text = result.get("response", "")
        output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        return response_text
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
    
    input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False
    }
    
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    
    try:
        result = response.json()
        response_text = result.get("response", "")
        output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        return response_text
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
    
    input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False
    }
    
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    
    try:
        result = response.json()
        response_text = result.get("response", "")
        output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        return response_text
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
