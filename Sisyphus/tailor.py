from pydoc import text
import requests
from Sisyphus import helpers
from Sisyphus import parsers
import logging
from Sisyphus.decorators import log_time
import config
import aiohttp
import asyncio
import warnings
from config import CONFIG
DEFAULT_MODEL = "llama3:8b"
DEFAULT_URL = "http://localhost:11434"

# Set up logging
print = logging.info

@log_time
def compare_start(output, sample_starts = ""):
    # Compare the two outputs and return the differences
    equal = True
    start_lines = sample_starts.splitlines()
    start_lines = [line.strip() for line in start_lines if line.strip()]
    output_lines = output.splitlines()
    output_lines = [line.strip() for line in output_lines if line.strip()]
    if len(start_lines) != len(output_lines):
        # Handle length mismatch
        logging.warning(f"[OUTPUT][FAIL] compare_start: Length mismatch: {len(start_lines)} != {len(output_lines)}")
        equal = False
    else:
        print("[OUTPUT][OK] Output matches expected length")
        
    for i in range(len(start_lines)):
        #Check if output lines starts with start_lines
        if output_lines[i].startswith(start_lines[i]):
            continue
        else:
            equal = False
            logging.warning(f"[OUTPUT][FAIL] compare_start: Output line {i} does not start with sample start line")
            print(f"[OUTPUT][FAIL] compare_start: Output line: {output_lines[i]}")
            print(f"[OUTPUT][FAIL] compare_start: Expected start line: {start_lines[i]}")
    if equal:
        print("[OUTPUT][OK] Output matches expected start lines")
    return equal

@log_time
async def ollama_request(session, payload, ollama_url):
    # Check payload fields
    for field in ["model", "system", "prompt", "stream", "temperature"]:
        value = payload.get(field, None)
        if value is not None:
            logging.info(f"[OLLAMA]ollama_request: payload field {field} with value {value} found")
        else:
            logging.error(f"[ERROR][OLLAMA]ollama_request: payload field {field} is missing or is NoneType")
    async with session.post(f"{ollama_url}/api/generate", json=payload) as resp:
        data = await resp.json()
        if resp.status == 400:
            logging.error(f"[ERROR][OLLAMA]Bad Request: Payload={payload}, Response={data}")
        return data.get("response", "")
    
@log_time
async def parallel_requests(payloads, ollama_url):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(len(payloads)):
            payload = payloads[i].copy()
            # payload["prompt"] = f"Prompt {i+1}"  
            tasks.append(ollama_request(session, payload, ollama_url))
        results = await asyncio.gather(*tasks)
    return results


@log_time
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
    [1]URL: <URL of Project 1>
    [1]Type: <Type of Project 1>
    [1]Duration: <Start Date 1> - <End Date 1>
    [1]Description: <Description 1>
    [1]Project Title: <Project Title 2>
    [1]URL: <URL of Project 2>
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
    [1]URL: <URL of Project 1>
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
                #Check if role field exists in item
                if 'role' in item:
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
                #Check if job_title field exists in item
                if 'job_title' in item:
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
                #Check if project_title field exists in item
                if 'project_title' in item:
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
                #Check if role field exists in item
                if 'role' in item:
                    if line.strip() == item['role']:
                        return_list[0].append(item)
                        reference_list_vl.remove(item)
                        found = True
                        break
            if found:
                continue
            for item in reference_list_w:
                #Check if job_title field exists in item
                if 'job_title' in item:
                    if line.strip() == item['job_title']:
                        return_list[1].append(item)
                        reference_list_w.remove(item)
                        found = True
                        break
            if found:
                continue
            for item in reference_list_p:
                #Check if project_title field exists in item
                if 'project_title' in item:
                    if line.strip() == item['project_title']:
                        return_list[2].append(item)
                        reference_list_p.remove(item)
                        found = True
                        break
        tmp_dict['volunteering_and_leadership'] = return_list[0]
        tmp_dict['work_experience'] = return_list[1]
        tmp_dict['projects'] = return_list[2]
    return tmp_dict

@log_time
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
            if not line.startswith(("[0]Projects:", "[1]URL:", "[1]Type:", "[1]Duration:")):
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
                                    "[0]Projects:", "[1]URL:", "[1]Type:")):
                line = line.replace("[1]Role: ", "[R]").replace("[1]Description: ", "Description: ").replace("[1]Skills: ", "Skills: ").replace("[1]Job Title: ", "[J]").replace("[1]Project Title: ", "[P]").strip()
                if line:
                    return_list.append(line)
        for item in return_list:
            return_text += f"{item}\n"
        return return_text

@log_time
def clean_first_step(text):
    # Remove lines that do not start with [X] where X is a capitalized letter
    cleaned_lines = []
    for line in text.split('\n'):
        if line.startswith(("[R]", "[J]", "[P]")):
            cleaned_lines.append(line)
    return '\n'.join(cleaned_lines)  

#For each main tailor function (including pruning), we need to create 3 functions
#Tailor Volunteering and Leadership
@log_time
def summarize_job_description(job_description = "", system = "", ollama_url=DEFAULT_URL, model=DEFAULT_MODEL):
    # Summarize the job description by extracting key responsibilities and requirements
    # This is a placeholder implementation
    prompt = f"""Summarize the following job description by extracting key responsibilities, requirements, and highlighting needed skills, both technical and soft.
Don't forget to also include the Company Name and the Job Title.
Job Description:
{job_description}
"""
    if config.DEBUG["TOKEN_LOGGING"]: input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False,
        "temperature": CONFIG["MODELS"]["TEMPERATURE"]
    }
    for field in ["model", "system", "prompt", "stream", "temperature"]:
        value = payload.get(field, None)
        if value is not None:
            logging.info(f"[OLLAMA]summarize_job_description: payload field {field} with value {value} found")
        else:
            logging.error(f"[ERROR][OLLAMA]summarize_job_description: payload field {field} is missing or is NoneType")
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        if response.status_code == 400:
            logging.error(f"[ERROR][OLLAMA]Bad Request: Payload={payload}, Response={result}")
        response_text = result.get("response", "")
        if config.DEBUG["TOKEN_LOGGING"]: output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        print(f"[SUCCESS][OLLAMA]summarize_job_description: {result}")
        return response_text
    
    except requests.exceptions.JSONDecodeError as e:
        logging.error("[ERROR][OLLAMA]summarize_job_description: Ollama response was not valid JSON.", exc_info=True)
        logging.error(f"Response text: {response.text}")
        return "[ERROR][OLLAMA]summarize_job_description: Ollama response was not valid JSON."

@log_time
def step0_volunteering_and_leadership(model=DEFAULT_MODEL, system1="", ollama_url=DEFAULT_URL, 
                                       raw_cv_data="", job_description=""):
    prompt = f"""Given the following "Volunteering and Leadership" resume section:
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
"""
    if config.DEBUG["TOKEN_LOGGING"]: input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system1,
        "prompt": prompt,
        "stream": False,
        "temperature": CONFIG["MODELS"]["TEMPERATURE"]
    }
    for field in ["model", "system", "prompt", "stream", "temperature"]:
        value = payload.get(field, None)
        if value is not None:
            logging.info(f"[OLLAMA]step0_volunteering_and_leadership: payload field {field} with value {value} found")
        else:
            logging.error(f"[ERROR][OLLAMA]step0_volunteering_and_leadership: payload field {field} is missing or is NoneType")
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        if response.status_code == 400:
            logging.error(f"[ERROR][OLLAMA]Bad Request: Payload={payload}, Response={result}")
        response_text = result.get("response", "")
        if config.DEBUG["TOKEN_LOGGING"]: output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        print(f"[SUCCESS][OLLAMA]step0_volunteering_and_leadership: {result}")
        return response_text
    except requests.exceptions.JSONDecodeError as e:
        logging.error("[ERROR][OLLAMA]step0_volunteering_and_leadership: Ollama response was not valid JSON.", exc_info=True)
        logging.error(f"Response text: {response.text}")
        return "[ERROR][OLLAMA]step0_volunteering_and_leadership: Ollama response was not valid JSON."

@log_time
def step3_volunteering_and_leadership(model=DEFAULT_MODEL, system2="", ollama_url=DEFAULT_URL, 
                                       experience="", job_description=""):
    prompt = f"""Given the "Description" and "Skills" subsections of a role belonging to the "Volunteering and Leadership" section of a resume:
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
"""
    if config.DEBUG["TOKEN_LOGGING"]: input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system2,
        "prompt": prompt,
        "stream": False,
        "temperature": CONFIG["MODELS"]["TEMPERATURE"]
    }
    for field in ["model", "system", "prompt", "stream", "temperature"]:
        value = payload.get(field, None)
        if value is not None:
            logging.info(f"[OLLAMA]step3_volunteering_and_leadership: payload field {field} with value {value} found")
        else:
            logging.error(f"[ERROR][OLLAMA]step3_volunteering_and_leadership: payload field {field} is missing or is NoneType")
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        
        if response.status_code == 400:
            logging.error(f"[ERROR][OLLAMA]Bad Request: Payload={payload}, Response={result}")
        response_text = result.get("response", "")
        if config.DEBUG["TOKEN_LOGGING"]: output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        print(f"[SUCCESS][OLLAMA]step3_volunteering_and_leadership: {result}")
        return response_text
    except requests.exceptions.JSONDecodeError as e:
        logging.error("[ERROR][OLLAMA]step3_volunteering_and_leadership: Ollama response was not valid JSON.", exc_info=True)
        logging.error(f"Response text: {response.text}")
        return "[ERROR][OLLAMA]step3_volunteering_and_leadership: Ollama response was not valid JSON."

