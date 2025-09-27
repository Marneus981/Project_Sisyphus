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
from Sisyphus import payloads_wip as payloads
import re
import traceback
DEFAULT_MODEL = "llama3:8b"
DEFAULT_URL = "http://localhost:11434"

template_call_info = {
    "call_id": "", 
    "payload_in": {
                    "model": DEFAULT_MODEL, #Set at runtime
                    "system": "",  #Set at runtime
                    "stream": False,
                    "temperature": CONFIG["MODELS"]["TEMPERATURE"]
                    },
    "format": {},
    "prompt_in": "",
    "ollama_url": DEFAULT_URL, #Set at runtime
    "sample_starts": [] #[type, sample starts]
}

print = logging.info
#region MISC FUNCTIONS
def fetch_complete_call_info(call_id = "", runtime_info = {}):
    function_name =helpers.inspect_function()
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: fetching complete call info for call id {call_id}...")
    if call_id not in payloads.PAYLOADS:
        if config.DEBUG["ERROR_LOGGING"]: print(f"[ERROR][OLLAMA]{function_name}: call_id {call_id} not found in payloads.PAYLOADS")
        raise ValueError(f"[ERROR][OLLAMA]{function_name}: call_id {call_id} not found in payloads.PAYLOADS")
    if call_id == "":
        if config.DEBUG["ERROR_LOGGING"]: print(f"[ERROR][OLLAMA]{function_name}: call_id {call_id} not provided")
        raise ValueError(f"[ERROR][OLLAMA]{function_name}: call_id {call_id} not provided")
    runtime_info_tmp = runtime_info.copy()
    fixed_call_info = payloads.PAYLOADS[call_id].copy()
    for key in runtime_info_tmp:
        if key == "payload_in" or key == "format":
            for key_n in runtime_info_tmp[key]:
                fixed_call_info[key][key_n] = runtime_info_tmp[key][key_n]
        else:
            fixed_call_info[key] = runtime_info_tmp[key]
    if config.DEBUG["INFO_LOGGING"]: 
        print(f"[INFO][OLLAMA]{function_name}: complete call info:")
        for key in fixed_call_info:
            print(f"[INFO][OLLAMA]{function_name}: found key {key} with value:")
            print(f"{fixed_call_info[key]}")
    return fixed_call_info

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
                for part in parts:
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

def compare_start_nb(output, sample_starts = []):
    # Compare the two outputs and return the differences
    function_name = helpers.inspect_function()
    if sample_starts == []:
        return True
    comparison_type = sample_starts[0].strip() #strict or flexible
    if comparison_type not in ["strict", "flexible"]:
        raise ValueError(f"[ERROR]{function_name}: invalid comparison_type {comparison_type}, allowed types are strict or flexible")
    start_lines = sample_starts[2:] #exclude type, filter type: digits or cap_letters
    start_lines = [line.strip() for line in start_lines if line.strip()]
    output_lines = output.splitlines()
    output_lines = [line.strip() for line in output_lines if line.strip()]
    if len(start_lines) != len(output_lines):
        # Handle length mismatch
        if comparison_type == "strict":
            return False

    for i in range(len(output_lines)):
        #Check if output lines starts with start_lines
        if comparison_type == "strict":
            if output_lines[i].startswith(start_lines[i]):
                continue
            else:
                return False
        elif comparison_type == "flexible":
            for j in range(len(start_lines)):
                if output_lines[i].startswith(start_lines[j]):
                    break
            else:
                return False
    return True
@log_time
def compare_start(output, sample_starts = []):
    function_name = helpers.inspect_function()
    # Compare the two outputs and return the differences
    if sample_starts == []:
        if config.DEBUG["WARNING_LOGGING"]: logging.warning(f"[WARNING]{function_name}: sample_starts is empty, verify PAYLOADS or code logic")
        return True
    comparison_type = sample_starts[0].strip() #strict or flexible
    if comparison_type not in ["strict", "flexible"]:
        if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR]{function_name}: Invalid comparison type: {comparison_type}")
        raise ValueError(f"[ERROR]{function_name}: invalid comparison_type {comparison_type}, allowed types are strict or flexible")
    start_lines = sample_starts[2:] #exclude type, filter type: digits or cap_letters
    start_lines = [line.strip() for line in start_lines if line.strip()]
    output_lines = output.splitlines()
    output_lines = [line.strip() for line in output_lines if line.strip()]
    if len(start_lines) != len(output_lines):
        # Handle length mismatch
        if comparison_type == "strict":
            if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR]{function_name}: Length mismatch: {len(start_lines)} != {len(output_lines)}")
            return False
        if config.DEBUG["WARNING_LOGGING"]: logging.warning(f"[WARNING]{function_name}: Length mismatch: {len(start_lines)} != {len(output_lines)}")
    else:
        if config.DEBUG["INFO_LOGGING"]: print("[SUCCESS]Output matches expected length")

    for i in range(len(output_lines)):
        #Check if output lines starts with start_lines
        if comparison_type == "strict":
            if output_lines[i].startswith(start_lines[i]):
                continue
            else:
                logging.warning(f"[ERROR]{function_name}: Output line {i} does not start with sample start line")
                print(f"[ERROR]{function_name}: Output line: {output_lines[i]}")
                print(f"[ERROR]{function_name}: Expected start line: {start_lines[i]}")
                return False
        elif comparison_type == "flexible":
            for j in range(len(start_lines)):
                if output_lines[i].startswith(start_lines[j]):
                    break
            else:
                logging.warning(f"[ERROR]compare_start: Output line {i} does not start with any sample start line")
                print(f"[ERROR]{function_name}: Output line: {output_lines[i]}")
                print(f"[ERROR]{function_name}: Expected start lines: {start_lines}")
                return False
    if config.DEBUG["INFO_LOGGING"]: print("[SUCCESS]Output matches expected start lines")
    return True

@log_time
def clean_first_step(text):
    # Remove lines that do not start with [X] where X is a capitalized letter
    function_name = helpers.inspect_function()
    cleaned_lines = []
    for line in text.split('\n'):
        if line.startswith(("[R]", "[J]", "[P]", "[E]")):
            line = line.strip()
            prefix = line[0:3]
            temp_lines = line[3:].split(':')
            if len(temp_lines) == 1:
                raise ValueError(f"[ERROR]{function_name}: No experience title found")
            cleaned_lines.append(prefix.strip() + temp_lines[1].strip())
    return '\n'.join(cleaned_lines)  

@log_time
def augment_output(input_text, reference_dict, type):
    function_name = helpers.inspect_function()
    allowed_types = ['volunteering_and_leadership','work_experience','projects', 'vl_w_p', ]
    if type not in allowed_types:
        raise ValueError(f"[ERROR]{function_name}: Invalid type: {type}. Allowed types are: {allowed_types}")
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
                    if line.strip().lower() == item['role'].lower():
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
                    if line.strip().lower() == item['job_title'].lower():
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
                    if line.strip().lower() == item['project_title'].lower():
                        return_list.append(item)
                        reference_list.remove(item)
                        break
        tmp_dict[type] = return_list

    elif type == 'vl_w_p':
        # Remove [R], [J], [P] markers at the start of each line
        input_lines = [line[3:] if line.startswith(('[E]')) else line for line in input_lines]
        return_list = [[],[],[]]
        # reference_list_vl = reference_dict['volunteering_and_leadership']
        # reference_list_w = reference_dict['work_experience']
        # reference_list_p = reference_dict['projects']
        super_list = reference_dict['volunteering_and_leadership'] + reference_dict['work_experience'] + reference_dict['projects']
        for line in input_lines:

            for item in super_list:
                #Check if role field exists in item
                if 'role' in item:
                    if line.strip().lower() == item['role'].lower():
                        return_list[0].append(item)
                        super_list.remove(item)

                        break
                if 'job_title' in item:
                    if line.strip().lower() == item['job_title'].lower():
                        return_list[1].append(item)
                        super_list.remove(item)

                        break
                if 'project_title' in item:
                    if line.strip().lower() == item['project_title'].lower():
                        return_list[2].append(item)
                        super_list.remove(item)

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
                line = line.replace("[1]Role: ", "Experience:").replace("[1]Description: ", "Description: ").replace("[1]Skills: ", "Skills: ").strip()
                if line:
                    return_list.append(line)
        for item in return_list:
            return_text += f"{item}\n"
        return return_text

    if type == 'work_experience':
        for line in input_lines:
            if not line.startswith(("[0]Work Experience:", "[1]Company:", "[1]Location:", "[1]Duration:")):
                line = line.replace("[1]Job Title: ", "Experience:").replace("[1]Description: ", "Description: ").replace("[1]Skills: ", "Skills: ").strip()
                if line:
                    return_list.append(line)
        for item in return_list:
            return_text += f"{item}\n"
        return return_text
    if type == 'projects':
        for line in input_lines:
            if not line.startswith(("[0]Projects:", "[1]URL:", "[1]Type:", "[1]Duration:")):
                line = line.replace("[1]Project Title: ", "Experience:").replace("[1]Description: ", "Description: ").replace("[1]Skills: ", "Skills: ").strip()
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
                line = line.replace("[1]Role: ", "Experience:").replace("[1]Description: ", "Description: ").replace("[1]Skills: ", "Skills: ").replace("[1]Job Title: ", "Experience:").replace("[1]Project Title: ", "Experience:").strip()
                if line:
                    return_list.append(line)
        for item in return_list:
            return_text += f"{item}\n"
        return return_text
#endregion

#region SYNC OLLAMA CALLS
"""
Call Payload Format:
{
        "call_id": "call_id_string", #Usually the old tailor function name, used to fetch info from payloads.PAYLOADS
        "payload_in": {
                       "model": DEFAULT_MODEL, #Set at runtime
                       "system": "",  #Set at runtime
                       "stream": False,
                       "temperature": CONFIG["MODELS"]["TEMPERATURE"]
                       # Add prompt at runtime
                       ...
                       },
        "format": {#Set at runtime
                   "field1": "",
                   "field2": "",
                   ...
                   },
        "prompt_in": "...{field1}...{field2}...",
        "ollama_url": DEFAULT_URL,
        "sample_starts": [strict/flexible, digits/cap_letters, start1, start2, ...] #[type, sample starts]
    }
"""