@log_time
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
    step3_text = step2_text.split("[1]Role: ")[1:]
    step3_text = ["[1]Role: " + exp for exp in step3_text]
    step3_list = []
    for exp in step3_text:
        print(f"tailor_volunteering_and_leadership: step3_volunteering_and_leadership: exp:\n" + exp)
        #Transform to dict
        exp_dict = parsers.parse_subfields(helpers.filter_output(exp).strip())
        #Separate dict in two: one containing description and skills, the other containing the rest
        first_part_dict = {k: v for k, v in exp_dict.items() if k in ["description", "skills"]}
        second_part_dict = {k: v for k, v in exp_dict.items() if k not in ["description", "skills"]}
        #Convert to text
        first_part_text = parsers.inv_parse_subfields(first_part_dict).strip()
        second_part_text = parsers.inv_parse_subfields(second_part_dict).strip()
        print(f"tailor_volunteering_and_leadership: step3_volunteering_and_leadership: second_part_text:\n" + second_part_text)
        first_part_text_new = step3_volunteering_and_leadership(model=model, system2=system2, ollama_url=ollama_url, experience=first_part_text, job_description=job_description_summary)
        print(f"tailor_volunteering_and_leadership: step3_volunteering_and_leadership: first_part_text_new:\n" + first_part_text_new)
        first_part_text_new = helpers.filter_output(first_part_text_new.strip())
        print(f"tailor_volunteering_and_leadership: step3_volunteering_and_leadership: first_part_text_new (filtered):\n" + first_part_text_new)
        #Join with second part
        temp = second_part_text + "\n" + first_part_text_new
        print(f"tailor_volunteering_and_leadership: step3_volunteering_and_leadership: temp:\n" + temp)
        step3_list.append(temp)
    step3_text = "\n".join(step3_list)
    print(f"tailor_volunteering_and_leadership: step3_text:\n" + step3_text)
    step4_text = "[0]Volunteering and Leadership:\n" + step3_text
    print(f"tailor_volunteering_and_leadership: step4_text before filtering:\n" + step4_text)
    step4_text = helpers.filter_output(step4_text.strip())
    print(f"tailor_volunteering_and_leadership: step4_text after filtering:\n" + step4_text)
    return step4_text

# Tailor Work Experience
@log_time
def step0_work_experience(model=DEFAULT_MODEL, system1="", ollama_url=DEFAULT_URL, 
                          raw_cv_data="", job_description=""):
    prompt = f"""Given the following "Work Experience" resume section:
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
"""
    if config.DEBUG["TOKEN_LOGGING"]: input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system1,
        "prompt": prompt,
        "stream": False,
        "temperature": CONFIG["MODELS"]["TEMPERATURE"]
    }
    for field in ["model", "system", "prompt", "stream", "temperature"]:
        value = payload.get(field, None)
        if value is not None:
            logging.info(f"[OLLAMA]step0_work_experience: payload field {field} with value {value} found")
        else:
            logging.error(f"[ERROR][OLLAMA]step0_work_experience: payload field {field} is missing or is NoneType")
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        
        if response.status_code == 400:
            logging.error(f"[ERROR][OLLAMA]Bad Request: Payload={payload}, Response={result}")
        response_text = result.get("response", "")
        if config.DEBUG["TOKEN_LOGGING"]: output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        print(f"[SUCCESS][OLLAMA]step0_work_experience: {result}")
        return response_text
    except requests.exceptions.JSONDecodeError as e:
        logging.error("[ERROR][OLLAMA]step0_work_experience: Ollama response was not valid JSON.", exc_info=True)
        logging.error(f"Response text: {response.text}")
        return "[ERROR][OLLAMA]step0_work_experience: Ollama response was not valid JSON."

@log_time
def step3_work_experience(model=DEFAULT_MODEL, system2="", ollama_url=DEFAULT_URL, 
                          experience="", job_description=""):
    prompt = f"""Given the "Description" and "Skills" subsections of a role belonging to the "Work Experience" section of a resume:
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
"""
    if config.DEBUG["TOKEN_LOGGING"]: input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system2,
        "prompt": prompt,
        "stream": False,
        "temperature": CONFIG["MODELS"]["TEMPERATURE"]
    }
    for field in ["model", "system", "prompt", "stream", "temperature"]:
        value = payload.get(field, None)
        if value is not None:
            logging.info(f"[OLLAMA]step3_work_experience: payload field {field} with value {value} found")
        else:
            logging.error(f"[ERROR][OLLAMA]step3_work_experience: payload field {field} is missing or is NoneType")
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        
        if response.status_code == 400:
            logging.error(f"[ERROR][OLLAMA]Bad Request: Payload={payload}, Response={result}")
        response_text = result.get("response", "")
        if config.DEBUG["TOKEN_LOGGING"]: output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        print(f"[SUCCESS][OLLAMA]step3_work_experience: {result}")
        return response_text
    except requests.exceptions.JSONDecodeError as e:
        logging.error("[ERROR][OLLAMA]step3_work_experience: Ollama response was not valid JSON.", exc_info=True)
        logging.error(f"Response text: {response.text}")
        return "[ERROR][OLLAMA]step3_work_experience: Ollama response was not valid JSON."

@log_time
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
    step3_text = step2_text.split("[1]Job Title: ")[1:]
    step3_text = ["[1]Job Title: " + exp for exp in step3_text]
    step3_list = []
    for exp in step3_text:
        print(f"tailor_work_experience: step3_work_experience: exp:\n" + exp)
        #Transform to dict
        exp_dict = parsers.parse_subfields(helpers.filter_output(exp).strip())
        #Separate dict in two: one containing description and skills, the other containing the rest
        first_part_dict = {k: v for k, v in exp_dict.items() if k in ["description", "skills"]}
        second_part_dict = {k: v for k, v in exp_dict.items() if k not in ["description", "skills"]}
        #Convert to text
        first_part_text = parsers.inv_parse_subfields(first_part_dict).strip()
        second_part_text = parsers.inv_parse_subfields(second_part_dict).strip()
        first_part_text_new = step3_work_experience(model=model, system2=system2, ollama_url=ollama_url, experience=first_part_text, job_description=job_description_summary)
        print(f"tailor_work_experience: step3_work_experience: first_part_text_new:\n" + first_part_text_new)
        first_part_text_new = helpers.filter_output(first_part_text_new.strip())
        print(f"tailor_work_experience: step3_work_experience: first_part_text_new (filtered):\n" + first_part_text_new)
        #Join with second part
        temp = second_part_text + "\n" + first_part_text_new
        print(f"tailor_work_experience: step3_work_experience: temp:\n" + temp)
        step3_list.append(temp)
    step3_text = "\n".join(step3_list)
    print(f"tailor_work_experience: step3_text:\n" + step3_text)
    step4_text = "[0]Work Experience:\n" + step3_text
    print(f"tailor_work_experience: step4_text before filtering:\n" + step4_text)
    step4_text = helpers.filter_output(step4_text.strip())
    print(f"tailor_work_experience: step4_text after filtering:\n" + step4_text)
    return step4_text
# Tailor Projects
@log_time
def step0_projects(model=DEFAULT_MODEL, system1="", ollama_url=DEFAULT_URL, 
                   raw_cv_data="", job_description=""):
    prompt = f"""Given the following "Projects" resume section:
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
"""
    if config.DEBUG["TOKEN_LOGGING"]: input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system1,
        "prompt": prompt,
        "stream": False,
        "temperature": CONFIG["MODELS"]["TEMPERATURE"]
    }
    for field in ["model", "system", "prompt", "stream", "temperature"]:
        value = payload.get(field, None)
        if value is not None:
            logging.info(f"[OLLAMA]step0_projects: payload field {field} with value {value} found")
        else:
            logging.error(f"[ERROR][OLLAMA]step0_projects: payload field {field} is missing or is NoneType")
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        
        if response.status_code == 400:
            logging.error(f"[ERROR][OLLAMA]Bad Request: Payload={payload}, Response={result}")
        response_text = result.get("response", "")
        if config.DEBUG["TOKEN_LOGGING"]: output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        print(f"[SUCCESS][OLLAMA]step0_projects: {result}")
        return response_text
    except requests.exceptions.JSONDecodeError as e:
        logging.error("[ERROR][OLLAMA]step0_projects: Ollama response was not valid JSON.", exc_info=True)
        logging.error(f"Response text: {response.text}")
        return "[ERROR][OLLAMA]step0_projects: Ollama response was not valid JSON."