#region STANDARD CALL
@log_time
def standard_ollama_call(call_info =template_call_info):
    call_id = call_info["call_id"]
    payload_in = call_info["payload_in"]
    format = call_info["format"]
    prompt_in = call_info["prompt_in"]
    ollama_url = call_info["ollama_url"]
    function_name = helpers.inspect_function()
    #General Checks
    if call_id not in payloads.STANDARD:
        if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: call_id {call_id} not found in STANDARD payloads")
        return f"[ERROR][OLLAMA]{function_name}: call_id {call_id} not found in STANDARD payloads"
    if config.DEBUG["INFO_LOGGING"]: logging.info(f"[OLLAMA]{function_name}: call_id: {call_id}")
    if prompt_in == "":
        if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: prompt_in is empty string")
        return f"[ERROR][OLLAMA]{function_name}: prompt_in is empty string"
    #Check for formatting in prompt_in
    pattern = r"\{[a-z0-9_]+\}"
    search_pattern = re.search(pattern, prompt_in)
    if search_pattern:
        if config.DEBUG["WARNING_LOGGING"]: logging.warning(f"[WARNING][OLLAMA]{function_name}: prompt_in contains placeholders")
    if search_pattern and format != {}:
        helpers.missing_format_pieces(prompt_in,format)
        prompt = prompt_in.format(**format)
        prompt = helpers.process_input(prompt)
    else:
        prompt = prompt_in
        prompt = helpers.process_input(prompt)
    payload = payload_in.copy()
    payload["prompt"] = prompt

    #DEFAULT SYNC CALL CODE
    if config.DEBUG["TOKEN_LOGGING"]: input_tks = helpers.token_math(payload["model"], payload["prompt"])
    for field in ["model", "system", "prompt", "stream", "temperature"]:
        value = payload.get(field, None)
        if value is not None:
            if config.DEBUG["INFO_LOGGING"]: logging.info(f"[OLLAMA]{function_name}: payload field {field} with value {value} found")
        else:
            if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: payload field {field} is missing or is NoneType")
            return f"[ERROR][OLLAMA]{function_name}: payload field {field} is missing or is NoneType"
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        if response.status_code == 400:
            if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: Bad Request: Payload={payload}, Response={result}")
            return f"[ERROR][OLLAMA]{function_name}: Ollama status_code 400"    
        response_text = result.get("response", "")
        if config.DEBUG["TOKEN_LOGGING"]: output_tks = helpers.token_math(payload["model"], response_text, type="output", offset=input_tks)
        if config.DEBUG["INFO_LOGGING"]: print(f"[SUCCESS][OLLAMA]{function_name}: {result}")
        return response_text
    except requests.exceptions.JSONDecodeError as e:
        error_trace =  helpers.traceback_error(e)
        if config.DEBUG["ERROR_LOGGING"]: 
            logging.error("[ERROR][OLLAMA]Traceback:")
            logging.error(f"{error_trace}")
            logging.error(f"[ERROR][OLLAMA]{function_name}: Ollama response was not valid JSON", exc_info=True)
            logging.error(f"[ERROR][OLLAMA]{function_name}: Response text: {response.text}")
        return f"[ERROR][OLLAMA]{function_name}: Ollama response was not valid JSON"
#endregion

#region NON-STANDARD CALLS
@log_time
def batch_summarize_sections(call_info = template_call_info):
    call_id = call_info["call_id"]
    payload_in = call_info["payload_in"]

    sections = call_info["format"].get("sections", [])
    section_names = call_info["format"].get("section_names", [])
    sections_text = "\n".join(sections)
    format = {
        "sections_text": sections_text
    }

    prompt_in = call_info["prompt_in"]
    ollama_url = call_info["ollama_url"]
    function_name = helpers.inspect_function()

    if call_id != function_name:
        if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: call_id {call_id} is not {function_name}")
        return f"[ERROR][OLLAMA]{function_name}: call_id {call_id} is not {function_name}"
    #Needs prompt_in
    if prompt_in == "":
        if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: prompt_in is empty string")
        return f"[ERROR][OLLAMA]{function_name}: prompt_in is empty string"
    
    if config.DEBUG["INFO_LOGGING"]: logging.info(f"[OLLAMA]{function_name}: call_id: {call_id}")
    
    prompt = prompt_in
    for name in section_names:
        prompt =prompt + f"Section Summary: {name} Summary; Wholistic summary of the section's information.\n"

    helpers.missing_format_pieces(call_info["format"]["second_half"],format)
    prompt +=  call_info["format"]["second_half"].format(**format)
    prompt = helpers.process_input(prompt)
    payload = payload_in.copy()
    payload["prompt"] = prompt

    #DEFAULT SYNC CALL CODE
    if config.DEBUG["TOKEN_LOGGING"]: input_tks = helpers.token_math(payload["model"], payload["prompt"])
    for field in ["model", "system", "prompt", "stream", "temperature"]:
        value = payload.get(field, None)
        if value is not None:
            if config.DEBUG["INFO_LOGGING"]: logging.info(f"[OLLAMA]{function_name}: payload field {field} with value {value} found")
        else:
            if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: payload field {field} is missing or is NoneType")
            return f"[ERROR][OLLAMA]{function_name}: payload field {field} is missing or is NoneType"
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        if response.status_code == 400:
            if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: Bad Request: Payload={payload}, Response={result}")
            return f"[ERROR][OLLAMA]{function_name}: Bad Request: Payload={payload}, Response={result}"
        response_text = result.get("response", "")
        if config.DEBUG["TOKEN_LOGGING"]: output_tks = helpers.token_math(payload["model"], response_text, type="output", offset=input_tks)
        print(f"[SUCCESS][OLLAMA]{function_name}: {result}")
        return response_text
    except requests.exceptions.JSONDecodeError as e:
        error_trace =  helpers.traceback_error(e)
        if config.DEBUG["ERROR_LOGGING"]: 
            logging.error("[ERROR][OLLAMA]Traceback:")
            logging.error(f"{error_trace}")
            logging.error(f"[ERROR][OLLAMA]{function_name}: Ollama response was not valid JSON", exc_info=True)
            logging.error(f"[ERROR][OLLAMA]{function_name}: Response text: {response.text}")
        return f"[ERROR][OLLAMA]{function_name}: Ollama response was not valid JSON"

@log_time #USED IN MAIN
def tailor_volunteering_and_leadership(call_info = template_call_info):
    
    call_id = call_info["call_id"]
    payload_in = call_info["payload_in"]
    format = call_info["format"]
    prompt_in = call_info["prompt_in"]
    ollama_url = call_info["ollama_url"]
    function_name = helpers.inspect_function()
    if call_id != function_name:
        if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: call_id {call_id} is not {function_name}")
        return f"[ERROR][OLLAMA]{function_name}: call_id {call_id} is not {function_name}"
    
    raw_cv_data = format["raw_cv_data"]
    job_description_summary = format["job_description_summary"]
    section = format["section"]
    reference_dct = format["reference_dct"]

    #Original Arguments: model=DEFAULT_MODEL, system1="", system2="", ollama_url=DEFAULT_URL, 
                        #raw_cv_data="", job_description_summary="", 
                        #section="volunteering_and_leadership", reference_dct={}
    system1 = format.get("systems", "")[0]
    system2 = format.get("systems", "")[1]
    

    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: raw_cv_data:\n" + raw_cv_data)
    step0 = prepare_input_text(raw_cv_data, type=section)
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step0:\n" + step0)
    
    runtime_info_temp = {"call_id": format["standard_calls"][0],
                          "ollama_url": ollama_url,
                          "format": {
                              "raw_cv_data": step0,
                              "job_description": job_description_summary,
                          },
                          "payload_in":{
                              "system":system1,
                              "model": payload_in["model"]
                          }                   
    }
    step1 = ollama_call(runtime_info= runtime_info_temp)
    #step1 = step0_volunteering_and_leadership(model=model, system1=system1, ollama_url=ollama_url, raw_cv_data=step0, job_description=job_description_summary)

    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: {format.get("standard_calls", "")[0]}:\n" + step1)
    step1_clean = clean_first_step(step1).strip()
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step1_clean:\n" + step1_clean)
    step2_dct = augment_output(step1_clean, reference_dct, type=section)
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step2_dct:\n" + str(step2_dct))
    #helpers.filter_output()#REDUNDANT?
    step2_text = parsers.inv_parse_cv(step2_dct)
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step2_text:\n" + step2_text)
    step3_text = []
    #Delete line that starts with [0]Volunteering and Leadership
    step2_text = step2_text.replace("[0]Volunteering and Leadership:", "")
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step2_text (No [0]):\n" + step2_text)
    #helpers.filter_output()#REDUNDANT?
    step2_text = step2_text.strip()
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step2_text after filtering:\n" + step2_text)
    #Split text into list of individual experiences (each experience starts with [1]Role)
    step3_text = step2_text.split("[1]Role: ")[1:]
    step3_text = ["[1]Role: " + exp for exp in step3_text]
    step3_list = []
    for exp in step3_text:
        if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step3_text(loop): exp:\n" + exp)
        #Transform to dict
        #helpers.filter_output()#REDUNDANT?
        exp_dict = parsers.parse_subfields(exp.strip())
        #Separate dict in two: one containing description and skills, the other containing the rest
        first_part_dict = {k: v for k, v in exp_dict.items() if k in ["description", "skills"]}
        second_part_dict = {k: v for k, v in exp_dict.items() if k not in ["description", "skills"]}
        #Convert to text
        first_part_text = parsers.inv_parse_subfields(first_part_dict).strip()
        second_part_text = parsers.inv_parse_subfields(second_part_dict).strip()
        if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step3_text(loop): exp: first_part_text:\n" + first_part_text)
        if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step3_text(loop): exp: second_part_text:\n" + second_part_text)

        runtime_info_temp = {"call_id": format["standard_calls"][1],
                          "ollama_url": ollama_url,
                          "format": {
                              "experience": first_part_text,
                              "job_description": job_description_summary,
                          },
                          "payload_in":{
                              "system":system2,
                              "model": payload_in["model"]
                          }                   
        }   
        first_part_text_new = ollama_call(runtime_info=runtime_info_temp)

        #first_part_text_new = step3_volunteering_and_leadership(model=model, system2=system2, ollama_url=ollama_url, experience=first_part_text, job_description=job_description_summary)
        if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step3_text(loop): exp: {format.get("standard_calls", "")[1]}: first_part_text_new:\n" + first_part_text_new)
        #helpers.filter_output()#REDUNDANT?
        first_part_text_new = first_part_text_new.strip()
        if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step3_text(loop): exp: {format.get("standard_calls", "")[1]}: first_part_text_new (filtered):\n" + first_part_text_new)
        #Join with second part
        temp = second_part_text + "\n" + first_part_text_new
        if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step3_text(loop): exp: {format.get("standard_calls", "")[1]}: temp(joined):\n" + temp)
        step3_list.append(temp)
    step3_text = "\n".join(step3_list)
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step3_text:\n" + step3_text)
    step4_text = "[0]Volunteering and Leadership:\n" + step3_text
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step4_text (before filtering):\n" + step4_text)
    #helpers.filter_output()#REDUNDANT?
    step4_text = step4_text.strip()
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step4_text (after filtering):\n" + step4_text)
    return step4_text

@log_time #USED IN MAIN
def tailor_work_experience(call_info = template_call_info):
    call_id = call_info["call_id"]
    payload_in = call_info["payload_in"]
    format = call_info["format"]
    prompt_in = call_info["prompt_in"]
    ollama_url = call_info["ollama_url"]
    function_name = helpers.inspect_function()
    if call_id != function_name:
        if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: call_id {call_id} is not {function_name}")
        return f"[ERROR][OLLAMA]{function_name}: call_id {call_id} is not {function_name}"
    
    raw_cv_data = format["raw_cv_data"]
    job_description_summary = format["job_description_summary"]
    section = format["section"]
    reference_dct = format["reference_dct"]
    #Original Arguments: model=DEFAULT_MODEL, system1="", system2="", ollama_url=DEFAULT_URL, 
                          #raw_cv_data="", job_description_summary="", 
                          #section="work_experience", reference_dct={}
    system1 = format.get("systems", "")[0]
    system2 = format.get("systems", "")[1]

    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: raw_cv_data:\n" + raw_cv_data)
    step0 = prepare_input_text(raw_cv_data, type=section)
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step0:\n" + step0)

    runtime_info_temp = {"call_id": format["standard_calls"][0],
                          "ollama_url": ollama_url,
                          "format": {
                              "raw_cv_data": step0,
                              "job_description": job_description_summary,
                          },
                          "payload_in":{
                              "system":system1,
                              "model": payload_in["model"]
                          }               
    }
    step1 = ollama_call(runtime_info= runtime_info_temp)
    #step1 = step0_work_experience(model=model, system1=system1, ollama_url=ollama_url, raw_cv_data=step0, job_description=job_description_summary)
    
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: {format.get("standard_calls", "")[0]}:\n" + step1)
    step1_clean = clean_first_step(step1).strip()
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step1_clean:\n" + step1_clean)
    step2_dct = augment_output(step1_clean, reference_dct, type=section)
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step2_dct:\n" + str(step2_dct))
    #helpers.filter_output()#REDUNDANT?
    step2_text = parsers.inv_parse_cv(step2_dct)
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step2_text:\n" + step2_text)
    step3_text = []
    step2_text = step2_text.replace("[0]Work Experience:", "")
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step2_text (No [0]):\n" + step2_text)
    #helpers.filter_output()#REDUNDANT?
    step2_text = step2_text.strip()
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step2_text after filtering:\n" + step2_text)
    step3_text = step2_text.split("[1]Job Title: ")[1:]
    step3_text = ["[1]Job Title: " + exp for exp in step3_text]
    step3_list = []
    for exp in step3_text:
        if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step3_text(loop): exp:\n" + exp)
        #Transform to dict
        #helpers.filter_output()#REDUNDANT?
        exp_dict = parsers.parse_subfields(exp.strip())
        #Separate dict in two: one containing description and skills, the other containing the rest
        first_part_dict = {k: v for k, v in exp_dict.items() if k in ["description", "skills"]}
        second_part_dict = {k: v for k, v in exp_dict.items() if k not in ["description", "skills"]}
        #Convert to text
        first_part_text = parsers.inv_parse_subfields(first_part_dict).strip()
        second_part_text = parsers.inv_parse_subfields(second_part_dict).strip()
        if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step3_text(loop): exp: first_part_text:\n" + first_part_text)
        if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step3_text(loop): exp: second_part_text:\n" + second_part_text)

        runtime_info_temp = {"call_id": format["standard_calls"][1],
                          "ollama_url": ollama_url,
                          "format": {
                              "experience": first_part_text,
                              "job_description": job_description_summary,
                          },
                          "payload_in":{
                              "system":system2,
                              "model": payload_in["model"]
                          }       
        }   
        first_part_text_new = ollama_call(runtime_info= runtime_info_temp)

        #first_part_text_new = step3_work_experience(model=model, system2=system2, ollama_url=ollama_url, experience=first_part_text, job_description=job_description_summary)
        if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step3_text(loop): exp: {format.get("standard_calls", "")[1]}: first_part_text_new:\n" + first_part_text_new)
        #helpers.filter_output()#REDUNDANT?
        first_part_text_new = first_part_text_new.strip()
        if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step3_text(loop): exp: {format.get("standard_calls", "")[1]}: first_part_text_new (filtered):\n" + first_part_text_new)
        #Join with second part
        temp = second_part_text + "\n" + first_part_text_new
        if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step3_text(loop): exp: {format.get("standard_calls", "")[1]}: temp:\n" + temp)
        step3_list.append(temp)
    step3_text = "\n".join(step3_list)
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step3_text:\n" + step3_text)
    step4_text = "[0]Work Experience:\n" + step3_text
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step4_text before filtering:\n" + step4_text)
    #helpers.filter_output()#REDUNDANT?
    step4_text = step4_text.strip()
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step4_text after filtering:\n" + step4_text)
    return step4_text

@log_time #USED IN MAIN
def tailor_projects(call_info = template_call_info):
    call_id = call_info["call_id"]
    payload_in = call_info["payload_in"]
    format = call_info["format"]
    prompt_in = call_info["prompt_in"]
    ollama_url = call_info["ollama_url"]
    function_name = helpers.inspect_function()
    if call_id != function_name:
        if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: call_id {call_id} is not {function_name}")
        return f"[ERROR][OLLAMA]{function_name}: call_id {call_id} is not {function_name}"
    
    raw_cv_data = format["raw_cv_data"]
    job_description_summary = format["job_description_summary"]
    section = format["section"]
    reference_dct = format["reference_dct"]

    #Original Arguments: model=DEFAULT_MODEL, system1="", system2="", ollama_url=DEFAULT_URL, 
                   #raw_cv_data="", job_description_summary="", 
                   #section="projects", reference_dct={}
    system1 = format.get("systems", "")[0]
    system2 = format.get("systems", "")[1]
    
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: raw_cv_data:\n" + raw_cv_data)
    step0 = prepare_input_text(raw_cv_data, type=section)
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step0:\n" + step0)

    runtime_info_temp = {"call_id": format["standard_calls"][0],
                          "ollama_url": ollama_url,
                          "format": {
                              "raw_cv_data": step0,
                              "job_description": job_description_summary,
                          },
                          "payload_in":{
                              "system":system1,
                              "model": payload_in["model"]
                          }               
    }
    step1 = ollama_call(runtime_info= runtime_info_temp)
    #step1 = step0_projects(model=model, system1=system1, ollama_url=ollama_url, raw_cv_data=step0, job_description=job_description_summary)
    
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: {format.get("standard_calls", "")[0]}:\n" + step1)
    step1_clean = clean_first_step(step1).strip()
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step1_clean:\n" + step1_clean)
    step2_dct = augment_output(step1_clean, reference_dct, type=section)
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step2_dct:\n" + str(step2_dct))
    #helpers.filter_output()#REDUNDANT?
    step2_text = parsers.inv_parse_cv(step2_dct)
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step2_text:\n" + step2_text)
    step3_text = []
    step2_text = step2_text.replace("[0]Projects:", "")
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step2_text (No [0]):\n" + step2_text)
    #helpers.filter_output()#REDUNDANT?
    step2_text = step2_text.strip()
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step2_text after filtering:\n" + step2_text)
    step3_text = step2_text.split("[1]Project Title: ")[1:]
    step3_text = ["[1]Project Title: " + exp for exp in step3_text]
    step3_list = []
    for exp in step3_text:
        if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step3_text(loop): exp:\n" + exp)
        #Transform to dict
        #helpers.filter_output(exp).strip()#REDUNDANT?
        exp_dict = parsers.parse_subfields(exp.strip())
        #Separate dict in two: one containing description and skills, the other containing the rest
        first_part_dict = {k: v for k, v in exp_dict.items() if k in ["description", "skills"]}
        second_part_dict = {k: v for k, v in exp_dict.items() if k not in ["description", "skills"]}
        #Convert to text
        first_part_text = parsers.inv_parse_subfields(first_part_dict).strip()
        second_part_text = parsers.inv_parse_subfields(second_part_dict).strip()
        if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step3_text(loop): exp: first_part_text:\n" + first_part_text)
        if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step3_text(loop): exp: second_part_text:\n" + second_part_text)
        
        runtime_info_temp = {"call_id": format["standard_calls"][1],
                          "ollama_url": ollama_url,
                          "format": {
                              "experience": first_part_text,
                              "job_description": job_description_summary,
                          },
                          "payload_in":{
                              "system":system2,
                              "model": payload_in["model"]
                          }       
        }    
        first_part_text_new = ollama_call(runtime_info = runtime_info_temp)

        #first_part_text_new = step3_projects(model=model, system2=system2, ollama_url=ollama_url, experience=first_part_text, job_description=job_description_summary)
        if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step3_text(loop): exp: {format.get("standard_calls", "")[1]}: first_part_text_new:\n" + first_part_text_new)
        #helpers.filter_output()#REDUNDANT?
        first_part_text_new = first_part_text_new.strip()
        if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step3_text(loop): exp: {format.get("standard_calls", "")[1]}: first_part_text_new (filtered):\n" + first_part_text_new)
        #Join with second part
        temp = second_part_text + "\n" + first_part_text_new
        if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step3_text(loop): exp: {format.get("standard_calls", "")[1]}: temp(joined):\n" + temp)
        step3_list.append(temp)
    step3_text = "\n".join(step3_list)
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step3_text:\n" + step3_text)
    step4_text = "[0]Projects:\n" + step3_text
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step4_text (before filtering):\n" + step4_text)
    #helpers.filter_output()#REDUNDANT?
    step4_text = step4_text.strip()
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step4_text (after filtering):\n" + step4_text)
    return step4_text