@log_time
def step3_projects(model=DEFAULT_MODEL, system2="", ollama_url=DEFAULT_URL, 
                   experience="", job_description=""):
    prompt = f"""Given the "Description" and "Skills" subsections of a project belonging to the "Projects" section of a resume:
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
"""
    if config.DEBUG["TOKEN_LOGGING"]: input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system2,
        "prompt": prompt,
        "stream": False,
        "temperature": CONFIG["MODELS"]["TEMPERATURE"]
    }
    for field in ["model", "system", "prompt", "stream", "temperature"]:
        value = payload.get(field, None)
        if value is not None:
            logging.info(f"[OLLAMA]step3_projects: payload field {field} with value {value} found")
        else:
            logging.error(f"[ERROR][OLLAMA]step3_projects: payload field {field} is missing or is NoneType")
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        
        if response.status_code == 400:
            logging.error(f"[ERROR][OLLAMA]Bad Request: Payload={payload}, Response={result}")
        response_text = result.get("response", "")
        if config.DEBUG["TOKEN_LOGGING"]: output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        print(f"[SUCCESS][OLLAMA]step3_projects: {result}")
        return response_text
    except requests.exceptions.JSONDecodeError as e:
        logging.error("[ERROR][OLLAMA]step3_projects: Ollama response was not valid JSON.", exc_info=True)
        logging.error(f"Response text: {response.text}")
        return "[ERROR][OLLAMA]step3_projects: Ollama response was not valid JSON."

@log_time
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
    step3_text = step2_text.split("[1]Project Title: ")[1:]
    step3_text = ["[1]Project Title: " + exp for exp in step3_text]
    step3_list = []
    for exp in step3_text:
        print(f"tailor_projects: step3_projects: exp:\n" + exp)
        #Transform to dict
        exp_dict = parsers.parse_subfields(helpers.filter_output(exp).strip())
        #Separate dict in two: one containing description and skills, the other containing the rest
        first_part_dict = {k: v for k, v in exp_dict.items() if k in ["description", "skills"]}
        second_part_dict = {k: v for k, v in exp_dict.items() if k not in ["description", "skills"]}
        #Convert to text
        first_part_text = parsers.inv_parse_subfields(first_part_dict).strip()
        second_part_text = parsers.inv_parse_subfields(second_part_dict).strip()
        first_part_text_new = step3_projects(model=model, system2=system2, ollama_url=ollama_url, experience=first_part_text, job_description=job_description_summary)
        print(f"tailor_projects: step3_projects: first_part_text_new:\n" + first_part_text_new)
        first_part_text_new = helpers.filter_output(first_part_text_new.strip())
        print(f"tailor_projects: step3_projects: first_part_text_new (filtered):\n" + first_part_text_new)
        #Join with second part
        temp = second_part_text + "\n" + first_part_text_new
        print(f"tailor_projects: step3_projects: temp:\n" + temp)
        step3_list.append(temp)
    step3_text = "\n".join(step3_list)
    print(f"tailor_projects: step3_text:\n" + step3_text)
    step4_text = "[0]Projects:\n" + step3_text
    print(f"tailor_projects: step4_text before filtering:\n" + step4_text)
    step4_text = helpers.filter_output(step4_text.strip())
    print(f"tailor_projects: step4_text after filtering:\n" + step4_text)
    return step4_text
#Prune Experiences

@log_time
def step0_prune_experiences(model = DEFAULT_MODEL, system1 = "", ollama_url = DEFAULT_URL,
                            experiences = "", job_description = ""):
    
    #   - If possible, select 1 experience from each section (Volunteering and Leadership, Work Experience, and Projects).
    prompt = f"""Given the following experiences across 3 resume sections (Volunteering and Leadership, Work Experience, and Projects):
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
- [R] Role: Volunteering and Leadership
- [J] Job Title: Work Experience
- [P] Project Title: Project
"""
    if config.DEBUG["TOKEN_LOGGING"]: input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system1,
        "prompt": prompt,
        "stream": False,
        "temperature": CONFIG["MODELS"]["TEMPERATURE"]
    }
    for field in ["model", "system", "prompt", "stream", "temperature"]:
        value = payload.get(field, None)
        if value is not None:
            logging.info(f"[OLLAMA]step0_prune_experiences: payload field {field} with value {value} found")
        else:
            logging.error(f"[ERROR][OLLAMA]step0_prune_experiences: payload field {field} is missing or is NoneType")
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        
        if response.status_code == 400:
            logging.error(f"[ERROR][OLLAMA]Bad Request: Payload={payload}, Response={result}")
        response_text = result.get("response", "")
        if config.DEBUG["TOKEN_LOGGING"]: output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        print(f"[SUCCESS][OLLAMA]step0_prune_experiences: {result}")
        return response_text
    except requests.exceptions.JSONDecodeError as e:
        logging.error("[ERROR][OLLAMA]step0_prune_experiences: Ollama response was not valid JSON.", exc_info=True)
        logging.error(f"Response text: {response.text}")
        return "[ERROR][OLLAMA]step0_prune_experiences: Ollama response was not valid JSON."

@log_time
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

#Longer input tailoring functions
#Sliding Window + Hierarchical solution
#Tailor Summary
@log_time
def generate_payloads_summarize_section(sections, section_names, systems, model=DEFAULT_MODEL, ollama_url=DEFAULT_URL):
    payloads = []
    requests = len(sections)
    for i in range(requests):
        prompt = f"""Given the following section from a resume:
{sections[i]}
Summarize the sections in a wholistic manner while following these guidelines:
- Be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
- Include all information, competencies, achievements, and skills, this is a wholistic summary of the candidate's qualifications.
Return the summarized information as a single continuous string of text, following this format strictly:
[S]{section_names[i]} Section Summary: Wholistic summary of the section's information.
"""
        if config.DEBUG["TOKEN_LOGGING"]: input_tks = helpers.token_math(model, prompt)
        payload = {
            "model": model,
            "system": systems[i],
            "prompt": prompt,
            "stream": False,
            "temperature": CONFIG["MODELS"]["TEMPERATURE"]
        }
        for field in ["model", "system", "prompt", "stream", "temperature"]:
            value = payload.get(field, None)
            if value is not None:
                logging.info(f"[OLLAMA]generate_payloads_summarize_section: payload field {field} with value {value} found")
            else:
                logging.error(f"[ERROR][OLLAMA]generate_payloads_summarize_section: payload field {field} is missing or is NoneType")
        payloads.append(payload)
    return payloads

@log_time
def summarize_section(section="", model = DEFAULT_MODEL, system = "", ollama_url = DEFAULT_URL, section_name = ""):
    # Implement the logic to summarize the section based on the job description
    prompt = f"""Given the following section from a resume:
{section}
Summarize the sections in a wholistic manner while following these guidelines:
- Be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
- Include all information, competencies, achievements, and skills, this is a wholistic summary of the candidate's qualifications.
Return the summarized information as a single continuous string of text, following this format strictly:
[S]{section_name} Section Summary: Wholistic summary of the section's information.
"""
    if config.DEBUG["TOKEN_LOGGING"]: input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False,
        "temperature": CONFIG["MODELS"]["TEMPERATURE"]
    }
    for field in ["model", "system", "prompt", "stream", "temperature"]:
        value = payload.get(field, None)
        if value is not None:
            logging.info(f"[OLLAMA]summarize_section: payload field {field} with value {value} found")
        else:
            logging.error(f"[ERROR][OLLAMA]summarize_section: payload field {field} is missing or is NoneType")
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        
        if response.status_code == 400:
            logging.error(f"[ERROR][OLLAMA]Bad Request: Payload={payload}, Response={result}")
        response_text = result.get("response", "")
        if config.DEBUG["TOKEN_LOGGING"]: output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        print(f"[SUCCESS][OLLAMA]summarize_section: {result}")
        return response_text
    except requests.exceptions.JSONDecodeError as e:
        logging.error("[ERROR][OLLAMA]summarize_section: Ollama response was not valid JSON.", exc_info=True)
        logging.error(f"Response text: {response.text}")
        return "[ERROR][OLLAMA]summarize_section: Ollama response was not valid JSON."