@log_time #USED IN MAIN
def prune_experiences(call_info = template_call_info):
    
    call_id = call_info["call_id"]
    payload_in = call_info["payload_in"]
    format = call_info["format"]
    prompt_in = call_info["prompt_in"]
    ollama_url = call_info["ollama_url"]
    function_name = helpers.inspect_function()
    if call_id != function_name:
        if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: call_id {call_id} is not {function_name}")
        return f"[ERROR][OLLAMA]{function_name}: call_id {call_id} is not {function_name}"
    experiences = format["experiences"]
    job_description_summary = format["job_description_summary"]
    section = format["section"]
    reference_dct = format["reference_dct"]

    #Original Arguments: model=DEFAULT_MODEL, system1="", ollama_url=DEFAULT_URL, 
                   #experiences="", job_description_summary="", section="vl_w_p", reference_dct={}
    system1 = payload_in.get("system","")

    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: experiences:\n" + experiences)
    step0 = prepare_input_text(experiences, type=section)
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step0:\n" + step0)

    runtime_info_temp = {"call_id": format["standard_calls"][0],
                          "ollama_url": ollama_url,
                          "format": {
                              "experiences": step0,
                              "job_description": job_description_summary,
                          },
                          "payload_in":{
                              "system":system1,
                              "model": payload_in["model"]
                          }               
    }
    step1 = ollama_call(runtime_info= runtime_info_temp)
    #step1 = step0_prune_experiences(model=model, system1=system1, ollama_url=ollama_url, experiences=step0, job_description=job_description_summary)
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step1:\n" + step1)
    step1_clean = clean_first_step(step1).strip()
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step1_clean:\n" + step1_clean)
    step2_dct = augment_output(step1_clean, reference_dct, type=section)
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step2_dct:\n" + str(step2_dct))
    #helpers.filter_output()#REDUNDANT?
    step2_text = parsers.inv_parse_cv(step2_dct)
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step2_text:\n" + step2_text)
    return step2_text

@log_time
def generate_call_infos_summarize_section(sections, section_names, systems, model=DEFAULT_MODEL, ollama_url=DEFAULT_URL):
    function_name = helpers.inspect_function()
    if len(sections) != len(section_names) or len(section_names) != len(systems) or len(systems) != len(sections):
        raise ValueError(f"[ERROR]{function_name}: lenght mismatch len(sections) = {len(sections)}, len(section_names) = {len(section_names)}, len(systems) = {len(systems)}")
    call_infos = []
    requests = len(sections)
    for i in range(requests):
        prompt = f"""[REQUEST]
Given a section from a resume, summarize the sections in a wholistic manner while following these guidelines:
- Be very concise but detail-driven, which means that you must include as many relevant details as possible with minimal fluff.
- Include all information, competencies, achievements, and skills, this is a wholistic summary of the candidate's qualifications.
- Return the summarized information as a single continuous string of text, following the output format strictly. 
- Do not forget to include the field names at the start of each line, as per the OUTPUT FORMAT.
- Return the requested information, strictly filling out the OUTPUT FORMAT.

[OUTPUT FORMAT]
Section Summary: {section_names[i]} Summary; Wholistic summary of the section's information.


[INPUT]
INPUT section from a resume:
{sections[i]}


"""
        if config.DEBUG["TOKEN_LOGGING"]: input_tks = helpers.token_math(model, prompt)
        call_info = {
            "call_id": "standard_async",
            "payload_in": {
                "model": systems[i],
                "system": "",
                }, 
            "format":{
            },
            "prompt_in": prompt,
            "ollama_url":  ollama_url,
        }
        call_infos.append(call_info)
    return call_infos

@log_time
def sliding_window_two_sections(call_info = template_call_info):
    
    call_id = call_info["call_id"]
    payload_in = call_info["payload_in"]
    format = call_info["format"]
    prompt_in = call_info["prompt_in"]
    ollama_url = call_info["ollama_url"]
    function_name = helpers.inspect_function()
    if call_id != function_name:
        if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: call_id {call_id} is not {function_name}")
        return f"[ERROR][OLLAMA]{function_name}: call_id {call_id} is not {function_name}"
    
    sections = format["sections"]
    section_names = format["section_names"]
    systems=format["systems"]
    mode =format["mode"]
    candidate_name = format["candidate_name"]
    candidate_title = format["candidate_title"]

    #Original Aurguments: section1 = "", section2 ="", 
                        # model=DEFAULT_MODEL, system1="", system2="", system = "", 
                        # ollama_url=DEFAULT_URL,
                        # section1_name = "", section2_name = "", 
                        # candidate_name = "", candidate_title = "", 
                        # mode = "single"
    if CONFIG["SUMMARY_REQUESTS"] > 2:
        if config.DEBUG["WARNING_LOGGING"]: logging.warning(f"[WARNING][OLLAMA]{function_name}: number of requests SUMMARY_REQUESTS exceeds sliding window size, using maximum possible request number (2)")
    if CONFIG["SUMMARY_REQUESTS"] < 0:
        return f"[ERROR][OLLAMA]{function_name}: number of requests SUMMARY_REQUESTS must be a positive integer"

    summaries = []
    if mode == "single":
        for i in range(0, 2):
                runtime_info_temp = {
                    "call_id": format["standard_calls"][0],
                    "payload_in":{
                        "model": payload_in["model"],
                        "system": systems[i]
                    },
                    "format": {
                        "section": sections[i],
                        "section_name": section_names[i]
                    },
                    "ollama_url":ollama_url
                }
                summary = ollama_call(runtime_info=runtime_info_temp)
                #helpers.filter_output(summary.strip(), mode= "cap_letters")#REDUNDANT?
                summaries.append(summary.strip())
    elif mode == "batch":
        runtime_info_temp = {
                    "call_id": format["non_standard_calls"][0],
                    "payload_in":{
                        "model": payload_in["model"],
                        "system": systems[0]
                    },
                    "format": {
                        "sections": sections,
                        "section_names": section_names
                    },
                    "ollama_url":ollama_url
                }
        ollama_func_name = format["non_standard_calls"][0] 
        summaries_raw = ollama_call(runtime_info=runtime_info_temp, function=globals()[ollama_func_name])
        #helpers.filter_output(summaries_raw.strip(), mode= "cap_letters")#REDUNDANT?
        summaries = summaries_raw.strip().split("\n")
    elif mode == "parallel":
        runtime_info_temps = generate_call_infos_summarize_section(sections=sections, section_names=section_names, systems=systems, model=payload_in["model"], ollama_url=ollama_url)
        ollama_func_name = format["async_calls"][0]
        responses = asyncio.run(ollama_call_async(runtime_infos=runtime_info_temps, function=globals()[ollama_func_name]))
        summaries=[]
        for response in responses:
            #helpers.filter_output(response.strip(), mode="cap_letters")#REDUNDANT?
            summaries.append(response.strip())
    summary1 = summaries[0] if len(summaries) > 0 else ""
    summary2 = summaries[1] if len(summaries) > 1 else ""
    formatting = {
        "summary1": summary1,
        "summary2": summary2,
        "candidate_name": candidate_name,
        "candidate_title": candidate_title,
        "section1_name":section_names[0],
        "section2_name":section_names[1]
    }
    helpers.missing_format_pieces(prompt_in,formatting)
    prompt = prompt_in.format(**formatting)
    prompt = helpers.process_input(prompt)
    payload = payload_in.copy()
    payload["prompt"] = prompt
    
    if config.DEBUG["TOKEN_LOGGING"]: input_tks = helpers.token_math(payload["model"], payload["prompt"])
    for field in ["model", "system", "prompt", "stream", "temperature"]:
        value = payload.get(field, None)
        if value is not None:
            if config.DEBUG["INFO_LOGGING"]: logging.info(f"[OLLAMA]{function_name}: payload field {field} with value {value} found")
        else:
            if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: payload field {field} is missing or is NoneType")
            return f"[ERROR][OLLAMA]{function_name}: payload field {field} is missing or is NoneType"
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        if response.status_code == 400:
            if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: Bad Request: Payload={payload}, Response={result}")
            return f"[ERROR][OLLAMA]{function_name}: Ollama status_code 400"    
        response_text = result.get("response", "")
        if config.DEBUG["TOKEN_LOGGING"]: output_tks = helpers.token_math(payload["model"], response_text, type="output", offset=input_tks)
        if config.DEBUG["INFO_LOGGING"]: print(f"[SUCCESS][OLLAMA]{function_name}: {result}")
        return response_text
    except requests.exceptions.JSONDecodeError as e:
        error_trace =  helpers.traceback_error(e)
        if config.DEBUG["ERROR_LOGGING"]: 
            logging.error("[ERROR][OLLAMA]Traceback:")
            logging.error(f"{error_trace}")
            logging.error(f"[ERROR][OLLAMA]{function_name}: Ollama response was not valid JSON", exc_info=True)
            logging.error(f"[ERROR][OLLAMA]{function_name}: Response text: {response.text}")
        return f"[ERROR][OLLAMA]{function_name}: Ollama response was not valid JSON"