@log_time
def batch_summarize_sections(sections = [], section_names = [], model=DEFAULT_MODEL, system="", ollama_url=DEFAULT_URL):
    # Implement the logic to summarize the section based on the job description
    sections_text = "\n".join(sections)
    prompt = f"""Given the following sections from a resume:
{sections_text}
Summarize the sections in a wholistic manner while following these guidelines:
- Be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
- Include all information, competencies, achievements, and skills, this is a wholistic summary of the candidate's qualifications.
- Keep in mind that these summaries will be used in a "Sliding Window" approach to summarize the entire resume effectively, so include information that is relevant for the overall context of the resume.
Return the summarized information as a single continuous string of text, following this format strictly:
"""
    for name in section_names:
        prompt += f"[S]{name} Section Summary: Wholistic summary of the section's information.\n"
    if config.DEBUG["TOKEN_LOGGING"]: input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False,
        "temperature": CONFIG["MODELS"]["TEMPERATURE"]
    }
    for field in ["model", "system", "prompt", "stream", "temperature"]:
        value = payload.get(field, None)
        if value is not None:
            logging.info(f"[OLLAMA]batch_summarize_section: payload field {field} with value {value} found")
        else:
            logging.error(f"[ERROR][OLLAMA]batch_summarize_section: payload field {field} is missing or is NoneType")
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        
        if response.status_code == 400:
            logging.error(f"[ERROR][OLLAMA]Bad Request: Payload={payload}, Response={result}")
        response_text = result.get("response", "")
        if config.DEBUG["TOKEN_LOGGING"]: output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        print(f"[SUCCESS][OLLAMA]batch_summarize_section: {result}")
        return response_text
    except requests.exceptions.JSONDecodeError as e:
        logging.error("[ERROR][OLLAMA]batch_summarize_section: Ollama response was not valid JSON.", exc_info=True)
        logging.error(f"Response text: {response.text}")
        return "[ERROR][OLLAMA]batch_summarize_section: Ollama response was not valid JSON."


@log_time
def summarize_general_info(general_info_text = "", model = DEFAULT_MODEL, system = "", ollama_url = DEFAULT_URL):
    prompt = f"""Given the following general information from a resume:
{general_info_text}
Summarize the general information section of a resume in a wholistic manner; be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
Since this is a summary of a resume's general information, you need to include the candidate's Name, Contact Information, Title, and Languages Spoken.
Return the summarized general information as follows:
[S]General Information Summary: Brief and concise summary of the resume's general information, presented as a single continuous string of text.
"""
    if config.DEBUG["TOKEN_LOGGING"]: input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False,
        "temperature": CONFIG["MODELS"]["TEMPERATURE"]
    }
    for field in ["model", "system", "prompt", "stream", "temperature"]:
        value = payload.get(field, None)
        if value is not None:
            logging.info(f"[OLLAMA]summarize_general_info: payload field {field} with value {value} found")
        else:
            logging.error(f"[ERROR][OLLAMA]summarize_general_info: payload field {field} is missing or is NoneType")
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        
        if response.status_code == 400:
            logging.error(f"[ERROR][OLLAMA]Bad Request: Payload={payload}, Response={result}")
        response_text = result.get("response", "")
        if config.DEBUG["TOKEN_LOGGING"]: output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        print(f"[SUCCESS][OLLAMA]summarize_general_info: {result}")
        return helpers.filter_output(response_text.strip(), mode= "cap_letters")
    except requests.exceptions.JSONDecodeError as e:
        logging.error("[ERROR][OLLAMA]summarize_general_info: Ollama response was not valid JSON.", exc_info=True)
        logging.error(f"Response text: {response.text}")
        return "[ERROR][OLLAMA]summarize_general_info: Ollama response was not valid JSON."

@log_time
def summarize_skills( model=DEFAULT_MODEL, system="", ollama_url=DEFAULT_URL, skill_section=""):
    prompt = f"""Given the following skills information from a resume:
{skill_section}
Summarize the skills section of a resume in a wholistic manner; be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
Return the summarized skills information as follows:
[S]Skills Summary: Brief and concise wholistic summary of the resume's skills, presented as a single continuous string of text.
"""
    if config.DEBUG["TOKEN_LOGGING"]: input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False,
        "temperature": CONFIG["MODELS"]["TEMPERATURE"]
    }
    for field in ["model", "system", "prompt", "stream", "temperature"]:
        value = payload.get(field, None)
        if value is not None:
            logging.info(f"[OLLAMA]summarize_skills: payload field {field} with value {value} found")
        else:
            logging.error(f"[ERROR][OLLAMA]summarize_skills: payload field {field} is missing or is NoneType")
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        
        if response.status_code == 400:
            logging.error(f"[ERROR][OLLAMA]Bad Request: Payload={payload}, Response={result}")
        response_text = result.get("response", "")
        if config.DEBUG["TOKEN_LOGGING"]: output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        print(f"[SUCCESS][OLLAMA]summarize_skills: {result}")
        return helpers.filter_output(response_text.strip(), mode= "cap_letters")
    except requests.exceptions.JSONDecodeError as e:
        logging.error("[ERROR][OLLAMA]summarize_skills: Ollama response was not valid JSON.", exc_info=True)
        logging.error(f"Response text: {response.text}")
        return "[ERROR][OLLAMA]summarize_skills: Ollama response was not valid JSON."

@log_time
def sliding_window_two_sections(section1 = "", section2 ="", model=DEFAULT_MODEL, system1="", system2="", system = "", ollama_url=DEFAULT_URL,
                                section1_name = "", section2_name = "", candidate_name = "", candidate_title = "", mode = "single"):
    if CONFIG["SUMMARY_REQUESTS"] > 2:
        warnings.warn("[WARNING]sliding_window_two_sections: number of requests exceeds sliding window size, using maximum possible request number (2)")
    if CONFIG["SUMMARY_REQUESTS"] < 0:
        raise ValueError("[ERROR]sliding_window_two_sections: SUMMARY_REQUESTS must be a positive integer")
    sections = [section1, section2]
    section_names = [section1_name, section2_name]
    systems = [system1, system2]
    summaries = []
    if mode == "single":
        for i in range(0, 2):
                summary = summarize_section(sections[i], model=model, system=systems[i], ollama_url=ollama_url, section_name=section_names[i])
                summaries.append(helpers.filter_output(summary.strip(), mode= "cap_letters"))
    elif mode == "batch":
        summaries_raw = batch_summarize_sections(sections=sections, section_names=section_names, model=model, system=system1, ollama_url=ollama_url)
        summaries = helpers.filter_output(summaries_raw.strip(), mode= "cap_letters").split("\n")
    elif mode == "parallel":
        payloads = generate_payloads_summarize_section(sections=[section1, section2], section_names=[section1_name, section2_name], systems=[system1, system2], model=model, ollama_url=ollama_url)
        responses = asyncio.run(parallel_requests(payloads, ollama_url=ollama_url))
        summaries = [helpers.filter_output(response.strip(), mode="cap_letters") for response in responses]
    summary1 = summaries[0] if len(summaries) > 0 else ""
    summary2 = summaries[1] if len(summaries) > 1 else ""
    prompt = f"""Given the following resume section summaries:
{summary1}
{summary2}
Create a new summary that incorporates all two summaries, following these guidelines:
- Be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
- Include all information, competencies, achievements, and skills, this is a wholistic summary of the candidate's qualifications.
- Maintain the context and flow between the two sections.
- When referring to the candidate, use their name: {candidate_name} or their title: {candidate_title}
Return the summarized information as a single continuous string of text, following this format strictly:
[S]{section1_name} + {section2_name} Sections Summary: Wholistic summary of the sections' information, competencies, achievements, and key skills.
"""
    if config.DEBUG["TOKEN_LOGGING"]: input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False,
        "temperature": CONFIG["MODELS"]["TEMPERATURE"]
    }
    for field in ["model", "system", "prompt", "stream", "temperature"]:
        value = payload.get(field, None)
        if value is not None:
            logging.info(f"[OLLAMA]sliding_window_two_sections: payload field {field} with value {value} found")
        else:
            logging.error(f"[ERROR][OLLAMA]sliding_window_two_sections: payload field {field} is missing or is NoneType")
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        
        if response.status_code == 400:
            logging.error(f"[ERROR][OLLAMA]Bad Request: Payload={payload}, Response={result}")
        response_text = result.get("response", "")
        if config.DEBUG["TOKEN_LOGGING"]: output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        response_text = helpers.filter_output(response_text.strip(), mode= "cap_letters")
        print(f"[SUCCESS][OLLAMA]sliding_window_two_sections: {result}")
        return response_text
    except requests.exceptions.JSONDecodeError as e:
        logging.error("[ERROR][OLLAMA]sliding_window_two_sections: Ollama response was not valid JSON.", exc_info=True)
        logging.error(f"Response text: {response.text}")
        return "[ERROR][OLLAMA]sliding_window_two_sections: Ollama response was not valid JSON."