@log_time
def sliding_window_three_sections(call_info = template_call_info):
    call_id = call_info["call_id"]
    payload_in = call_info["payload_in"]
    format = call_info["format"]
    prompt_in = call_info["prompt_in"]
    ollama_url = call_info["ollama_url"]
    function_name = helpers.inspect_function()
    if call_id != function_name:
        if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: call_id {call_id} is not {function_name}")
        return f"[ERROR][OLLAMA]{function_name}: call_id {call_id} is not {function_name}"
    sections = format["sections"]
    section_names = format["section_names"]
    systems=format["systems"]
    mode =format["mode"]
    candidate_name = format["candidate_name"]
    candidate_title = format["candidate_title"]

    #Original Arguments: section1 = "", section2 = "", section3 = "", 
                       # model=DEFAULT_MODEL, system1="", system2="", system3="", system = "", ollama_url=DEFAULT_URL,
                       # section1_name = "", section2_name = "", section3_name = "", 
                       # candidate_name = "", candidate_title = "", mode = "single"
    if CONFIG["SUMMARY_REQUESTS"] > 3:
        if config.DEBUG["WARNING_LOGGING"]: warnings.warn("[WARNING]sliding_window_three_sections: number of requests exceeds sliding window size, using maximum possible request number (3)")
    if CONFIG["SUMMARY_REQUESTS"] < 0:
        raise ValueError("[ERROR]sliding_window_three_sections: SUMMARY_REQUESTS must be a positive integer")

    summaries = []
    for i in range(0, 3, CONFIG["SUMMARY_REQUESTS"]):
        if mode == "single":
            for j in range(0,CONFIG["SUMMARY_REQUESTS"]):
                if i+j >= 3:
                    break
                else:
                    runtime_info_temp = {
                        "call_id": format["standard_calls"][0],
                        "payload_in":{
                            "model": payload_in["model"],
                            "system": systems[i+j]
                        },
                        "format": {
                            "section": sections[i+j],
                            "section_name": section_names[i+j]
                        },
                        "ollama_url":ollama_url
                    }
                    summary = ollama_call(runtime_info=runtime_info_temp)
                    #helpers.filter_output(summary.strip(), mode= "cap_letters")#REDUNDANT?
                    summaries.append(summary.strip())
        if mode == "batch":
            upper_bound = i + CONFIG["SUMMARY_REQUESTS"]
            if upper_bound > 3:
                upper_bound = 3
            runtime_info_temp = {
                "call_id": format["non_standard_calls"][0],
                "payload_in":{
                    "model": payload_in["model"],
                    "system": systems[0]
                },
                "format": {
                    "sections": sections[i:upper_bound],
                    "section_names": section_names[i:upper_bound]
                },
                "ollama_url":ollama_url
            }
            ollama_func_name = format["non_standard_calls"][0] 
            summaries_raw = ollama_call(runtime_info=runtime_info_temp, function=globals()[ollama_func_name])
            #helpers.filter_output(summary.strip(), mode= "cap_letters")#REDUNDANT?
            raw_summaries_list = summaries_raw.strip().split("\n")
            for sum in raw_summaries_list:

                summaries.append(sum.strip())
            if upper_bound == 3:
                break
        if mode == "parallel":
            upper_bound = i + CONFIG["SUMMARY_REQUESTS"]
            if upper_bound > 3:
                upper_bound = 3
            runtime_info_temps = generate_call_infos_summarize_section(sections=sections[i:upper_bound], section_names=section_names[i:upper_bound], systems=systems[i:upper_bound], model=payload_in["model"], ollama_url=ollama_url)
            ollama_func_name = format["async_calls"][0]
            responses = asyncio.run(ollama_call_async(runtime_infos=runtime_info_temps, function=globals()[ollama_func_name]))
            for response in responses:
                #helpers.filter_output(response.strip(), mode= "cap_letters")#REDUNDANT?
                summaries.append(response.strip())
            if upper_bound == 3:
                break

    summary1 = summaries[0] if len(summaries) > 0 else ""
    summary2 = summaries[1] if len(summaries) > 1 else ""
    summary3 = summaries[2] if len(summaries) > 2 else ""
    formatting = {
        "summary1": summary1,
        "summary2": summary2,
        "summary3": summary3,
        "candidate_name": candidate_name,
        "candidate_title": candidate_title,
        "section1_name":section_names[0],
        "section2_name":section_names[1],
        "section3_name":section_names[2]
    }
    helpers.missing_format_pieces(prompt_in,formatting)
    prompt = prompt_in.format(**formatting)
    prompt = helpers.process_input(prompt)
    payload = payload_in.copy()
    payload["prompt"] = prompt
    if config.DEBUG["TOKEN_LOGGING"]: input_tks = helpers.token_math(payload["model"], payload["prompt"])
    for field in ["model", "system", "prompt", "stream", "temperature"]:
        value = payload.get(field, None)
        if value is not None:
            if config.DEBUG["INFO_LOGGING"]: logging.info(f"[OLLAMA]{function_name}: payload field {field} with value {value} found")
        else:
            if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: payload field {field} is missing or is NoneType")
            return f"[ERROR][OLLAMA]{function_name}: payload field {field} is missing or is NoneType"
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        if response.status_code == 400:
            if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: Bad Request: Payload={payload}, Response={result}")
            return f"[ERROR][OLLAMA]{function_name}: Ollama status_code 400"    
        response_text = result.get("response", "")
        if config.DEBUG["TOKEN_LOGGING"]: output_tks = helpers.token_math(payload["model"], response_text, type="output", offset=input_tks)
        if config.DEBUG["INFO_LOGGING"]: print(f"[SUCCESS][OLLAMA]{function_name}: {result}")
        return response_text
    except requests.exceptions.JSONDecodeError as e:
        error_trace =  helpers.traceback_error(e)
        if config.DEBUG["ERROR_LOGGING"]: 
            logging.error("[ERROR][OLLAMA]Traceback:")
            logging.error(f"{error_trace}")
            logging.error(f"[ERROR][OLLAMA]{function_name}: Ollama response was not valid JSON", exc_info=True)
            logging.error(f"[ERROR][OLLAMA]{function_name}: Response text: {response.text}")
        return f"[ERROR][OLLAMA]{function_name}: Ollama response was not valid JSON"

@log_time
def sliding_window_four_sections(call_info = template_call_info):
    call_id = call_info["call_id"]
    payload_in = call_info["payload_in"]
    format = call_info["format"]
    prompt_in = call_info["prompt_in"]
    ollama_url = call_info["ollama_url"]
    function_name = helpers.inspect_function()
    if call_id != function_name:
        if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: call_id {call_id} is not {function_name}")
        return f"[ERROR][OLLAMA]{function_name}: call_id {call_id} is not {function_name}"
    sections = format["sections"]
    section_names = format["section_names"]
    systems=format["systems"]
    mode =format["mode"]
    candidate_name = format["candidate_name"]
    candidate_title = format["candidate_title"]

    #Original Arguments: section1="", section2="", section3="", section4="",
                        #model=DEFAULT_MODEL,
                        #system1="", system2="", system3="", system4="",
                        #system="",
                        #ollama_url=DEFAULT_URL,
                        #section1_name="", section2_name="", section3_name="", section4_name="",
                        #candidate_name="",
                        #candidate_title="",
                        #mode="single"

    if CONFIG["SUMMARY_REQUESTS"] > 4:
        if config.DEBUG["WARNING_LOGGING"]: warnings.warn("[WARNING]sliding_window_four_sections: number of requests exceeds sliding window size, using maximum possible request number (4)")
    if CONFIG["SUMMARY_REQUESTS"] < 0:
        raise ValueError("[ERROR]sliding_window_four_sections: SUMMARY_REQUESTS must be a positive integer")

    summaries = []
    for i in range(0, 4, CONFIG["SUMMARY_REQUESTS"]):
        if mode == "single":
            for j in range(0,CONFIG["SUMMARY_REQUESTS"]):
                if i+j >= 4:
                    break
                else:
                    runtime_info_temp = {
                        "call_id": format["standard_calls"][0],
                        "payload_in":{
                            "model": payload_in["model"],
                            "system": systems[i+j]
                        },
                        "format": {
                            "section": sections[i+j],
                            "section_name": section_names[i+j]
                        },
                        "ollama_url":ollama_url
                    }
                    summary = ollama_call(runtime_info=runtime_info_temp)
                    #helpers.filter_output(summary.strip(), mode= "cap_letters")#REDUNDANT?
                    summaries.append(summary.strip())
        if mode == "batch":
            upper_bound = i + CONFIG["SUMMARY_REQUESTS"]
            if upper_bound > 4:
                upper_bound = 4
            runtime_info_temp = {
                "call_id": format["non_standard_calls"][0],
                "payload_in":{
                    "model": payload_in["model"],
                    "system": systems[0]
                },
                "format": {
                    "sections": sections[i:upper_bound],
                    "section_names": section_names[i:upper_bound]
                },
                "ollama_url":ollama_url
            }
            ollama_func_name = format["non_standard_calls"][0] 
            summaries_raw = ollama_call(runtime_info=runtime_info_temp, function=globals()[ollama_func_name])
            #helpers.filter_output(summary.strip(), mode= "cap_letters")#REDUNDANT?
            raw_summaries_list = summaries_raw.strip().split("\n")
            for sum in raw_summaries_list:
                summaries.append(sum.strip())
            if upper_bound == 4:
                break
        if mode == "parallel":
            upper_bound = i + CONFIG["SUMMARY_REQUESTS"]
            if upper_bound > 4:
                upper_bound = 4
            runtime_info_temps = generate_call_infos_summarize_section(sections=sections[i:upper_bound], section_names=section_names[i:upper_bound], systems=systems[i:upper_bound], model=payload_in["model"], ollama_url=ollama_url)
            ollama_func_name = format["async_calls"][0]
            responses = asyncio.run(ollama_call_async(runtime_infos=runtime_info_temps, function= globals()[ollama_func_name]))
            for response in responses:
                #helpers.filter_output(response.strip(), mode= "cap_letters")#REDUNDANT?
                summaries.append(response.strip())
            if upper_bound == 4:
                break

    summary1 = summaries[0] if len(summaries) > 0 else ""
    summary2 = summaries[1] if len(summaries) > 1 else ""
    summary3 = summaries[2] if len(summaries) > 2 else ""
    summary4 = summaries[3] if len(summaries) > 3 else ""
    formatting = {
        "summary1": summary1,
        "summary2": summary2,
        "summary3": summary3,
        "summary4": summary4,
        "candidate_name": candidate_name,
        "candidate_title": candidate_title,
        "section1_name":section_names[0],
        "section2_name":section_names[1],
        "section3_name":section_names[2],
        "section4_name":section_names[3]
    }
    helpers.missing_format_pieces(prompt_in,formatting)
    prompt = prompt_in.format(**formatting)
    prompt = helpers.process_input(prompt)
    payload = payload_in.copy()
    payload["prompt"] = prompt
    if config.DEBUG["TOKEN_LOGGING"]: input_tks = helpers.token_math(payload["model"], payload["prompt"])
    for field in ["model", "system", "prompt", "stream", "temperature"]:
        value = payload.get(field, None)
        if value is not None:
            if config.DEBUG["INFO_LOGGING"]: logging.info(f"[OLLAMA]{function_name}: payload field {field} with value {value} found")
        else:
            if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: payload field {field} is missing or is NoneType")
            return f"[ERROR][OLLAMA]{function_name}: payload field {field} is missing or is NoneType"
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        if response.status_code == 400:
            if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: Bad Request: Payload={payload}, Response={result}")
            return f"[ERROR][OLLAMA]{function_name}: Ollama status_code 400"    
        response_text = result.get("response", "")
        if config.DEBUG["TOKEN_LOGGING"]: output_tks = helpers.token_math(payload["model"], response_text, type="output", offset=input_tks)
        if config.DEBUG["INFO_LOGGING"]: print(f"[SUCCESS][OLLAMA]{function_name}: {result}")
        return response_text
    except requests.exceptions.JSONDecodeError as e:
        error_trace =  helpers.traceback_error(e)
        if config.DEBUG["ERROR_LOGGING"]: 
            logging.error("[ERROR][OLLAMA]Traceback:")
            logging.error(f"{error_trace}")
            logging.error(f"[ERROR][OLLAMA]{function_name}: Ollama response was not valid JSON", exc_info=True)
            logging.error(f"[ERROR][OLLAMA]{function_name}: Response text: {response.text}")
        return f"[ERROR][OLLAMA]{function_name}: Ollama response was not valid JSON"