@log_time
def sliding_window_three_sections(section1 = "", section2 = "", section3 = "", model=DEFAULT_MODEL, system1="", system2="", system3="", system = "", ollama_url=DEFAULT_URL,
                                section1_name = "", section2_name = "", section3_name = "", candidate_name = "", candidate_title = "", mode = "single"):
    if CONFIG["SUMMARY_REQUESTS"] > 3:
        warnings.warn("[WARNING]sliding_window_three_sections: number of requests exceeds sliding window size, using maximum possible request number (3)")
    if CONFIG["SUMMARY_REQUESTS"] < 0:
        raise ValueError("[ERROR]sliding_window_three_sections: SUMMARY_REQUESTS must be a positive integer")
    sections = [section1, section2, section3]
    section_names = [section1_name, section2_name, section3_name]
    systems = [system1, system2, system3]
    summaries = []

    for i in range(0, 3, CONFIG["SUMMARY_REQUESTS"]):
        if mode == "single":
            for j in range(0,CONFIG["SUMMARY_REQUESTS"]):
                if i+j >= 3:
                    break
                else:
                    summary = summarize_section(sections[i+j], model=model, system=systems[i+j], ollama_url=ollama_url, section_name=section_names[i+j])
                    summaries.append(helpers.filter_output(summary.strip(), mode= "cap_letters"))
        if mode == "batch":
            upper_bound = i + CONFIG["SUMMARY_REQUESTS"]
            if upper_bound > 3:
                upper_bound = 3
            summary = batch_summarize_sections(sections=sections[i:upper_bound], section_names=section_names[i:upper_bound], model=model, system=system1, ollama_url=ollama_url)
            summaries.append(helpers.filter_output(summary.strip(), mode= "cap_letters"))
            if upper_bound == 3:
                break
        if mode == "parallel":
            upper_bound = i + CONFIG["SUMMARY_REQUESTS"]
            if upper_bound > 3:
                upper_bound = 3
            payloads = generate_payloads_summarize_section(sections=sections[i:upper_bound], section_names=section_names[i:upper_bound], systems=systems[i:upper_bound], model=model, ollama_url=ollama_url)
            responses = asyncio.run(parallel_requests(payloads, ollama_url=ollama_url))
            for response in responses:
                summaries.append(helpers.filter_output(response.strip(), mode= "cap_letters"))
            if upper_bound == 3:
                break

    summary1 = summaries[0] if len(summaries) > 0 else ""
    summary2 = summaries[1] if len(summaries) > 1 else ""
    summary3 = summaries[2] if len(summaries) > 2 else ""

    prompt = f"""Given the following resume section summaries:
{summary1}
{summary2}
{summary3}
Create a new summary that incorporates all three summaries, following these guidelines:
- Be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
- Include all information, competencies, achievements, and skills, this is a wholistic summary of the candidate's qualifications.
- Maintain the context and flow between the three sections.
- When referring to the candidate, use their name: {candidate_name} or their title: {candidate_title}
Return the summarized information as a single continuous string of text, following this format strictly:
[S]{section1_name} + {section2_name} + {section3_name} Sections Summary: Wholistic summary of the sections' information, competencies, achievements, and key skills.
"""
    if config.DEBUG["TOKEN_LOGGING"]: input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False,
        "temperature": CONFIG["MODELS"]["TEMPERATURE"]
    }
    for field in ["model", "system", "prompt", "stream", "temperature"]:
        value = payload.get(field, None)
        if value is not None:
            logging.info(f"[OLLAMA]sliding_window_three_sections: payload field {field} with value {value} found")
        else:
            logging.error(f"[ERROR][OLLAMA]sliding_window_three_sections: payload field {field} is missing or is NoneType")
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        
        if response.status_code == 400:
            logging.error(f"[ERROR][OLLAMA]Bad Request: Payload={payload}, Response={result}")
        response_text = result.get("response", "")
        if config.DEBUG["TOKEN_LOGGING"]: output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        response_text = helpers.filter_output(response_text.strip(), mode= "cap_letters")
        print(f"[SUCCESS][OLLAMA]sliding_window_three_sections: {result}")
        return response_text
    except requests.exceptions.JSONDecodeError as e:
        logging.error("[ERROR][OLLAMA]sliding_window_three_sections: Ollama response was not valid JSON.", exc_info=True)
        logging.error(f"Response text: {response.text}")
        return "[ERROR][OLLAMA]sliding_window_three_sections: Ollama response was not valid JSON."

@log_time
def sliding_window_four_sections(
    section1="",
    section2="",
    section3="",
    section4="",
    model=DEFAULT_MODEL,
    system1="",
    system2="",
    system3="",
    system4="",
    system="",
    ollama_url=DEFAULT_URL,
    section1_name="",
    section2_name="",
    section3_name="",
    section4_name="",
    candidate_name="",
    candidate_title="",
    mode="single"
):
    if CONFIG["SUMMARY_REQUESTS"] > 4:
        warnings.warn("[WARNING]sliding_window_four_sections: number of requests exceeds sliding window size, using maximum possible request number (4)")
    if CONFIG["SUMMARY_REQUESTS"] < 0:
        raise ValueError("[ERROR]sliding_window_four_sections: SUMMARY_REQUESTS must be a positive integer")
    sections = [section1, section2, section3, section4]
    section_names = [section1_name, section2_name, section3_name, section4_name]
    systems = [system1, system2, system3, system4]
    summaries = []

    for i in range(0, 4, CONFIG["SUMMARY_REQUESTS"]):
        if mode == "single":
            for j in range(0,CONFIG["SUMMARY_REQUESTS"]):
                if i+j >= 4:
                    break
                else:
                    summary = summarize_section(sections[i+j], model=model, system=systems[i+j], ollama_url=ollama_url, section_name=section_names[i+j])
                    summaries.append(helpers.filter_output(summary.strip(), mode= "cap_letters"))
        if mode == "batch":
            upper_bound = i + CONFIG["SUMMARY_REQUESTS"]
            if upper_bound > 4:
                upper_bound = 4
            summary = batch_summarize_sections(sections=sections[i:upper_bound], section_names=section_names[i:upper_bound], model=model, system=system1, ollama_url=ollama_url)
            summaries.append(helpers.filter_output(summary.strip(), mode= "cap_letters"))
            if upper_bound == 4:
                break
        if mode == "parallel":
            upper_bound = i + CONFIG["SUMMARY_REQUESTS"]
            if upper_bound > 4:
                upper_bound = 4
            payloads = generate_payloads_summarize_section(sections=sections[i:upper_bound], section_names=section_names[i:upper_bound], systems=systems[i:upper_bound], model=model, ollama_url=ollama_url)
            responses = asyncio.run(parallel_requests(payloads, ollama_url=ollama_url))
            for response in responses:
                summaries.append(helpers.filter_output(response.strip(), mode= "cap_letters"))
            if upper_bound == 4:
                break

    summary1 = summaries[0] if len(summaries) > 0 else ""
    summary2 = summaries[1] if len(summaries) > 1 else ""
    summary3 = summaries[2] if len(summaries) > 2 else ""
    summary4 = summaries[3] if len(summaries) > 3 else ""
    prompt = f"""Given the following resume section summaries:
{summary1}
{summary2}
{summary3}
{summary4}
Create a new summary that incorporates all four summaries, following these guidelines:
- Be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
- Include all information, competencies, achievements, and skills, this is a wholistic summary of the candidate's qualifications.
- Maintain the context and flow between the four sections.
- When referring to the candidate, use their name: {candidate_name} or their title: {candidate_title}
Return the summarized information as a single continuous string of text, following this format strictly:
[S]{section1_name} + {section2_name} + {section3_name} + {section4_name} Sections Summary: Wholistic summary of the sections' information, competencies, achievements, and key skills.
"""
    if config.DEBUG["TOKEN_LOGGING"]:
        input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False,
        "temperature": CONFIG["MODELS"]["TEMPERATURE"]
    }
    for field in ["model", "system", "prompt", "stream", "temperature"]:
        value = payload.get(field, None)
        if value is not None:
            logging.info(f"[OLLAMA]sliding_window_four_sections: payload field {field} with value {value} found")
        else:
            logging.error(f"[ERROR][OLLAMA]sliding_window_four_sections: payload field {field} is missing or is NoneType")
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        
        if response.status_code == 400:
            logging.error(f"[ERROR][OLLAMA]Bad Request: Payload={payload}, Response={result}")
        response_text = result.get("response", "")
        if config.DEBUG["TOKEN_LOGGING"]:
            output_tks = helpers.token_math(model, response_text, type="output", offset=input_tks)
        response_text = helpers.filter_output(response_text.strip(), mode="cap_letters")
        print(f"[SUCCESS][OLLAMA]sliding_window_four_sections: {result}")
        return response_text
    except requests.exceptions.JSONDecodeError as e:
        logging.error("[ERROR][OLLAMA]sliding_window_four_sections: Ollama response was not valid JSON.", exc_info=True)
        logging.error(f"Response text: {response.text}")
        return "[ERROR][OLLAMA]sliding_window_four_sections: Ollama response was not valid JSON."


@log_time
def slide_summary(
    sections_dct_list=[],
    model=DEFAULT_MODEL,
    system_s="",
    system="",
    system1="",
    system2="",
    system3="",
    system4="",
    ollama_url=DEFAULT_URL,
    windows=2,
    skill_section=False,
    mode="single"
):
    general_keys = ['name', 'contact_information', 'title', 'languages']
    special_keys = [
        'education',
        'certifications',
        'awards_and_scholarships',
        'volunteering_and_leadership',
        'work_experience',
        'projects'
    ]
    skills_key = ['skills']
    general_txts = []
    special_txts = []
    skill_txt = ""
    candidate_name = ""
    candidate_title = ""
    for item in sections_dct_list:
        key = next(iter(item))
        if key == "name":
            candidate_name = item[key]
        elif key == "title":
            candidate_title = item[key]
        if key in general_keys:
            temp = helpers.filter_output(parsers.inv_parse_cv(item).strip())
            general_txts.append(temp)
        elif key in skills_key:
            temp = helpers.filter_output(parsers.inv_parse_cv_out(item).strip())
            skill_txt += temp + "\n"
        elif key in special_keys:
            if skill_section:
                temp = helpers.filter_output(parsers.inv_parse_cv_out(item).strip())
            else:
                temp = helpers.filter_output(parsers.inv_parse_cv(item).strip())
            special_txts.append(temp)
    print(f"slide_summary: candidate_name: {candidate_name}")
    print(f"slide_summary: candidate_title: {candidate_title}")
    print(f"slide_summary: general_txts: {len(general_txts)}")
    print(f"slide_summary: special_txts: {len(special_txts)}")
    slide_results = []
    if windows == 2:
        track = len(special_keys) - 1
    elif windows == 3:
        track = len(special_keys) - 2
    elif windows == 4:
        track = len(special_keys) - 3
    else:
        raise ValueError("Invalid number of windows, must be 2, 3, or 4.")
    for i in range(0, track):
        if windows == 2:
            slide = sliding_window_two_sections(
                section1=special_txts[i],
                section2=special_txts[i + 1],
                model=model,
                system=system,
                system1=system1,
                system2=system2,
                section1_name=special_keys[i],
                section2_name=special_keys[i + 1],
                candidate_name=candidate_name,
                candidate_title=candidate_title,
                ollama_url=ollama_url,
                mode=mode
            )
            slide_results.append(slide)
        elif windows == 3:
            slide = sliding_window_three_sections(
                section1=special_txts[i],
                section2=special_txts[i + 1],
                section3=special_txts[i + 2],
                model=model,
                system=system,
                system1=system1,
                system2=system2,
                system3=system3,
                section1_name=special_keys[i],
                section2_name=special_keys[i + 1],
                section3_name=special_keys[i + 2],
                candidate_name=candidate_name,
                candidate_title=candidate_title,
                ollama_url=ollama_url,
                mode=mode
            )
            slide_results.append(slide)
        elif windows == 4:
            slide = sliding_window_four_sections(
                section1=special_txts[i],
                section2=special_txts[i + 1],
                section3=special_txts[i + 2],
                section4=special_txts[i + 3],
                model=model,
                system=system,
                system1=system1,
                system2=system2,
                system3=system3,
                system4=system4,
                section1_name=special_keys[i],
                section2_name=special_keys[i + 1],
                section3_name=special_keys[i + 2],
                section4_name=special_keys[i + 3],
                candidate_name=candidate_name,
                candidate_title=candidate_title,
                ollama_url=ollama_url,
                mode=mode
            )
            slide_results.append(slide)
    general_info = "\n".join(general_txts).strip()
    general_info_summary = summarize_general_info(general_info, model=model, system=system_s, ollama_url=ollama_url)
    skills_summary = summarize_skills(model=model, system=system_s, ollama_url=ollama_url, skill_section=skill_txt)
    slide_results.insert(0, general_info_summary)
    slide_results.append(skills_summary)
    return slide_results

@log_time
def step0_tailor_summary(model=DEFAULT_MODEL, ollama_url=DEFAULT_URL, raw_cv_data = ""
                         , system_s = "", system = "", system1 = "", system2 = "", system3 = "", system4 = "", system0 = "",
                         windows = 2, skill_section = False, mode="single"):

    if skill_section:
        sections_dct = parsers.parse_cv_out(raw_cv_data)
    else:
        sections_dct = parsers.parse_cv(raw_cv_data)
    sections_dct_list = parsers.dict_spliter(sections_dct)
    slides = slide_summary(sections_dct_list,
                            model=model,
                            system_s=system_s, system=system, system1=system1, system2=system2, system3=system3, system4=system4,
                            ollama_url=ollama_url, windows=windows, mode=mode, skill_section=skill_section)
    #Join slides
    slides_txt = "\n".join(slides).strip()
    prompt = f"""Given the following resume sections summarized:
{slides_txt}
Create a wholistic summary of all of them, following these guidelines:
- Include the candidate's contact information, as well as their title and name.
- Include any certifications or qualifications.
- Include all education.
- Include all projects, work experience, and volunteering and leadership roles.
- Include all information, competencies, achievements, and skills, this is a wholistic summary of the candidate's qualifications.
- Maintain the context and flow between the sections.
- Be very concise but detail-driven as well, which means that you must include as many relevant details as possible with minimal fluff.
Return the summarized information as a single continuous string of text, following this format strictly:
[0]Summary: Wholistic summary of all sections.
"""
    if config.DEBUG["TOKEN_LOGGING"]: input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system0,
        "prompt": prompt,
        "stream": False,
        "temperature": CONFIG["MODELS"]["TEMPERATURE"]
    }
    for field in ["model", "system", "prompt", "stream", "temperature"]:
        value = payload.get(field, None)
        if value is not None:
            logging.info(f"[OLLAMA]step0_tailor_summary: payload field {field} with value {value} found")
        else:
            logging.error(f"[ERROR][OLLAMA]step0_tailor_summary: payload field {field} is missing or is NoneType")
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        
        if response.status_code == 400:
            logging.error(f"[ERROR][OLLAMA]Bad Request: Payload={payload}, Response={result}")
        response_text = result.get("response", "")
        if config.DEBUG["TOKEN_LOGGING"]: output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        print(f"[SUCCESS][OLLAMA]step0_tailor_summary: {result}")
        return helpers.filter_output(response_text.strip())
    except requests.exceptions.JSONDecodeError as e:
        logging.error("[ERROR][OLLAMA]step0_tailor_summary: Ollama response was not valid JSON.", exc_info=True)
        logging.error(f"Response text: {response.text}")
        return "[ERROR][OLLAMA]step0_tailor_summary: Ollama response was not valid JSON."

@log_time
def step1_tailor_summary(model=DEFAULT_MODEL, ollama_url=DEFAULT_URL, 
                         prev_summary = "", job_description  = "", system = ""):
    prompt = f"""Given the following wholistic summary of a resume:
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
"""
    if config.DEBUG["TOKEN_LOGGING"]: input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False,
        "temperature": CONFIG["MODELS"]["TEMPERATURE"]
    }
    for field in ["model", "system", "prompt", "stream", "temperature"]:
        value = payload.get(field, None)
        if value is not None:
            logging.info(f"[OLLAMA]step1_tailor_summary: payload field {field} with value {value} found")
        else:
            logging.error(f"[ERROR][OLLAMA]step1_tailor_summary: payload field {field} is missing or is NoneType")
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        
        if response.status_code == 400:
            logging.error(f"[ERROR][OLLAMA]Bad Request: Payload={payload}, Response={result}")
        response_text = result.get("response", "")
        if config.DEBUG["TOKEN_LOGGING"]: output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        print(f"[SUCCESS][OLLAMA]step1_tailor_summary: {result}")
        return helpers.filter_output(response_text.strip())
    except requests.exceptions.JSONDecodeError as e:
        logging.error("[ERROR][OLLAMA]step1_tailor_summary: Ollama response was not valid JSON.", exc_info=True)
        logging.error(f"Response text: {response.text}")
        return "[ERROR][OLLAMA]step1_tailor_summary: Ollama response was not valid JSON."

@log_time
def tailor_summary(model=DEFAULT_MODEL, ollama_url=DEFAULT_URL,
                    raw_cv_data="", job_description="",
                    system_s="", system00="", system1="", system2="", system3="", system4="", system0="", windows=2,
                    system01="", mode="single"):
    # - Summary (LAST; Based on Job Description AND Overall Resume)
    print(f"tailor_summary: raw_cv_data:\n" + raw_cv_data)
    step0 = step0_tailor_summary(model=model, ollama_url=ollama_url, raw_cv_data=raw_cv_data,
                                  system_s=system_s, system=system00, system1=system1, system2=system2, system3=system3, system4=system4, system0=system0,
                                  windows=windows, mode=mode)
    step1 = step1_tailor_summary(model=model, ollama_url=ollama_url, prev_summary=step0, job_description=job_description,
                                  system=system01)
    return step1.strip()