@log_time
def slide_summary(call_info = template_call_info):
    call_id = call_info["call_id"]
    payload_in = call_info["payload_in"]
    format = call_info["format"]
    prompt_in = call_info["prompt_in"]
    ollama_url = call_info["ollama_url"]
    function_name = helpers.inspect_function()
    if call_id != function_name:
        if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: call_id {call_id} is not {function_name}")
        return f"[ERROR][OLLAMA]{function_name}: call_id {call_id} is not {function_name}"
    
    sys_len =   len(format["systems"])                     
    if  sys_len< 3:                       
        if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: sys_len {sys_len} is less than operational minimum (3)")
        return f"[ERROR][OLLAMA]{function_name}: sys_len {sys_len} is less than operational minimum (3)"                                            
    systems=format.get("systems", ["","",""])
    mode =format.get("mode", "single")
    sections_dct_list = format.get("sections_dct_list", [])
    skill_section = format.get("skill_section", False)
    windows = format.get("windows", 2)

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
    skill_txts = []
    candidate_name = ""
    candidate_title = ""
    for item in sections_dct_list:
        key = next(iter(item))
        if key == "name":
            candidate_name = item[key]
        elif key == "title":
            candidate_title = item[key]
        if key in general_keys:
            #helpers.filter_output()#REDUNDANT?
            temp = parsers.inv_parse_cv(item).strip()
            general_txts.append(temp)
        elif key in skills_key:
            #helpers.filter_output()#REDUNDANT?
            temp = parsers.inv_parse_cv_out(item).strip()
            skill_txts.append(temp)
            # skill_txt = skill_txt + temp + "\n"
        elif key in special_keys:
            if skill_section:
                #helpers.filter_output()#REDUNDANT?
                temp = parsers.inv_parse_cv_out(item).strip()
            else:
                #helpers.filter_output()#REDUNDANT?
                temp = parsers.inv_parse_cv(item).strip()
            special_txts.append(temp)
    if config.DEBUG["INFO_LOGGING"]: 
        print(f"[INFO][OLLAMA]{function_name}: candidate_name: {candidate_name}")
        print(f"[INFO][OLLAMA]{function_name}: candidate_title: {candidate_title}")
        print(f"[INFO][OLLAMA]{function_name}: general_txts: {len(general_txts)}")
        print(f"[INFO][OLLAMA]{function_name}: special_txts: {len(special_txts)}")
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
            runtime_info_temp = {
                                    "call_id": format["non_standard_calls"][0], 
                                    "payload_in": {
                                        "model": payload_in["model"],
                                        "system": payload_in["system"],
                                    },
                                    "format": {
                                        "sections" : [special_txts[i], special_txts[i + 1]],
                                        "section_names":  [special_keys[i], special_keys[i + 1]],
                                        "systems": systems[:2],
                                        "candidate_name":candidate_name,
                                        "candidate_title":candidate_title,
                                        "mode": mode, 
                                    }, 
                                    "ollama_url": ollama_url,
            }
            ollama_func_name = format["non_standard_calls"][0] 
            slide = ollama_call(runtime_info=runtime_info_temp, function=globals()[ollama_func_name])
            slide_results.append(slide)
        elif windows == 3:
            runtime_info_temp = {
                                    "call_id": format["non_standard_calls"][1], 
                                    "payload_in": {
                                        "model": payload_in["model"],
                                        "system": payload_in["system"],
                                    },
                                    "format": {
                                        "sections" : [special_txts[i], special_txts[i + 1], special_txts[i + 2]],
                                        "section_names":  [special_keys[i], special_keys[i + 1], special_keys[i + 2]],
                                        "systems": systems[:3],
                                        "candidate_name":candidate_name,
                                        "candidate_title":candidate_title,
                                        "mode": mode, 
                                    }, 
                                    "ollama_url": ollama_url,
            }
            ollama_func_name = format["non_standard_calls"][1] 
            slide = ollama_call(runtime_info=runtime_info_temp, function=globals()[ollama_func_name])
            slide_results.append(slide)
        elif windows == 4:
            runtime_info_temp = {
                                    "call_id": format["non_standard_calls"][2], 
                                    "payload_in": {
                                        "model": payload_in["model"],
                                        "system": payload_in["system"],
                                    },
                                    "format": {
                                        "sections" : [special_txts[i], special_txts[i + 1], special_txts[i + 2], special_txts[i + 3]],
                                        "section_names":  [special_keys[i], special_keys[i + 1], special_keys[i + 2], special_keys[i + 3]],
                                        "systems": systems[:4],
                                        "candidate_name":candidate_name,
                                        "candidate_title":candidate_title,
                                        "mode": mode, 
                                    }, 
                                    "ollama_url": ollama_url,
            }
            ollama_func_name = format["non_standard_calls"][2] 
            slide = ollama_call(runtime_info=runtime_info_temp, function=globals()[ollama_func_name])
            slide_results.append(slide)
    general_info = "\n".join(general_txts).strip()
    runtime_info_temp = {
        "call_id": format["standard_calls"][0],
        "payload_in": {
            "model": payload_in["model"],
            "system": systems[-1],
        },
        "format": {
            "general_info_text": general_info
        },
        "ollama_url": ollama_url
    }
    general_info_summary = ollama_call(runtime_info=runtime_info_temp) #standard call
    slide_results.insert(0, general_info_summary)
    if skill_section:
        skills_info = "\n".join(skill_txts).strip()
        runtime_info_temp = {
            "call_id": format["standard_calls"][1],
            "payload_in": {
                "model": payload_in["model"],
                "system": systems[-1],
            },
            "format": {
                "skill_section": skills_info
            },
            "ollama_url": ollama_url
        }
        skills_summary = ollama_call(runtime_info=runtime_info_temp) #standard call
        slide_results.append(skills_summary)
    return slide_results