@log_time
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
            if (templine != "") or templine:
                parts = line.split(";")
                parts = [part.strip() for part in parts]
                    #Programming Languages: Programming Language N1, ..., Programming Language NN
                    #Technical Skills: Technical Skill N1, ..., Technical Skill N2
                    #Soft Skills: Soft Skill N1, ..., Soft Skill N2
                for part in enumerate(parts):
                    if "Programming Languages:" in part:
                        skills = part.split(":")
                        if len(skills) > 1:
                            skills = [skill.strip() for skill in skills]
                            skills_r = skills[1].split(",")
                            skills_r = [skill.strip() for skill in skills_r]
                            programming_skills += skills_r
                        else:
                            print("No Programming Languages found in Skills section")
                    elif "Technical Skills:" in part:
                        skills = part.split(":")
                        if len(skills) > 1:
                            skills = [skill.strip() for skill in skills]
                            skills_r = skills[1].split(",")
                            skills_r = [skill.strip() for skill in skills_r]
                            technical_skills += skills_r
                        else:
                            print("No Technical Skills found in Skills section")
                    elif "Soft Skills:" in part:
                        skills = part.split(":")
                        if len(skills) > 1:
                            skills = [skill.strip() for skill in skills]
                            skills_r = skills[1].split(",")
                            skills_r = [skill.strip() for skill in skills_r]
                            soft_skills += skills_r
                        else:
                            print("No Soft Skills found in Skills section")

                # if "Programming Languages" in line:

                #     part0 = parts[0].split(": ")
                #     part0_prog = part0[2]
                #     part0_prog_splt = part0_prog.split(", ")
                #     programming_skills += part0_prog_splt
                # else:
                #     print("No Programming Languages found in Skills section")
                # if "Technical Skills" in line:
                #     part1 = parts[1].split(": ")
                #     part1_tech = part1[1]
                #     part1_tech_splt = part1_tech.split(", ")
                #     technical_skills += part1_tech_splt
                # else:
                #     print("No Technical Skills found in Skills section")
                # if "Soft Skills" in line:
                #     part2 = parts[2].split(": ")
                #     part2_soft = part2[1]
                #     part2_soft_splt = part2_soft.split(", ")
                #     soft_skills += part2_soft_splt
                # else:
                #     print("No Soft Skills found in Skills section")
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

@log_time
def tailor_skills(model=DEFAULT_MODEL, system="", ollama_url=DEFAULT_URL, cv_data="", job_description="", section="Skills"):

    prompt = f"""Given the following list of "Programming Languages", "Technical Skills" and "Soft Skills" considered to be relevant for the job description below them:
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
"""
    if config.DEBUG["TOKEN_LOGGING"]: input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False,
        "temperature": CONFIG["MODELS"]["TEMPERATURE"]
    }
    for field in ["model", "system", "prompt", "stream", "temperature"]:
        value = payload.get(field, None)
        if value is not None:
            logging.info(f"[OLLAMA]tailor_skills: payload field {field} with value {value} found")
        else:
            logging.error(f"[ERROR][OLLAMA]tailor_skills: payload field {field} is missing or is NoneType")
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        
        if response.status_code == 400:
            logging.error(f"[ERROR][OLLAMA]Bad Request: Payload={payload}, Response={result}")
        response_text = result.get("response", "")
        if config.DEBUG["TOKEN_LOGGING"]: output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        print(f"[SUCCESS][OLLAMA]tailor_skills: {result}")
        return response_text
    except requests.exceptions.JSONDecodeError as e:
        logging.error("[ERROR][OLLAMA]tailor_skills: Ollama response was not valid JSON.", exc_info=True)
        logging.error(f"Response text: {response.text}")
        return "[ERROR][OLLAMA]tailor_skills: Ollama response was not valid JSON."

#Resume/Cover Letter Consistency Checker VS Old Resume
#Chain: old resume, new resume >>> new_vs_old_section >>> consistency_checker_vs_cv
#Chain: new resume, cover letter >>> summarize resume >>> consistency_checker_vs_cv
@log_time
def new_vs_old_section(old_resume_s_txt, new_resume_s_txt, section_name = "", model = DEFAULT_MODEL, system = "", ollama_url = DEFAULT_URL):
    prompt = f"""Given the following raw untailored resume section:
{old_resume_s_txt}
And the following tailored resume section:
{new_resume_s_txt}
Compare the two resume sections and:
- Confirm that the tailored section does not contain any made-up information.
- Verify that all information in the tailored section is present in the raw section, even if paraphrased.
- Identify any contradictions between the two sections.
- Identify any contradictions within the tailored section (with itself).
Output your analysis as a single continuous string of text, strictly following the format below:
[0]{section_name} Analysis:
"""
    if config.DEBUG["TOKEN_LOGGING"]: input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False,
        "temperature": CONFIG["MODELS"]["TEMPERATURE"]
    }
    for field in ["model", "system", "prompt", "stream", "temperature"]:
        value = payload.get(field, None)
        if value is not None:
            logging.info(f"[OLLAMA]new_vs_old_section: payload field {field} with value {value} found")
        else:
            logging.error(f"[ERROR][OLLAMA]new_vs_old_section: payload field {field} is missing or is NoneType")
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        
        if response.status_code == 400:
            logging.error(f"[ERROR][OLLAMA]Bad Request: Payload={payload}, Response={result}")
        response_text = result.get("response", "")
        if config.DEBUG["TOKEN_LOGGING"]: output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        print(f"[SUCCESS][OLLAMA]new_vs_old_section: {result}")
        return helpers.filter_output(response_text.strip())
    except requests.exceptions.JSONDecodeError as e:
        logging.error("[ERROR][OLLAMA]new_vs_old_section: Ollama response was not valid JSON.", exc_info=True)
        logging.error(f"Response text: {response.text}")
        return "[ERROR][OLLAMA]new_vs_old_section: Ollama response was not valid JSON."
    return

@log_time
def new_vs_old_resume(old_resume_txt = "", new_resume_txt = "", model = DEFAULT_MODEL, system_s = "", ollama_url = DEFAULT_URL):
    old_resume_txt0 = return_text_with_skills(old_resume_txt)
    old_dcts = parsers.dict_spliter(parsers.parse_cv_out(helpers.filter_output(old_resume_txt0.strip())))
    new_dcts = parsers.dict_spliter(parsers.parse_cv_out(helpers.filter_output(new_resume_txt.strip())))
    old_txts = [parsers.inv_parse_cv_out(dct).strip() for dct in old_dcts]
    new_txts = [parsers.inv_parse_cv_out(dct).strip() for dct in new_dcts]
    analysis_txts = []
    print("Length of old_txts:", len(old_txts))
    print("Length of new_txts:", len(new_txts))
    if len(old_txts) != len(new_txts):
        raise ValueError("The number of sections in the old and new resumes do not match.")
    for i in range(len(old_txts)):
        analysis_txt = new_vs_old_section(old_txts[i], new_txts[i], model=model, system=system_s, ollama_url=ollama_url)
        analysis_txts.append(analysis_txt)
    return analysis_txts

@log_time
def consistency_checker_vs_cv(model=DEFAULT_MODEL, ollama_url=DEFAULT_URL, system = "", system_s="", cv_data="", cv_data_orig ="", type="CV"):
    if type == "CV":
        print("Consistency Checker: Tailored Resume VS Original Resume:")
        #Chain: old resume, new resume >>> new_vs_old_section >>> consistency_checker_vs_cv
        text_analysis =new_vs_old_resume(old_resume_txt=cv_data_orig, new_resume_txt=cv_data, 
                                         model=model, ollama_url=ollama_url, 
                                         system_s=system_s)
        #Join the analysis texts into a single string
        all_analysis = "\n".join(text_analysis).strip()
        prompt = f"""The following list contains a per-section analysis of the resumes, comparing the synthesized data in the new resume against the original:
{all_analysis}
Now, given this information, synthesize a report which extracts the following data from the list of analyses:
- Whether the new resume is consistent with the original resume, meaning that all information in the new resume is present in the original resume, even if paraphrased.
- Whether the new resume is consistent with itself, meaning that there should be no contradictions or inconsistencies in the information provided.
The report should follow these guidelines:
- Be mindful not to include any line breaks in  the content of any of the sections/subsections.
- Be as objective as possible, and if you must make assumptions, make very conservative assumptions
- Do not create nor imagine any data that is not present in the original data.
The consistency check should be returned strictly in the following format (include the numbers "[0]", "[1]", do not modify the format):
[0]Consistency Checker VS Original Resume:
[1]Inconsistencies With Original Resume: [Yes/No]; [List of inconsistencies found, if any; return 'None' if no inconsistencies; must be a continuous block of text, composed of sentences separated by ".", not line breaks]
[1]Inconsistencies With Self: [Yes/No]; [List of inconsistencies found, if any; return 'None' if no inconsistencies; must be a continuous block of text, composed of sentences separated by ".", not line breaks]
[1]Suggestions for Improvement: [List of suggestions for improvement, if any; return 'None' if no suggestions; must be a continuous block of text, composed of sentences separated by ".", not line breaks]
"""
    
    elif type == "CL":
        print("Consistency Checker: Cover Letter VS Original Resume:")
        #Chain: new resume, cover letter >>> summarize resume >>> consistency_checker_vs_cv
        prompt = f"""Given the following cover letter:
{cv_data}
And the wholistic summary of the resume meant to accompany it on a job application:
{cv_data_orig}
Perform a consistency check on the tailored cover letter against the resume. This consistency check should include:
- Whether the cover letter is consistent with the resume, meaning that all skills and experiences mentioned in the cover letter should be present in the resume.
- Whether the cover letter is consistent with itself, meaning that there should be no contradictions or inconsistencies in the information provided.
The report should follow these guidelines:
- Be mindful not to include any line breaks in  the content of any of the sections/subsections.
- Be as objective as possible, and if you must make assumptions, make very conservative assumptions
- Do not create nor imagine any data that is not present in the original data.
The consistency check should be returned strictly in the following format (include the numbers "[0]", "[1]", do not modify the format):
[0]Consistency Checker Vs Resume:
[1]Inconsistencies With Resume: [Yes/No]; [List of inconsistencies found, if any; return 'None' if no inconsistencies; must be a continuous block of text, composed of sentences separated by ".", not line breaks]
[1]Inconsistencies With Self:  [Yes/No]; [List of inconsistencies found, if any; return 'None' if no inconsistencies; must be a continuous block of text, composed of sentences separated by ".", not line breaks]
[1]Suggestions for Improvement: [List of suggestions for improvement, if any; return 'None' if no suggestions; must be a continuous block of text, composed of sentences separated by ".", not line breaks]
"""
    
    if config.DEBUG["TOKEN_LOGGING"]: input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False,
        "temperature": CONFIG["MODELS"]["TEMPERATURE"]
    }
    for field in ["model", "system", "prompt", "stream", "temperature"]:
        value = payload.get(field, None)
        if value is not None:
            logging.info(f"[OLLAMA]consistency_checker_vs_cv: payload field {field} with value {value} found")
        else:
            logging.error(f"[ERROR][OLLAMA]consistency_checker_vs_cv: payload field {field} is missing or is NoneType")
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    
    try:
        result = response.json()
        
        if response.status_code == 400:
            logging.error(f"[ERROR][OLLAMA]Bad Request: Payload={payload}, Response={result}")
        response_text = result.get("response", "")
        if config.DEBUG["TOKEN_LOGGING"]: output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        print(f"[SUCCESS][OLLAMA]consistency_checker_vs_cv: {result}")
        return response_text
    except requests.exceptions.JSONDecodeError as e:
        logging.error("[ERROR][OLLAMA]consistency_checker_vs_cv: Ollama response was not valid JSON.", exc_info=True)
        logging.error(f"Response text: {response.text}")
        return "[ERROR][OLLAMA]consistency_checker_vs_cv: Ollama response was not valid JSON."

#Tailor Cover Letter
#Chain: new resume, job_desc >>> summarize resume, job desc >>> make_cover_letter_text
@log_time
def make_cover_letter_text(model=DEFAULT_MODEL,system = "",
                           ollama_url=DEFAULT_URL, cv_data="", job_description=""):
    prompt = f"""Given the following wholistic summary of a resume:
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
"""
    
    if config.DEBUG["TOKEN_LOGGING"]: input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False,
        "temperature": CONFIG["MODELS"]["TEMPERATURE"]
    }
    for field in ["model", "system", "prompt", "stream", "temperature"]:
        value = payload.get(field, None)
        if value is not None:
            logging.info(f"[OLLAMA]make_cover_letter_text: payload field {field} with value {value} found")
        else:
            logging.error(f"[ERROR][OLLAMA]make_cover_letter_text: payload field {field} is missing or is NoneType")
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    
    try:
        result = response.json()
        
        if response.status_code == 400:
            logging.error(f"[ERROR][OLLAMA]Bad Request: Payload={payload}, Response={result}")
        response_text = result.get("response", "")
        if config.DEBUG["TOKEN_LOGGING"]: output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        print(f"[SUCCESS][OLLAMA]make_cover_letter_text: {result}")
        return response_text
    except requests.exceptions.JSONDecodeError as e:
        logging.error("[ERROR][OLLAMA]make_cover_letter_text: Ollama response was not valid JSON.", exc_info=True)
        logging.error(f"Response text: {response.text}")
        return "[ERROR][OLLAMA]make_cover_letter_text: Ollama response was not valid JSON."

@log_time
def compose_cover_letter_dictionary(model=DEFAULT_MODEL, ollama_url=DEFAULT_URL, cv_text_summary="", cv_text="", job_description=""):
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
    cover_letter_text = make_cover_letter_text(model=model,system = system,
                           ollama_url=ollama_url, cv_data=cv_text_summary, job_description=job_description)

    clean_cover_letter_text = helpers.filter_output(cover_letter_text)
    
    clean_cover_letter_dict = parsers.parse_cl(clean_cover_letter_text)
    
    #Make a list of dicts with name, title, languages, contact_info and clean_cover_letter_dict
    dict_list = [name,title,languages,contact_info,clean_cover_letter_dict]
    output_dict = parsers.dict_grafter(dict_list)
    #Return the output_dict
    return output_dict

#Resume/Cover Letter Consistency Checker VS Job Description
#Chain: cover letter, job_desc >>> summarize job desc >>> consistency_checker_vs_job_desc
#Chain: new resume, job_desc >>> summarize resume, job desc >>> consistency_checker_vs_job_desc
@log_time
def consistency_checker_vs_job_desc(model=DEFAULT_MODEL,  ollama_url=DEFAULT_URL, system="", cv_data="", job_description="", type="CV"):
    if type == "CV":
        prompt = f"""Given the following summary of a resume:
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
"""
    elif type == "CL":

        prompt = f"""Given the following cover letter:
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
"""
    
    if config.DEBUG["TOKEN_LOGGING"]: input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False,
        "temperature": CONFIG["MODELS"]["TEMPERATURE"]
    }
    for field in ["model", "system", "prompt", "stream", "temperature"]:
        value = payload.get(field, None)
        if value is not None:
            logging.info(f"[OLLAMA]consistency_checker_vs_job_desc: payload field {field} with value {value} found")
        else:
            logging.error(f"[ERROR][OLLAMA]consistency_checker_vs_job_desc: payload field {field} is missing or is NoneType")
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    
    try:
        result = response.json()
        
        if response.status_code == 400:
            logging.error(f"[ERROR][OLLAMA]Bad Request: Payload={payload}, Response={result}")
        response_text = result.get("response", "")
        if config.DEBUG["TOKEN_LOGGING"]: output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        print(f"[SUCCESS][OLLAMA]consistency_checker_vs_job_desc: {result}")
        return response_text
    except requests.exceptions.JSONDecodeError as e:
        logging.error("[ERROR][OLLAMA]consistency_checker_vs_job_desc: Ollama response was not valid JSON.", exc_info=True)
        logging.error(f"Response text: {response.text}")
        return "[ERROR][OLLAMA]consistency_checker_vs_job_desc: Ollama response was not valid JSON."
#Tailor courses
@log_time
def tailor_courses(courses = "", job_description = "", model = DEFAULT_MODEL, system="", ollama_url=DEFAULT_URL):
    # Given a block of text with all courses taken in a given program
    # and a job description, this function will extract relevant courses
    # that match the skills and requirements outlined in the job description.
        # The format of each course is XXXYYY Course Name, where XXXYYY is the course code (e.g. CSC101, ECE201)
        # Courses are comma-separated
    prompt = f"""Given the following courses taken on a given program:
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
"""
    
    if config.DEBUG["TOKEN_LOGGING"]: input_tks = helpers.token_math(model, prompt)
    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False,
        "temperature": CONFIG["MODELS"]["TEMPERATURE"]
    }
    for field in ["model", "system", "prompt", "stream", "temperature"]:
        value = payload.get(field, None)
        if value is not None:
            logging.info(f"[OLLAMA]tailor_courses: payload field {field} with value {value} found")
        else:
            logging.error(f"[ERROR][OLLAMA]tailor_courses: payload field {field} is missing or is NoneType")
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    
    try:
        result = response.json()
        
        if response.status_code == 400:
            logging.error(f"[ERROR][OLLAMA]Bad Request: Payload={payload}, Response={result}")
        response_text = result.get("response", "")
        if config.DEBUG["TOKEN_LOGGING"]: output_tks = helpers.token_math(model, response_text, type="output", offset = input_tks)
        print(f"[SUCCESS][OLLAMA]tailor_courses: {result}")
        response_text = helpers.filter_output(response_text.strip())
        #remove [1]Courses: 
        response_text = response_text.replace("[1]Courses:", "").strip()
        return response_text
    except requests.exceptions.JSONDecodeError as e:
        logging.error("[ERROR][OLLAMA]tailor_courses: Ollama response was not valid JSON.", exc_info=True)
        logging.error(f"Response text: {response.text}")
        return "[ERROR][OLLAMA]tailor_courses: Ollama response was not valid JSON."
    
    