@log_time #USED IN MAIN ; returns ERROR as text
def step0_tailor_summary(call_info = template_call_info):
    call_id = call_info["call_id"]
    payload_in = call_info["payload_in"]
    format = call_info["format"]
    prompt_in = call_info["prompt_in"]
    ollama_url = call_info["ollama_url"]
    function_name = helpers.inspect_function()
    non_standard_calls= format.get("non_standard_calls", [])
    if call_id != function_name:
        if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: call_id {call_id} is not {function_name}")
        return f"[ERROR][OLLAMA]{function_name}: call_id {call_id} is not {function_name}" 
    sys_len =   len(format["systems"])                     
    if  sys_len< 4:                       
        if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: sys_len {sys_len} is less than operational minimum (3)")
        return f"[ERROR][OLLAMA]{function_name}: sys_len {sys_len} is less than operational minimum (4)"
    
    systems=format.get("systems", ["","","",""])
    mode =format.get("mode", "single")
    raw_cv_data =format.get("raw_cv_data", "")
    skill_section = format.get("skill_section", False)
    windows = format.get("windows", 2)
    #Original Arguments: raw_cv_data = ""
                         #, system_s = "", system = "", system1 = "", system2 = "", system3 = "", system4 = "", system0 = "",
                         #windows = 2, skill_section = False, mode="single"

    if skill_section:
        sections_dct = parsers.parse_cv_out(raw_cv_data)
    else:
        sections_dct = parsers.parse_cv(raw_cv_data)
    sections_dct_list = parsers.dict_spliter(sections_dct)
    runtime_info_temp = {"call_id": non_standard_calls[0], 
                        "ollama_url": ollama_url, #ollama_url=DEFAULT_URL,
                        "payload_in": {"model": payload_in["model"], #model=DEFAULT_MODEL,
                                        "system": systems[0], # #system="",
                                        }, 
                        "format": {
                            "sections_dct_list" : sections_dct_list, #sections_dct_list=[]
                            "systems": systems[1:], #(min size: 3) system1="", system2="", system3="", system4="", system_s="",
                            "skill_section": skill_section, #skill_section=False,
                            "windows":windows, #windows=2,
                            "mode": mode, #mode="single"
                        }
                        }
    ollama_func_name = non_standard_calls[0]
    slides = ollama_call(runtime_info=runtime_info_temp, function=globals()[ollama_func_name])
    #Join slides
    slides_txt = "\n".join(slides).strip()
    slides_txt_temp = {
        "slides_txt": slides_txt
    }
    helpers.missing_format_pieces(prompt_in,slides_txt_temp)
    prompt = prompt_in.format(**slides_txt_temp)
    prompt = helpers.process_input(prompt)
    payload = payload_in.copy()
    payload["prompt"] = prompt
    if config.DEBUG["TOKEN_LOGGING"]: input_tks = helpers.token_math(payload["model"], payload["prompt"])
    for field in ["model", "system", "prompt", "stream", "temperature"]:
        value = payload.get(field, None)
        if value is not None:
            if config.DEBUG["INFO_LOGGING"]: logging.info(f"[OLLAMA]{function_name}: payload field {field} with value {value} found")
        else:
            if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: payload field {field} is missing or is NoneType")
            return f"[ERROR][OLLAMA]{function_name}: payload field {field} is missing or is NoneType"
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        if response.status_code == 400:
            if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: Bad Request: Payload={payload}, Response={result}")
            return f"[ERROR][OLLAMA]{function_name}: Ollama status_code 400"    
        response_text = result.get("response", "")
        if config.DEBUG["TOKEN_LOGGING"]: output_tks = helpers.token_math(payload["model"], response_text, type="output", offset=input_tks)
        if config.DEBUG["INFO_LOGGING"]: print(f"[SUCCESS][OLLAMA]{function_name}: {result}")
        return response_text
    except requests.exceptions.JSONDecodeError as e:
        error_trace =  helpers.traceback_error(e)
        if config.DEBUG["ERROR_LOGGING"]: 
            logging.error("[ERROR][OLLAMA]Traceback:")
            logging.error(f"{error_trace}")
            logging.error(f"[ERROR][OLLAMA]{function_name}: Ollama response was not valid JSON", exc_info=True)
            logging.error(f"[ERROR][OLLAMA]{function_name}: Response text: {response.text}")
        return f"[ERROR][OLLAMA]{function_name}: Ollama response was not valid JSON"

@log_time #USED IN MAIN
def tailor_summary(call_info = template_call_info):
    call_id = call_info["call_id"]
    payload_in = call_info["payload_in"]
    format = call_info["format"]
    prompt_in = call_info["prompt_in"]
    ollama_url = call_info["ollama_url"]
    function_name = helpers.inspect_function()
    if call_id != function_name:
        if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: call_id {call_id} is not {function_name}")
        return f"[ERROR][OLLAMA]{function_name}: call_id {call_id} is not {function_name}" 
    sys_len =   len(format["systems"])                     
    if  sys_len< 6:                       
        if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: sys_len {sys_len} is less than operational minimum (6)")
        return f"[ERROR][OLLAMA]{function_name}: sys_len {sys_len} is less than operational minimum (6)"                                            

    #Original Arguments: model=DEFAULT_MODEL, ollama_url=DEFAULT_URL,
                        #raw_cv_data="", job_description="",
                        #system_s="", system00="", system1="", system2="", system3="", system4="", system0="", windows=2,
                        #system01="", mode="single"
    systems = format.get("systems", ["","","","","","",])#min 6
    raw_cv_data = format.get("raw_cv_data", "")
    job_description = format.get("job_description", "")
    windows = format.get("windows", 2)
    skill_section = format.get("skill_section", False)
    mode = format.get("mode", "single")

    print(f"tailor_summary: raw_cv_data:\n" + raw_cv_data)
    runtime_info_temp = {
        "call_id":format["non_standard_calls"][0],
        "payload_in":{
            "model": payload_in["model"],
            "system": systems[-2]
        },
        "format":{
            "raw_cv_data": raw_cv_data,
            "windows": windows,
            "mode": mode,
            "skill_section": skill_section,
            "systems": systems[:-2]
        },
        "ollama_url":ollama_url
    }
    ollama_func_name = format["non_standard_calls"][0] 
    step0 = ollama_call(runtime_info = runtime_info_temp, function= globals()[ollama_func_name])
    runtime_info_temp = {
        "call_id":format["standard_calls"][0],
        "payload_in":{
            "model": payload_in["model"],
            "system": systems[-1]
        },
        "format":{
            "prev_summary": step0,
            "job_description": job_description
        },
        "ollama_url":ollama_url
    }
    step1 = ollama_call(runtime_info = runtime_info_temp)
    return step1.strip()

@log_time
def new_vs_old_resume(call_info=template_call_info):
    call_id = call_info["call_id"]
    payload_in = call_info["payload_in"]
    format = call_info["format"]
    prompt_in = call_info["prompt_in"]
    ollama_url = call_info["ollama_url"]
    function_name = helpers.inspect_function()
    if call_id != function_name:
        if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: call_id {call_id} is not {function_name}")
        return f"[ERROR][OLLAMA]{function_name}: call_id {call_id} is not {function_name}" 


    old_resume_txt0 = return_text_with_skills(format["old_resume_txt"])
    #helpers.filter_output()#REDUNDANT?
    old_dct = parsers.parse_cv_out(old_resume_txt0.strip())
    section_names= []
    for key in old_dct:
        section_names.append(key)
    old_dcts = parsers.dict_spliter(old_dct)
    #helpers.filter_output(format["new_resume_txt"].strip())#REDUNDANT?
    new_dcts = parsers.dict_spliter(parsers.parse_cv_out(format["new_resume_txt"].strip()))
    old_txts = [parsers.inv_parse_cv_out(dct).strip() for dct in old_dcts]
    new_txts = [parsers.inv_parse_cv_out(dct).strip() for dct in new_dcts]
    analysis_txts = []
    print("Length of old_txts:", len(old_txts))
    print("Length of new_txts:", len(new_txts))
    if len(old_txts) != len(new_txts):
        raise ValueError("The number of sections in the old and new resumes do not match.")
    for i in range(len(old_txts)):
        runtime_info_temp = {
            "call_id": format["standard_calls"][0], 
            "payload_in": {
                        "model": payload_in["model"], #Set at runtime
                        "system": payload_in["system"] #Set at runtime
                        },
            "format": {#Set at runtime
                        "old_resume_s_txt": old_txts[i],
                        "new_resume_s_txt": new_txts[i],
                        "section_name": section_names[i]
                    },
            "ollama_url": ollama_url, #Set at runtime
        }
        analysis_txt = ollama_call(runtime_info=runtime_info_temp)
        analysis_txts.append(analysis_txt)
    return analysis_txts

@log_time #USED IN MAIN
def consistency_checker_vs_cv_cv(call_info = template_call_info):
    call_id = call_info["call_id"]
    payload_in = call_info["payload_in"]
    format = call_info["format"]
    prompt_in = call_info["prompt_in"]
    ollama_url = call_info["ollama_url"]
    function_name = helpers.inspect_function()
    if call_id != function_name:
        if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: call_id {call_id} is not {function_name}")
        return f"[ERROR][OLLAMA]{function_name}: call_id {call_id} is not {function_name}" 
    
    #Chain: old resume, new resume >>> new_vs_old_section >>> consistency_checker_vs_cv
    runtime_info_temp = {
        "call_id": format["non_standard_calls"][0], 
        "payload_in": {"model": payload_in["model"], #model=DEFAULT_MODEL,
                        "system": format["system_s"], # #system="",
        },
        "format": {
            "old_resume_txt" : format["cv_data_orig"], #old_resume_txt = ""
            "new_resume_txt": format["cv_data"] # new_resume_txt = ""
        }, 
        "ollama_url": ollama_url, #ollama_url=DEFAULT_URL,
    }
    ollama_func_name = format["non_standard_calls"][0] 
    text_analysis = ollama_call(runtime_info = runtime_info_temp, function= globals()[ollama_func_name])
    #Join the analysis texts into a single string
    all_analysis = "\n".join(text_analysis).strip()
    all_analysis_dct = {
        "all_analysis": all_analysis
    }
    helpers.missing_format_pieces(prompt_in,all_analysis_dct)
    prompt = prompt_in.format(**all_analysis_dct)
    prompt = helpers.process_input(prompt)
    payload = payload_in.copy()
    payload["prompt"] = prompt
    if config.DEBUG["TOKEN_LOGGING"]: input_tks = helpers.token_math(payload["model"], payload["prompt"])
    for field in ["model", "system", "prompt", "stream", "temperature"]:
        value = payload.get(field, None)
        if value is not None:
            if config.DEBUG["INFO_LOGGING"]: logging.info(f"[OLLAMA]{function_name}: payload field {field} with value {value} found")
        else:
            if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: payload field {field} is missing or is NoneType")
            return f"[ERROR][OLLAMA]{function_name}: payload field {field} is missing or is NoneType"
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    try:
        result = response.json()
        if response.status_code == 400:
            if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: Bad Request: Payload={payload}, Response={result}")
            return f"[ERROR][OLLAMA]{function_name}: Ollama status_code 400"    
        response_text = result.get("response", "")
        if config.DEBUG["TOKEN_LOGGING"]: output_tks = helpers.token_math(payload["model"], response_text, type="output", offset=input_tks)
        if config.DEBUG["INFO_LOGGING"]: print(f"[SUCCESS][OLLAMA]{function_name}: {result}")
        return response_text
    except requests.exceptions.JSONDecodeError as e:
        error_trace =  helpers.traceback_error(e)
        if config.DEBUG["ERROR_LOGGING"]: 
            logging.error("[ERROR][OLLAMA]Traceback:")
            logging.error(f"{error_trace}")
            logging.error(f"[ERROR][OLLAMA]{function_name}: Ollama response was not valid JSON", exc_info=True)
            logging.error(f"[ERROR][OLLAMA]{function_name}: Response text: {response.text}")
        return f"[ERROR][OLLAMA]{function_name}: Ollama response was not valid JSON"

    
@log_time #USED IN MAIN
def compose_cover_letter_dictionary(call_info = template_call_info):
    """
    Given a resume containing education, experiences, projects and skills considered 
    to be relevant a job description: Return a cover letter tailored to the job description.
    """
    call_id = call_info["call_id"]
    payload_in = call_info["payload_in"]
    format = call_info["format"]
    prompt_in = call_info["prompt_in"]
    ollama_url = call_info["ollama_url"]
    function_name = helpers.inspect_function()

    cv_text = format["cv_text"]

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
    runtime_info_temp = {
        "call_id": format["standard_calls"][0],
        "payload_in": {
            "model": payload_in["model"],
            "system": system,
        },
        "format": {
            "cv_data": format["cv_text_summary"],
            "job_description": format["job_description"]
        },
        "ollama_url": ollama_url,
    }
    cover_letter_text = ollama_call(runtime_info=runtime_info_temp) #Standard, no need to state function

    #clean_cover_letter_text = helpers.filter_output(cover_letter_text)#REDUNDANT?
    
    clean_cover_letter_dict = parsers.parse_cl(cover_letter_text)
    
    #Make a list of dicts with name, title, languages, contact_info and clean_cover_letter_dict
    dict_list = [name,title,languages,contact_info,clean_cover_letter_dict]
    output_dict = parsers.dict_grafter(dict_list)
    #Return the output_dict
    return output_dict  
#endregion

#region ASYNC OLLAMA CALLS
async def standard_ollama_call_async(session, retries = config.CONFIG["MODELS"]["RETRIES"],call_info = template_call_info):
    call_id = call_info["call_id"]
    payload_in = call_info["payload_in"]
    format = call_info["format"]
    prompt_in = call_info["prompt_in"]
    ollama_url = call_info["ollama_url"]
    sample_starts = call_info["sample_starts"]
    function_name = helpers.inspect_function()
    if call_id not in payloads.ASYNC:
        return f"[ERROR][OLLAMA][ASYNC]{function_name}: call_id {call_id} not found in ASYNC payloads"
    if format != {}:
        helpers.missing_format_pieces(prompt_in,format)
        prompt = prompt_in.format(**format)
        prompt = helpers.process_input(prompt)
    else:
        prompt = prompt_in
        prompt = helpers.process_input(prompt)
    payload = payload_in.copy()
    payload["prompt"] = prompt
    # Check payload fields
    for field in ["model", "system", "prompt", "stream", "temperature"]:
        value = payload.get(field, None)
        if value is None:
            return f"[ERROR][OLLAMA][ASYNC]{function_name}: payload field {field} is missing or is NoneType"
    for i in range(retries):
        async with session.post(f"{ollama_url}/api/generate", json=payload) as resp:
            try:
                data = await resp.json()
                if resp.status == 400:
                    continue
                    #return f"[ERROR][OLLAMA][ASYNC]{function_name}: Ollama status_code 400"    
                response_text =  data.get("response", "")
                if payload["sample_starts"] != []:
                    response = helpers.filter_output(response, format["prefix_dict"] )#sample_starts[1],
                    if compare_start_nb(response, sample_starts["sample_starts"]) == False:
                        continue         
                return response_text
            except aiohttp.ContentTypeError as e:
                continue
    return f"[ERROR][OLLAMA][ASYNC]{function_name}: All retries exhausted."
#endregion

#region MAIN CALL HANDLERS
@log_time
def ollama_call(retries=config.CONFIG["MODELS"]["RETRIES"], runtime_info = {}, function = standard_ollama_call):

    function_name = helpers.inspect_function()
    response = ""
    if retries < 1:
        if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: retries is less than 1")
        raise ValueError(f"[ERROR][OLLAMA]{function_name}: retries is less than 1")
    if runtime_info == {}:
        if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: runtime_info is empty dict")
        raise ValueError(f"[ERROR][OLLAMA]{function_name}: runtime_info is empty dict")
    if "call_id" not in runtime_info:
        if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: call_id is missing")
        raise ValueError("[ERROR][OLLAMA]{function_name}: call_id is missing")
    if runtime_info.get("call_id", "") == "":
        if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: call_id is empty")
        raise ValueError(f"[ERROR][OLLAMA]{function_name}: call_id is empty")
    call_info = fetch_complete_call_info(call_id=runtime_info["call_id"], runtime_info=runtime_info)
    #For standard calls: "call_id": "", "model": DEFAULT_MODEL, "system": "", "format": {} , "ollama_url": DEFAULT_URL need to be set
    for i in range(retries):
        if config.DEBUG["INFO_LOGGING"]: logging.info(f"[INFO][OLLAMA]{function_name}: Try {i+1}/{retries}...")
        try:
            #sample_starts key is unneeded, only useful for comparison and QA
            response =function(call_info)
            if isinstance(response,str):
                if config.DEBUG["INFO_LOGGING"]: logging.info(f"[INFO][OLLAMA]{function_name}: response is a str")
                if response.startswith("[ERROR]"):
                    if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: Ollama call returned error: {response}. Retrying {i+1}/{retries}...")
                    continue
                if call_info["sample_starts"] != []:
                    response = helpers.filter_output(response, call_info["format"]["prefix_dict"])#call_info["sample_starts"][1]
                    if config.DEBUG["INFO_LOGGING"]: logging.info(f"[INFO][OLLAMA]{function_name}: filtered response: {response}")
                    if compare_start(response, call_info["sample_starts"]) == False:
                        if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: Output does not match expected start lines or output length. Retrying {i+1}/{retries}...")
                        continue
                if config.DEBUG["INFO_LOGGING"]: logging.info(f"[SUCCESS][OLLAMA]{function_name}: Ollama call succeeded: {response}")
                return response
            elif isinstance(response,list):
                if config.DEBUG["INFO_LOGGING"]: logging.info(f"[INFO][OLLAMA]{function_name}: response is a list")
                for element in response:
                    #Assume is list of strings
                    if element.startswith("[ERROR]"):
                        if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: Ollama call returned error: {element}. Retrying {i+1}/{retries}...")
                        continue
                    if call_info["sample_starts"] != []:
                        element = helpers.filter_output(element, call_info["format"]["prefix_dict"])#call_info["sample_starts"][1]
                        if config.DEBUG["INFO_LOGGING"]: logging.info(f"[INFO][OLLAMA]{function_name}: filtered element: {element}")
                        if compare_start(element, call_info["sample_starts"]) == False:
                            if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: Output does not match expected start lines or output length. Retrying {i+1}/{retries}...")
                            continue
                    if config.DEBUG["INFO_LOGGING"]: logging.info(f"[SUCCESS][OLLAMA]{function_name}: Ollama call succeeded: {element}")
                return response
            elif isinstance(response,dict):
                if config.DEBUG["INFO_LOGGING"]: logging.info(f"[INFO][OLLAMA]{function_name}: response is a dict")
                if config.DEBUG["INFO_LOGGING"]: logging.info(f"[INFO][OLLAMA]{function_name}: assuming correctness check happens in other instances of ollama_call")
                return response


        except Exception as e:
            error_trace =  helpers.traceback_error(e)
            if config.DEBUG["ERROR_LOGGING"]: 
                logging.error("[ERROR][OLLAMA]Traceback:")
                logging.error(f"{error_trace}")
                logging.error(f"[ERROR][OLLAMA]{function_name}: {e}")
                logging.error(f"[ERROR][OLLAMA]{function_name}: Exception occurred during Ollama call. Retrying {i+1}/{retries}...")
            continue
    if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: All retries exhausted. Returning last response.")
    raise ValueError(f"[ERROR][OLLAMA]{function_name}: All retries exhausted.")
   
async def ollama_call_async(retries=config.CONFIG["MODELS"]["RETRIES"], runtime_infos = [], function = standard_ollama_call_async ):
    function_name = helpers.inspect_function()
    if retries < 1:
       raise ValueError(f"[ERROR][OLLAMA][ASYNC]{function_name}: retries is less than 1")
    if runtime_infos == []:
        raise ValueError (f"[ERROR][OLLAMA][ASYNC]{function_name}: runtime_infos is empty list")
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(len(runtime_infos)):
            runtime_info = runtime_infos[i].copy()
            if "call_id" not in runtime_info:
                raise ValueError(f"[ERROR]{function_name}: missing call_id")
            if runtime_info.get("call_id", "") == "":
                raise ValueError(f"[ERROR]{function_name}: empty call_id")
            call_info = fetch_complete_call_info(call_id=runtime_info["call_id"], runtime_info=runtime_info)
            # payload["prompt"] = f"Prompt {i+1}"  
            tasks.append(function(session, retries,call_info))
        results = await asyncio.gather(*tasks)
        for result in results:
            if result.startswith("[ERROR]"):
                raise ValueError(f"[ERROR]{function_name}: error in async processing of ollama calls")
    return results
#endregion

#endregion
