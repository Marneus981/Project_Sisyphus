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
from rapidfuzz import process, fuzz, utils
import rapidfuzz
from operator import itemgetter
from copy import deepcopy

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
                parts = line.replace("[1]Skills:", "").strip().split(";")
                parts = [part.strip() for part in parts]
                    #Programming Languages: Programming Language N1, ..., Programming Language NN
                    #Technical Skills: Technical Skill N1, ..., Technical Skill N2
                    #Soft Skills: Soft Skill N1, ..., Soft Skill N2
                for part in parts:
                    if "Programming Languages:" in part:
                        skills = part.replace("Programming Languages:","").strip()
                        if skills == "":
                            print("No Programming Languages found in Skills section")
                        else:
                            skills_r = skills.split(",")
                            skills_r = [skill.strip() for skill in skills_r]
                            programming_skills += skills_r
                        # skills = part.split(":")
                        # if len(skills) > 1:
                        #     skills = [skill.strip() for skill in skills]
                        #     skills_r = skills[1].split(",")
                        #     skills_r = [skill.strip() for skill in skills_r]
                        #     programming_skills += skills_r
                        # else:
                        #     print("No Programming Languages found in Skills section")
                    elif "Technical Skills:" in part:
                        skills = part.replace("Technical Skills:","").strip()
                        if skills == "":
                            print("No Technical Skills found in Skills section")
                        else:
                            skills_r = skills.split(",")
                            skills_r = [skill.strip() for skill in skills_r]
                            technical_skills += skills_r
                        # skills = part.split(":")
                        # if len(skills) > 1:
                        #     skills = [skill.strip() for skill in skills]
                        #     skills_r = skills[1].split(",")
                        #     skills_r = [skill.strip() for skill in skills_r]
                        #     technical_skills += skills_r
                        # else:
                        #     print("No Technical Skills found in Skills section")
                    elif "Soft Skills:" in part:
                        skills = part.replace("Soft Skills:","").strip()
                        if skills == "":
                            print("No Soft Skills found in Skills section")
                        else:
                            skills_r = skills.split(",")
                            skills_r = [skill.strip() for skill in skills_r]
                            soft_skills += skills_r
                        # skills = part.split(":")
                        # if len(skills) > 1:
                        #     skills = [skill.strip() for skill in skills]
                        #     skills_r = skills[1].split(",")
                        #     skills_r = [skill.strip() for skill in skills_r]
                        #     soft_skills += skills_r
                        # else:
                        #     print("No Soft Skills found in Skills section")

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
        "sections_text": sections_text,
        "section_names": ', '.join(section_names),
        "no_sections": len(section_names)
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
    
    prompt = prompt_in.format(**format)
    prompt = helpers.process_input(prompt)
    prompt = prompt + "OUTPUT FORMAT:\n"
    for name in section_names:
        prompt =prompt + f"Section Summary: This is a summary of the {name} section: Wholistic summary of the section's information.\n"

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

def process_job_desc(job_desc):
    function_name = helpers.inspect_function()
    job_lines = job_desc.splitlines()
    keywords_list = []
    for line in job_lines:
        tmp_line = line.lower()
        if "keywords:" in tmp_line:
            split_line = line.split(":",1)
            if len(split_line)>1:
                keywords = split_line[1].split(",")
                for keyword in keywords:
                    keyword = keyword.strip().lower()
                    keywords_list.append(keyword)
    if keywords_list == []:
        raise ValueError(f"[ERROR]{function_name}: 'Keywords:' field not found")
    if config.DEBUG["INFO_LOGGING"]:
        print(f"[INFO]{function_name}: keywords extracted: {str(keywords_list)}")
        # for keyw in keywords_list:
        #     print(f"keyw: {str(keyw)}")
    return keywords_list

def process_exps(exp_text):
    function_name = helpers.inspect_function()
    text = exp_text
    experiences = text.split("Experience:")
    experiences =experiences[1:]
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO]{function_name}: experiences: {str(experiences)}")
    list_exp_dcts = []
    for exp  in experiences:
        if config.DEBUG["INFO_LOGGING"]: print(f"[INFO]{function_name}: experience: {exp}")
        lines = exp.strip().splitlines()
        for line in lines:
            if config.DEBUG["INFO_LOGGING"]: print(f"[INFO]{function_name}: line: '{line}'")
        if lines[0].strip() != "":
            exp_line_temp = (lines[0].strip(),[])
        if "Description:" in lines[1]:
            desc_line_temp = (lines[1].replace("Description:","").strip(),[])
        else:
            desc_line_temp = ""
        if "Skills:" in lines[2]:
            soft = []
            tech = []
            prog = []
            skills_line_temp = lines[2].strip()
            #SOFT
            skills_line_temp_s = skills_line_temp.strip().split("Soft Skills:")
            #None if [1] is ""
            if len(skills_line_temp_s)>1:
                soft_lines = skills_line_temp_s[1].strip().split(",")
                for j in range(0,len(soft_lines)):
                        soft_lines[j] = soft_lines[j].strip()
                        if soft_lines[j] != "":
                            soft.append((soft_lines[j],[]))
            #TECH
            skills_line_temp_t = skills_line_temp_s[0].replace(";","").strip().split("Technical Skills:")
            #None if [1] is ""
            if len(skills_line_temp_t)>1:
                tech_lines = skills_line_temp_t[1].strip().split(",")
                for j in range(0,len(tech_lines)):
                        tech_lines[j] = tech_lines[j].strip()
                        if tech_lines[j] != "":
                            tech.append((tech_lines[j],[]))
            #PROG
            skills_line_temp_p = skills_line_temp_t[0].replace(";","").strip().split("Programming Languages:")
            #None if [1] is ""
            if len(skills_line_temp_p)>1:
                prog_lines = skills_line_temp_p[1].split(",")
                for j in range(0,len(prog_lines)):
                        prog_lines[j] = prog_lines[j].strip()
                        if prog_lines[j] != "":
                            prog.append((prog_lines[j],[]))
        else:
            soft = []
            tech = []
            prog = []
        temp_dct = {
            "experience":exp_line_temp,
            "description":desc_line_temp,
            "skills": {
                "programming_languages":prog,
                "technical_skills":tech,
                "soft_skills": soft
        }}
        if config.DEBUG["INFO_LOGGING"]:
            print(f"[INFO]{function_name}: experience: {temp_dct["experience"]}")
            print(f"[INFO]{function_name}: description: {temp_dct["description"]}")
            print(f"[INFO]{function_name}: skills:")
            print(f"[INFO]{function_name}: programming_languages: {str(temp_dct["skills"]["programming_languages"])}")
            print(f"[INFO]{function_name}: technical_skills: {str(temp_dct["skills"]["technical_skills"])}")
            print(f"[INFO]{function_name}: soft_skills: {str(temp_dct["skills"]["soft_skills"])}")
        list_exp_dcts.append(temp_dct)
    return list_exp_dcts


    # experiences = text.split("Experience:")
    
    # for experience in experiences:
    #     if config.DEBUG["INFO_LOGGING"]:
    #         print(f"[INFO]{function_name}: current experience: {experience}")
    #     experience_lines = experience.strip().splitlines()
    #     #Asume 3 lines
    #     skills = experience_lines[2].replace("Skills:","").strip()
    #     skill_types = skills.split(";")
    #     prog_tmp = skill_types[0].replace("Programming Languages:","").strip().split(",")
    #     prog= []
    #     for i in range(0,len(prog_tmp)):
    #         prog_tmp[i] = prog_tmp[i].strip()
    #         prog.append((prog_tmp[i],[]))
    #     tech_tmp = skill_types[1].replace("Technical Skills:","").strip().split(",")
    #     tech = []
    #     for i in range(0,len(tech_tmp)):
    #         tech_tmp[i] = tech_tmp[i].strip()
    #         tech.append((tech_tmp[i],[]))
    #     soft_tmp = skill_types[2].replace("Soft Skills:","").strip().split(",")
    #     soft = []
    #     for i in range(0,len(soft_tmp)):
    #         soft_tmp[i] = soft_tmp[i].strip()
    #         soft.append((soft_tmp[i],[]))
    #     temp_dct = {
    #         "experience":(experience_lines[0].strip(),[]),
    #         "description":(experience_lines[1].replace("Description:","").strip(),[]),
    #         "skills": {
    #             "programming_languages":prog,
    #             "technical_skills":tech,
    #             "soft_skills": soft
    #         }
    #     }
    #     if config.DEBUG["INFO_LOGGING"]:
    #         print(f"[INFO]{function_name}: experience: {temp_dct["experience"]}")
    #         print(f"[INFO]{function_name}: description: {temp_dct["description"]}")
    #         print(f"[INFO]{function_name}: skills:")
    #         print(f"[INFO]{function_name}: programming_languages: {str(temp_dct["skills"]["programming_languages"])}")
    #         print(f"[INFO]{function_name}: technical_skills: {str(temp_dct["skills"]["technical_skills"])}")
    #         print(f"[INFO]{function_name}: soft_skills: {str(temp_dct["skills"]["soft_skills"])}")
    #     list_exp_dcts.append(temp_dct)
    # return list_exp_dcts

def experience_scoring(exps, keywords):
    function_name = helpers.inspect_function()
    function_desc = getattr(rapidfuzz.fuzz, CONFIG["PRUNING"]["DISTANCE_ALGO_DESC"])
    function_key = getattr(rapidfuzz.fuzz, CONFIG["PRUNING"]["DISTANCE_ALGO_KEY"])
    scoring_mode = CONFIG["PRUNING"]["DUAL_SCORING"]["EXP"]
    exps_cpy =exps.copy()
    for exp in exps_cpy:
        for keyword in keywords:
            if not scoring_mode:
                exp["experience"][1].append((keyword,function_desc(keyword, exp["experience"][0], processor=utils.default_process)))
                exp["description"][1].append((keyword,function_desc(keyword, exp["description"][0], processor=utils.default_process)))
            else:
                way1_exp = function_desc(keyword, exp["experience"][0], processor=utils.default_process)
                way1_desc = function_desc(keyword, exp["description"][0], processor=utils.default_process)
                way2_exp = function_desc( exp["experience"][0],keyword, processor=utils.default_process)
                way2_desc = function_desc(exp["description"][0],keyword,  processor=utils.default_process)
                if way1_exp > way2_exp:
                    exp["experience"][1].append((keyword, way1_exp))
                else:
                    exp["experience"][1].append((keyword, way2_exp))
                if way1_desc > way2_desc:
                    exp["description"][1].append((keyword, way1_desc))
                else:
                    exp["description"][1].append((keyword, way2_desc))

            for prog in exp["skills"]["programming_languages"]:
                if not scoring_mode:
                    prog[1].append((keyword,function_key(keyword, prog[0], processor=utils.default_process)))
                else:
                    way1_prog = function_desc(keyword,prog[0], processor=utils.default_process)
                    way2_prog = function_desc( prog[0],keyword, processor=utils.default_process)
                    if way1_prog > way2_prog:
                        prog[1].append((keyword, way1_prog))
                    else:
                        prog[1].append((keyword, way2_prog))             
            for tech in exp["skills"]["technical_skills"]:
                if not scoring_mode:
                    tech[1].append((keyword, function_key(keyword, tech[0], processor=utils.default_process)))
                else:
                    way1_tech = function_desc(keyword,tech[0], processor=utils.default_process)
                    way2_tech = function_desc( tech[0],keyword, processor=utils.default_process)
                    if way1_tech > way2_tech:
                        tech[1].append((keyword, way1_tech))
                    else:
                        tech[1].append((keyword, way2_tech))                    
            for soft in exp["skills"]["soft_skills"]:
                if not scoring_mode:
                    soft[1].append((keyword,function_key(keyword, soft[0], processor=utils.default_process)))
                else:
                    way1_soft = function_desc(keyword,soft[0], processor=utils.default_process)
                    way2_soft = function_desc( soft[0],keyword, processor=utils.default_process)
                    if way1_soft > way2_soft:
                        soft[1].append((keyword, way1_soft))
                    else:
                        soft[1].append((keyword, way2_soft)) 
    if config.DEBUG["INFO_LOGGING"]:
        for exp in exps_cpy:
            print(f"[INFO]{function_name}: experience: {exp["experience"][0]}")
            print(f"[INFO]{function_name}: experience scores: {str(exp["experience"][1])}")
            print(f"[INFO]{function_name}: description: {exp["description"][0]}")
            print(f"[INFO]{function_name}: description scores: {str(exp["description"][1])}")
            for prog in exp["skills"]["programming_languages"]:
                print(f"[INFO]{function_name}: programming_languages: {prog[0]}")
                print(f"[INFO]{function_name}: programming_languages scores: {str(prog[1])}")                    
            for tech in exp["skills"]["technical_skills"]:
                print(f"[INFO]{function_name}: technical_skills: {tech[0]}")
                print(f"[INFO]{function_name}: technical_skills scores: {str(tech[1])}")    
            for soft in exp["skills"]["soft_skills"]:
                print(f"[INFO]{function_name}: soft_skills: {soft[0]}")
                print(f"[INFO]{function_name}: soft_skills scores: {str(soft[1])}")

    return exps_cpy

def experience_heuristics(exps_scored):
    function_name = helpers.inspect_function()
    weights = CONFIG["PRUNING"]["EXP_H_WEIGHTS"]
    exps_scored_cpy = exps_scored.copy()
    exp_threshold = CONFIG["PRUNING"]["THRESHOLDS"]["EXP"]

    for exp in exps_scored_cpy:
        prog_l = []#Lists of tuples
        tech_l = []
        soft_l = []
        prog_sum = 0.0
        tech_sum = 0.0
        soft_sum = 0.0
        prog_offset = 0
        tech_offset = 0
        soft_offset = 0
        for prog in exp["skills"]["programming_languages"]:
            best_score = max(prog[1], key=itemgetter(1))
            if best_score[1] < exp_threshold:
                best_score = (best_score[0], 0.0)
                prog_offset = prog_offset + 1
            prog_l.append(best_score)
            prog_sum = prog_sum +  best_score[1]           
        for tech in exp["skills"]["technical_skills"]:
            best_score = max(tech[1], key=itemgetter(1))
            if best_score[1] < exp_threshold:
                best_score = (best_score[0], 0.0)
                tech_offset = tech_offset + 1
            tech_l.append(best_score)
            tech_sum = tech_sum +  best_score[1]
        for soft in exp["skills"]["soft_skills"]:
            best_score = max(soft[1], key=itemgetter(1))
            if best_score[1] < exp_threshold:
                best_score = (best_score[0], 0.0)
                soft_offset = soft_offset + 1
            soft_l.append(best_score)
            soft_sum = soft_sum +  best_score[1]
        exp_sum = 0.0
        desc_sum = 0.0
        exp_offset = 0
        desc_offset = 0
        for i in range(0, len (exp["experience"][1])):
            if exp["experience"][1][i][1]< exp_threshold:
                exp["experience"][1][i] = (exp["experience"][1][i][0],0.0)
                exp_offset = exp_offset + 1
            if exp["description"][1][i][1]< exp_threshold:
                exp["description"][1][i] = (exp["description"][1][i][0],0.0)
                desc_offset = desc_offset + 1
            exp_sum = exp_sum + exp["experience"][1][i][1]
            desc_sum = desc_sum + exp["description"][1][i][1]
        type = config.CONFIG["PRUNING"]["EXP_RATING_TYPE"]
        if type == "sum":
            prog_no = len(exp["skills"]["programming_languages"])-prog_offset
            tech_no = len(exp["skills"]["technical_skills"])-tech_offset
            soft_no = len(exp["skills"]["soft_skills"])-soft_offset
            exp_len = len(exp["experience"][1]) - exp_offset
            desc_len = len(exp["description"][1]) - desc_offset
            if prog_no > 0:
                prog_score = prog_sum *(1/prog_no) * weights["PROG"]
            else: prog_score =  0.0
            if tech_no >  0:
                tech_score = tech_sum *(1/tech_no) * weights["TECH"]
            else: tech_score =  0.0
            if soft_no > 0 :
                soft_score = soft_sum *(1/soft_no) * weights["SOFT"]
            else: soft_score =  0.0
            if exp_len > 0 :
                exp_score = exp_sum *(1/exp_len) * weights["EXP"]
            else: exp_score =  0.0
            if desc_len > 0 :
                desc_score = desc_sum *(1/desc_len) * weights["DESC"]
            else: desc_score =  0.0
            scores = {
                "experience": exp_score,
                "description": desc_score,
                "prog": prog_score,
                "tech": tech_score,
                "soft": soft_score
            }
        elif type == "SoM":

            prog_score = prog_sum * weights["PROG"]
            tech_score = tech_sum * weights["TECH"]
            soft_score = soft_sum * weights["SOFT"]
            exp_score = exp_sum * weights["EXP"]
            desc_score = desc_sum * weights["DESC"]
            scores = {
                "experience": exp_score,
                "description": desc_score,
                "prog": prog_score,
                "tech": tech_score,
                "soft": soft_score
            }
        elif type == "max":
            if len(prog_l) > 0:
                max(prog_l, key=itemgetter(1))
                max_prog = max(prog_l, key=itemgetter(1))[1]
            else:
                max_prog = 0
            if len(tech_l) > 0:
                max_tech = max(tech_l, key=itemgetter(1))[1]
            else:
                max_tech = 0
            if len(soft_l) > 0:
                max_soft = max(soft_l, key=itemgetter(1))[1]
            else:
                max_soft = 0
            
            
            scores = {
                "experience": max(exp["experience"][1], key=itemgetter(1))[1]* weights["EXP"],
                "description": max(exp["description"][1], key=itemgetter(1))[1]* weights["DESC"],
                "prog": max_prog * weights["PROG"],
                "tech": max_tech * weights["TECH"],
                "soft": max_soft * weights["SOFT"]
            }
        exp["scores"] = scores
        exp["total_score"] = scores["experience"] + scores["description"] + scores["prog"] + scores["tech"] + scores["soft"]
        """
        each exp = {
            "experience": (experience_text,[(keyword,score) with len(keywords)] )
            "description": (description_text,[distance_algo_scores with len(keywords)])
            c:{
                "programming_languages": [(prog_word1, [(keyword,score) with len(keywords),...],
                "technical_skills": [(tech_word1, [(keyword,score) with len(keywords),...],
                "soft_skills": [(soft_word1, [(keyword,score) with len(keywords),...]
            }
            "scores":{
                "experience":(heuristic value for experience)
                "description":(heuristic value for description)
                "prog": (heuristic value for prog)
                "tech": (heuristic value for tech)
                "soft": (heuristic value for soft)
            },
            "total_score": float number
        }
        """
        if config.DEBUG["HEURISTIC_LOGGING"]:
            print(f"[HEURISTIC][EXPERIENCES]{function_name}:HEURISTIC REPORT")
            print(f"[HEURISTIC]{function_name}: experience: {exp["experience"][0]}; with title score: {exp["scores"]["experience"]}; title weight: {weights["EXP"]}")
            print(f"[HEURISTIC]{function_name}: description: {exp["description"][0]}; with description score: {exp["scores"]["description"]}; description weight: {weights["DESC"]}")
            print(f"[HEURISTIC]{function_name}: prog score: {exp["scores"]["prog"]}; prog weight: {weights["PROG"]}")
            for skill in exp["skills"]["programming_languages"]:
                for keyword in skill[1]:
                    if keyword[1]>exp_threshold:
                        print(f"[HEURISTIC]{function_name}: skill {skill[0]}: keyword {keyword[0]}:score (before heuristic): {keyword[1]}")
            print(f"[HEURISTIC]{function_name}: tech score: {exp["scores"]["tech"]}; tech weight: {weights["TECH"]}")
            for skill in exp["skills"]["technical_skills"]:
                for keyword in skill[1]:
                    if keyword[1]>exp_threshold:
                        print(f"[HEURISTIC]{function_name}: skill {skill[0]}: keyword {keyword[0]}:score (before heuristic): {keyword[1]}")
            print(f"[HEURISTIC]{function_name}: soft score: {exp["scores"]["soft"]}; soft weight: {weights["SOFT"]}")
            for skill in exp["skills"]["soft_skills"]:
                for keyword in skill[1]:
                    if keyword[1]>exp_threshold:
                        print(f"[HEURISTIC]{function_name}: skill {skill[0]}: keyword {keyword[0]}:score (before heuristic): {keyword[1]}")
            print(f"[HEURISTIC]{function_name}: final score: {exp["total_score"]}")
            
            
    return exps_scored_cpy

@log_time
def experience_pruning_algorithm(job_desc,text,v_list,w_list,p_list):
    function_name = helpers.inspect_function()
#For experiences:
    #Input: job desc and a text to prune
    #Assuming: keyword matched job description
    """
    [E]Experience:
    Description:
    Skills:
    ...
    """    
    #Extract keyword list
    keywords = process_job_desc(job_desc) 
    #Extract list
    exps = process_exps(text)
    #Score each experience based on % matching
    exps_scored = experience_scoring(exps,keywords)
    #Heuristics(for final scoring)
    exps_heuristics = experience_heuristics(exps_scored)
    #Rank em
    sorted_exps = sorted(exps_heuristics, key=itemgetter('total_score'), reverse=True)
    simple_sorted_exps = []
    algo_th = CONFIG["PRUNING"]["NO_EXPERIENCES"]["ALGO_TH"]
    for exp in sorted_exps:
        if exp["total_score"] < algo_th:
            continue
        simple_sorted_exps.append(exp["experience"][0])
        if config.DEBUG["INFO_LOGGING"]: print(f"[INFO]{function_name}: simple_sorted_exps: exp: '{exp["experience"][0]}'")
    sorted_v_list =[]
    sorted_w_list = []
    sorted_p_list = []
    
    for exp in simple_sorted_exps:
        if exp in v_list:
            sorted_v_list.append(exp)
        if exp in w_list:
            sorted_w_list.append(exp)
        if exp in p_list:
            sorted_p_list.append(exp)
    
    sorted_v_list_cpy = deepcopy(sorted_v_list)
    sorted_w_list_cpy = deepcopy(sorted_w_list)
    sorted_p_list_cpy = deepcopy(sorted_p_list)
    #Fetch any currently preferred jobs; as well as job allocaion settings (total number of jobs, jobs per section)

    pref_list_v = CONFIG["PRUNING"]["PREFS"]["V"]
    pref_list_w = CONFIG["PRUNING"]["PREFS"]["W"] 
    pref_list_p = CONFIG["PRUNING"]["PREFS"]["P"]

    if pref_list_v != []:
        for item in reversed(pref_list_v):
            if config.DEBUG["INFO_LOGGING"]: print(f"[INFO]{function_name}: pref_list_v: item: '{item}'")
            rmv = False
            item_to_rmv = ""
            for i in sorted_v_list:
                if item in i:
                    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO]{function_name}: sorted_v_list removing item: '{i}'")
                    rmv = True
                    item_to_rmv = i
            if rmv:
                simple_sorted_exps.remove(item_to_rmv)
                # simple_sorted_exps.insert(0, item_to_rmv)
                sorted_v_list.remove(item_to_rmv)
                # sorted_v_list.insert(0, item_to_rmv)
    if pref_list_w != []:
        for item in reversed(pref_list_w):
            if config.DEBUG["INFO_LOGGING"]: print(f"[INFO]{function_name}: pref_list_w: item: '{item}'")
            rmv = False
            item_to_rmv = ""
            for i in sorted_w_list:
                if item in i:
                    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO]{function_name}: sorted_w_list removing item: '{i}'")
                    rmv = True
                    item_to_rmv = i
            if rmv:
                simple_sorted_exps.remove(item_to_rmv)
                # simple_sorted_exps.insert(0, item_to_rmv)
                sorted_w_list.remove(item_to_rmv)
                # sorted_w_list.insert(0, item_to_rmv)
    if pref_list_p != []:
        for item in reversed(pref_list_p):
            if config.DEBUG["INFO_LOGGING"]: print(f"[INFO]{function_name}: pref_list_p: item: '{item}'")
            rmv = False
            item_to_rmv = ""
            for i in sorted_p_list:
                if item in i:
                    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO]{function_name}: sorted_p_list removing item: '{i}'")
                    rmv = True
                    item_to_rmv = i
            if rmv:
                simple_sorted_exps.remove(item_to_rmv)
                # simple_sorted_exps.insert(0, item_to_rmv)
                sorted_p_list.remove(item_to_rmv)
                # sorted_p_list.insert(0, item_to_rmv)
    combined_pref_list = pref_list_v + pref_list_w + pref_list_p
    #Now we have a list of sorted experiences, with preferred ones removed from the list but stored in pref_list_x:
    #Two lists: preferred experiences, sorted experiences
    max_algo = CONFIG["PRUNING"]["NO_EXPERIENCES"]["ALGO"]
    if len(simple_sorted_exps)> max_algo:
        return_list = combined_pref_list + simple_sorted_exps[:max_algo]
    else:
        return_list = combined_pref_list + simple_sorted_exps
    #We have a combined list of preferred + algorithm selected experiences(up to max_algo)
    #min and max will be imposed on STEP1
    for i in range(0, len(return_list)):
        return_list[i] = "[E]Experience: " + return_list[i]
    return_txt = "\n".join(return_list)
    if config.DEBUG["INFO_LOGGING"]:
            print(f"[INFO]{function_name}: pruned text: {return_txt}")
    if config.DEBUG["HEURISTIC_LOGGING"]:
        print(f"[HEURISTIC][EXPERIENCES][STEP0]{function_name}:HEURISTIC REPORT")
        print(f"[HEURISTIC]{function_name}: algorithm-selected experiences, including preferrences(v,w,p): {len(sorted_v_list_cpy)}, {len(sorted_w_list_cpy)}, {len(sorted_p_list_cpy)}")
        for item in sorted_v_list_cpy:
            print(f"    [HEURISTIC]{function_name}: sorted v item: '{str(item)}'")
        for item in sorted_w_list_cpy:
            print(f"    [HEURISTIC]{function_name}: sorted w item: '{str(item)}'")
        for item in sorted_p_list_cpy:
            print(f"    [HEURISTIC]{function_name}: sorted p item: '{str(item)}'")
        print(f"[HEURISTIC]{function_name}: total experiences before pruning: {len(exps)}")
        print(f"[HEURISTIC]{function_name}: number of preferences(v,w,p): {len(pref_list_v)}, {len(pref_list_w)}, {len(pref_list_p)}")
        for item in pref_list_v:
            print(f"    [HEURISTIC]{function_name}: preferred v item: '{str(item)}'")
        for item in pref_list_w:
            print(f"    [HEURISTIC]{function_name}: preferred w item: '{str(item)}'")
        for item in pref_list_p:
            print(f"    [HEURISTIC]{function_name}: preferred p item: '{str(item)}'")
        

        print(f"[HEURISTIC]{function_name}: final pruned experiences count: {len(return_list)}")
        print(f"[HEURISTIC]{function_name}: final pruned experiences:")
        print(f"{return_txt}")
    return return_txt
    
def skill_scoring(list_to_score, keywords, type = "programming_languages"):
    """
    Input: List of strings to score
    Output: List of lists, per string to score, per keyword
    """
    function_name = helpers.inspect_function()
    list_to_score_cpy =deepcopy(list_to_score)
    score_lists = []
    # if type != "courses":
    if type == "programming_languages":
        scoring_mode = CONFIG["PRUNING"]["DUAL_SCORING"]["PROG"]
        function_score = getattr(rapidfuzz.fuzz, CONFIG["PRUNING"]["DISTANCE_ALGO_PROG"])
    elif type == "technical_skills":
        scoring_mode = CONFIG["PRUNING"]["DUAL_SCORING"]["TECH"]
        function_score = getattr(rapidfuzz.fuzz, CONFIG["PRUNING"]["DISTANCE_ALGO_TECH"])
    elif type == "soft_skills":
        scoring_mode = CONFIG["PRUNING"]["DUAL_SCORING"]["SOFT"]
        function_score = getattr(rapidfuzz.fuzz, CONFIG["PRUNING"]["DISTANCE_ALGO_SOFT"])
    else:
        raise  ValueError(f"[ERROR]{function_name}: invalid list type")
    for item in list_to_score_cpy:
        score_list = []
        for keyword in keywords:
            if not scoring_mode:
                score = function_score(item, keyword, processor=utils.default_process)
            else:
                score = max([function_score(item, keyword, processor=utils.default_process),function_score( keyword, item, processor=utils.default_process)])
            if config.DEBUG["INFO_LOGGING"]: print(f"[INFO]{function_name}: scored list item: {keyword} against {item}: {score}")
            score_list.append((item,keyword,score))
        score_lists.append(score_list)
    """
    returns a list of lists of pairs = [ 
    [(skill 1,keyword,score),etc..], ###list for skill 1,
    ...    
    ]
    """
    return score_lists
    # else:        
    #     function_score = getattr(rapidfuzz.fuzz, CONFIG["PRUNING"]["DISTANCE_ALGO_COURSES"])
    #     ##Implementation with added tags##

def skill_heuristics(scored_list, type = "programming_languages"):
    """
   input is list of lists of pairs = [ 
    [(skill1,keyword,score),etc..], ###list for skill 1,
    ...    
    ]
    """
    function_name = helpers.inspect_function()
    if type == "programming_languages":
        weight = CONFIG["PRUNING"]["PROG_H_WEIGHT"]
        heuristic_type = config.CONFIG["PRUNING"]["PROG_RATING_TYPE"]
        threshold = CONFIG["PRUNING"]["THRESHOLDS"]["PROG"]
    elif type == "technical_skills":
        weight = CONFIG["PRUNING"]["TECH_H_WEIGHT"]
        heuristic_type = config.CONFIG["PRUNING"]["TECH_RATING_TYPE"]
        threshold = CONFIG["PRUNING"]["THRESHOLDS"]["TECH"]
    elif type == "soft_skills":
        weight = CONFIG["PRUNING"]["SOFT_H_WEIGHT"]
        heuristic_type = config.CONFIG["PRUNING"]["SOFT_RATING_TYPE"]
        threshold = CONFIG["PRUNING"]["THRESHOLDS"]["SOFT"]
    else:
        raise  ValueError(f"[ERROR]{function_name}: invalid list type")
    scored_list_cpy = deepcopy(scored_list)
    list_offset = [0] * len(scored_list_cpy)
    for i in range(0, len(scored_list_cpy)):
        for j in range(0,len(scored_list_cpy[i])):
            if scored_list_cpy[i][j][2] < threshold:
                scored_list_cpy[i][j] = (scored_list_cpy[i][j][0],scored_list_cpy[i][j][1],0.0)
                list_offset[i] = list_offset[i] + 1
    heuristic_vals = []
    for i in range(0,len(scored_list_cpy)):
        item = scored_list_cpy[i]
        list_len = len(item)-list_offset[i]
        if list_len > 0:
            if heuristic_type == "sum":
                heuristic_vals.append(sum(keyword[2] for keyword in item)/list_len * weight)
            elif heuristic_type == "max":
                heuristic_vals.append(max(item,key=itemgetter(2))[2] * weight)
            elif heuristic_type == "SoM":
                heuristic_vals.append(sum(keyword[2] for keyword in item) * weight)
            else:
                ValueError(f"[ERROR]{function_name}: invalid heuristic type, check config")
        else: heuristic_vals.append(0.0)
    return_list = deepcopy(heuristic_vals)
    if config.DEBUG["HEURISTIC_LOGGING"]:
        print(f"[HEURISTIC][SKILLS]{function_name}:HEURISTIC REPORT")
        print(f"[HEURISTIC]{function_name}: type: {type}; threshold: {threshold}; weight: {weight}")
        for i in range(0,len(scored_list_cpy)):
            for j in range(0,len(scored_list_cpy[i])):
                if scored_list_cpy[i][j][2]>threshold:
                    print(f"[HEURISTIC]{function_name}: skill {scored_list_cpy[i][j][0]}: keyword {scored_list_cpy[i][j][1]}: score (before heuristic): {scored_list_cpy[i][j][2]}; score (after heuristic) type {heuristic_type}: {return_list[i]}")
    return return_list
@log_time
def skill_pruning_algorithm(job_desc, list_to_prune, type = "programming_languages"):
    function_name = helpers.inspect_function()
    #Extract keyword list
    keywords = process_job_desc(job_desc)
    list_scored = skill_scoring(list_to_prune, keywords, type)
    list_heuristic = skill_heuristics(list_scored, type) 
    paired_list_heuristic = []
    for i in range(0, len(list_heuristic)):
        paired_list_heuristic.append((list_to_prune[i],list_heuristic[i]))
    sorted_list_heuristic = sorted(paired_list_heuristic,key=itemgetter(1), reverse=True)
    if type == "programming_languages":
        max_total = CONFIG["PRUNING"]["NO_SKILLS"]["PROG"]
        max_algo = CONFIG["PRUNING"]["NO_SKILLS"]["ALGO_PROG"]
        prefs = CONFIG["PRUNING"]["PREFS"]["PROG"]
        prefs_toggle = CONFIG["PRUNING"]["NO_SKILLS"]["PREFERENCES_PROG"]
        threshold = CONFIG["PRUNING"]["NO_SKILLS"]["ALGO_PROG_TH"]
    elif type == "technical_skills":
        max_total = CONFIG["PRUNING"]["NO_SKILLS"]["TECH"]
        max_algo = CONFIG["PRUNING"]["NO_SKILLS"]["ALGO_TECH"]
        prefs_toggle = CONFIG["PRUNING"]["NO_SKILLS"]["PREFERENCES_TECH"]
        prefs = CONFIG["PRUNING"]["PREFS"]["TECH"]
        threshold = CONFIG["PRUNING"]["NO_SKILLS"]["ALGO_TECH_TH"]
    elif type == "soft_skills":
        max_total = CONFIG["PRUNING"]["NO_SKILLS"]["SOFT"]
        max_algo = CONFIG["PRUNING"]["NO_SKILLS"]["ALGO_SOFT"]
        prefs = CONFIG["PRUNING"]["PREFS"]["SOFT"]
        prefs_toggle = CONFIG["PRUNING"]["NO_SKILLS"]["PREFERENCES_SOFT"]
        threshold = CONFIG["PRUNING"]["NO_SKILLS"]["ALGO_SOFT_TH"]
    else:
        raise  ValueError(f"[ERROR]{function_name}: invalid list type")
    if max_total < 0 or max_algo < 0 or threshold < 0 :
        raise  ValueError(f"[ERROR]{function_name}: max_total, max_algo, threshold cannot be < 0")
    paired_prefs = []
    if prefs_toggle:
        for pref in reversed(prefs):
            paired_prefs.append((pref,1000.0))     
    off_set = 0
    for i in range(0,len(sorted_list_heuristic)):
        if sorted_list_heuristic[i-off_set][0] in prefs or sorted_list_heuristic[i-off_set][1]< threshold:
            sorted_list_heuristic.remove(sorted_list_heuristic[i-off_set])
            off_set = off_set+1
    if max_algo < len(sorted_list_heuristic): max_algo = max_algo
    else:max_algo = len(sorted_list_heuristic)
    if max_algo>0:
        paired_list = deepcopy(paired_prefs) +  deepcopy(sorted_list_heuristic[:max_algo])
    else:
        paired_list = deepcopy(paired_prefs)
    if max_total < len(paired_list): max_no = max_total
    else: max_no = len(paired_list)
    if max_no > 0 :
        return deepcopy(paired_list[:max_no])
    else:
        return([])

def tailor_skills_robust(call_info = template_call_info):
    call_id = call_info["call_id"]
    payload_in = call_info["payload_in"]
    format = call_info["format"]
    prompt_in = call_info["prompt_in"]
    ollama_url = call_info["ollama_url"]
    function_name = helpers.inspect_function()
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO]{function_name}: initiated")
    if call_id != function_name:
        if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: call_id {call_id} is not {function_name}")
        return f"[ERROR][OLLAMA]{function_name}: call_id {call_id} is not {function_name}"
    
    standard_call = format["standard_calls"][0]
    model = payload_in["model"]
    system_text = payload_in["system"]
    cv_data = format["cv_data"]
    job_description = format["job_description"]
    job_description_dct = format["job_description_dct"]
    # no_skills =format["no_skills"]
    # no_prog = format["no_prog"]
    # no_tech = format["no_tech"]
    # no_soft = format["no_soft"]

    #AI GENERATION (FILLER)
    runtime_info_temp = {
        "call_id": standard_call,
        "payload_in": {
            "model": model,
            "system": system_text
        },
        "format": {
            "cv_data": cv_data,
            "job_description": job_description,
            # "no_skills": no_skills,#on config, set on main
            # "no_prog":no_prog,#on config, set on main
            # "no_tech":no_tech,#on config, set on main
            # "no_soft":no_soft,#on config, set on main
        },
        "ollama_url":ollama_url
    }
    if config.DEBUG["INFO_LOGGING"]: print(f"[INFO]{function_name}: setup completed")
    if config.DEBUG["INFO_LOGGING"]: 
        print(f"[INFO]{function_name}: ai-powered pruning initiated")
        print(f"[INFO]{function_name}: ai-powered pruning input:")
        print(f"{cv_data}")

    sk_ollama = ollama_call(runtime_info=runtime_info_temp)
    if config.DEBUG["INFO_LOGGING"]: 
        print(f"[INFO]{function_name}: ai-powered pruning completed")
        print(f"[INFO]{function_name}: ai-powered pruning output:")
        print(f"{sk_ollama}")
    sk_ollama_dct = parsers.parse_cv_out(sk_ollama)
    skills_dct = parsers.parse_cv_out(cv_data)
    
    #ALGORITHMIC PRUNING (MAIN)
    prog_list = skills_dct["skills"]["programming_languages"]
    tech_list = skills_dct["skills"]["technical_skills"]
    soft_list = skills_dct["skills"]["soft_skills"]
    if config.DEBUG["INFO_LOGGING"]: 
        print(f"[INFO]{function_name}: algorithmic pruning initiated")
        print(f"[INFO]{function_name}: algorithmic pruning input: prog_list:")
        for p in prog_list:
            print(str(p))
        print(f"[INFO]{function_name}: algorithmic pruning input: tech_list:")
        for t in tech_list:
            print(str(t))
        print(f"[INFO]{function_name}: algorithmic pruning input: soft_list:")
        for s in soft_list:
            print(str(s))
    prog_list_pruned = skill_pruning_algorithm(job_description,prog_list,"programming_languages")
    tech_list_pruned = skill_pruning_algorithm(job_description,tech_list,"technical_skills")
    soft_list_pruned = skill_pruning_algorithm(job_description,soft_list,"soft_skills")
    if config.DEBUG["INFO_LOGGING"]: 
        print(f"[INFO]{function_name}: algorithmic pruning completed")
        print(f"[INFO]{function_name}: algorithmic pruning output: prog_list_pruned:")
        for p in prog_list_pruned:
            print(str(p))
        print(f"[INFO]{function_name}: algorithmic pruning output: tech_list_pruned:")
        for t in tech_list_pruned:
            print(str(t))
        print(f"[INFO]{function_name}: algorithmic pruning output: soft_list_pruned:")
        for s in soft_list_pruned:
            print(str(s))
    sk_pruning_dct = {
        "skills":{
            "programming_languages":deepcopy(prog_list_pruned),
            "technical_skills":deepcopy(tech_list_pruned),
            "soft_skills":deepcopy(soft_list_pruned)
        }
    }
    #PREFS + ALGO: sk_pruning_dct; NEXT: Add skills from job description if toggled
    prog_settings = {
        "type": "programming_languages",
        "max":CONFIG["PRUNING"]["NO_SKILLS"]["PROG"],
        # "pref":CONFIG["PRUNING"]["NO_SKILLS"]["PREFERENCES_PROG"],
        # "algo_max":CONFIG["PRUNING"]["NO_SKILLS"]["ALGO_PROG"],
        # "threshold":CONFIG["PRUNING"]["NO_SKILLS"]["ALGO_PROG_TH"]
        "copy": CONFIG["PRUNING"]["NO_SKILLS"]["COPY_PROG"],
        "copy_len": CONFIG["PRUNING"]["NO_SKILLS"]["COPY_LEN_PROG"]  
    }
    tech_settings = {
        "type":"technical_skills",
        "max":CONFIG["PRUNING"]["NO_SKILLS"]["TECH"],
        # "pref":CONFIG["PRUNING"]["NO_SKILLS"]["PREFERENCES_TECH"],
        # "algo_max":CONFIG["PRUNING"]["NO_SKILLS"]["ALGO_TECH"],
        # "threshold":CONFIG["PRUNING"]["NO_SKILLS"]["ALGO_TECH_TH"]
       "copy": CONFIG["PRUNING"]["NO_SKILLS"]["COPY_TECH"],
       "copy_len": CONFIG["PRUNING"]["NO_SKILLS"]["COPY_LEN_TECH"]   
    }
    soft_settings = {
        "type": "soft_skills",
        "max":CONFIG["PRUNING"]["NO_SKILLS"]["SOFT"],
        # "pref":CONFIG["PRUNING"]["NO_SKILLS"]["PREFERENCES_SOFT"],
        # "algo_max":CONFIG["PRUNING"]["NO_SKILLS"]["ALGO_SOFT"],
        # "threshold":CONFIG["PRUNING"]["NO_SKILLS"]["ALGO_SOFT_TH"]
        "copy": CONFIG["PRUNING"]["NO_SKILLS"]["COPY_SOFT"],
        "copy_len": CONFIG["PRUNING"]["NO_SKILLS"]["COPY_LEN_SOFT"]  
    }
    settings = [prog_settings,tech_settings,soft_settings]
    for setting in settings:
        curr_len = len(sk_pruning_dct["skills"][setting["type"]])
        if setting["copy"] and curr_len<setting["max"]:
            #We can continue adding
            if setting["copy_len"]==0:
                continue
            non_repeats = []
            for item in job_description_dct[setting["type"].replace("_"," ").title()]:
                if item.replace("-","").replace(".","").lower() not in [val[0].replace("-","").replace(".","").lower() for val in sk_pruning_dct["skills"][setting["type"]]]:
                    non_repeats.append((item,1000.0))
            if setting["copy_len"]<= setting["max"] - curr_len and setting["copy_len"] > 0 :
                copy_len = setting["copy_len"]
            else: copy_len =  setting["max"] - curr_len
            if len(non_repeats)< copy_len: copy_len = len(non_repeats)
            else: copy_len = copy_len
            sk_pruning_dct["skills"][setting["type"]] =  sk_pruning_dct["skills"][setting["type"]] + deepcopy(non_repeats[:copy_len])
    #AI GEN: new_sk_ollama_dct ; REMOVE DUPLICATES
    new_sk_ollama_dct = deepcopy(sk_ollama_dct)
    if config.DEBUG["INFO_LOGGING"]: 
        print(f"[INFO]{function_name}: malicious compliance deletion: deleting entries for algorithmic approach if found in ai-powered approach")
    for prog in sk_pruning_dct["skills"]["programming_languages"]:
        search_this = prog[0].replace("-","").replace(".","").lower()
        this_list = [val.replace("-","").replace(".","").lower() for val in new_sk_ollama_dct["skills"]["programming_languages"]]
        if search_this in this_list:
            index = this_list.index(search_this)
            print(f"deleted {str(prog[0])}")
            del new_sk_ollama_dct["skills"]["programming_languages"][index]
    for tech in sk_pruning_dct["skills"]["technical_skills"]:
        search_this =  tech[0].replace("-","").replace(".","").lower()
        this_list = [val.replace("-","").replace(".","").lower() for val in new_sk_ollama_dct["skills"]["technical_skills"]]
        if search_this in this_list:
            index = this_list.index(search_this)
            print(f"deleted {str(tech[0])}")
            del new_sk_ollama_dct["skills"]["technical_skills"][index]
    for soft in sk_pruning_dct["skills"]["soft_skills"]:
        search_this =soft[0].replace("-","").replace(".","").lower()
        this_list = [val.replace("-","").replace(".","").lower() for val in new_sk_ollama_dct["skills"]["soft_skills"]]
        if search_this in this_list:
            index = this_list.index(search_this)
            print(f"deleted {str(soft[0])}")
            del new_sk_ollama_dct["skills"]["soft_skills"][index]
    if config.DEBUG["INFO_LOGGING"]: 
        print(f"[INFO]{function_name}: malicious compliance deletion: completed:")
        print(f"[INFO]{function_name}: new_sk_ollama_dct[skills][programming_languages]:")
        for p in new_sk_ollama_dct["skills"]["programming_languages"]:
            print(str(p))
        print(f"[INFO]{function_name}: new_sk_ollama_dct[skills][technical_skills]::")
        for t in new_sk_ollama_dct["skills"]["technical_skills"]:
            print(str(t))
        print(f"[INFO]{function_name}: new_sk_ollama_dct[skills][soft_skills]:")
        for s in new_sk_ollama_dct["skills"]["soft_skills"]:
            print(str(s))
    #LAST: Fill with AI
    return_dct = {}
    return_dct["skills"] = {}
    for setting in settings:
        return_algo = []
        for tuple_item in sk_pruning_dct["skills"][setting["type"]]:
            print(f"appended {tuple_item[0]}")
            return_algo.append(tuple_item[0])
        print(f"type: {setting["type"]}; return_algo: {str(return_algo)}")

        if len(sk_pruning_dct["skills"][setting["type"]]) < setting["max"]:
            #We fill with AI
            return_algo =  return_algo + deepcopy(new_sk_ollama_dct["skills"][setting["type"]])
            ##############
            if len(return_algo) > setting["max"]:
                return_dct["skills"][setting["type"]] = deepcopy(return_algo[:setting["max"]])
            else:
                return_dct["skills"][setting["type"]] = deepcopy(return_algo)
        else:
            return_dct["skills"][setting["type"]] = deepcopy(return_algo[:setting["max"]])
    return_txt = parsers.inv_parse_cv_out(return_dct)
    if config.DEBUG["INFO_LOGGING"]: 
            print(f"[INFO]{function_name}: final output:")
            print(return_txt)
    return return_txt

def course_scoring(course_dct,keywords):
    """
    Needs to be done per education
    OUTPUT
    sample_dct = {
        course1: {
            itself: [list of scores (1 per keyword)], #Appended at runtime
            tag1: [list of scores (1 per keyword)]
            tag2: [list of scores (1 per keyword)]
            ...
        }
    }
    """
    function_name = helpers.inspect_function()
    function_score = getattr(rapidfuzz.fuzz, CONFIG["PRUNING"]["DISTANCE_ALGO_COURSES"])
    scoring_mode = CONFIG["PRUNING"]["DUAL_SCORING"]["COURSES"]

    course_dct_cpy = deepcopy(course_dct)
    for course in course_dct_cpy:
        if config.DEBUG["INFO_LOGGING"]: print(f"[INFO]{function_name}: current course: {course}")
        for tag in course_dct_cpy[course]:
            if config.DEBUG["INFO_LOGGING"]: print(f"[INFO]{function_name}: current tag: {tag}")
            temp_score_list = []
            for keyword in keywords:
                if tag == "itself":
                    temp_tag = course
                else:
                    temp_tag = tag
                if not scoring_mode:
                    temp_score_list.append(function_score(keyword, temp_tag, processor=utils.default_process))
                else:
                    temp_score_list.append(max([function_score(keyword, temp_tag, processor=utils.default_process),function_score( temp_tag, keyword, processor=utils.default_process)]))
            if config.DEBUG["INFO_LOGGING"]: print(f"[INFO]{function_name}: {course}: temp_score_list: {str(temp_score_list)}")
            course_dct_cpy[course][tag] = deepcopy(temp_score_list)
    return course_dct_cpy

def course_heuristics(scored_course_dct, keywords):
    """
    OUTPUT
    sample_dct = {
        course1: {
            itself: float_score (max or sum), #Appended at runtime
            tag1: float_score (max or sum),
            tag2: float_score (max or sum)
            ...
        }
    }
    """
    function_name = helpers.inspect_function()
    heuristic_type = config.CONFIG["PRUNING"]["COURSES_RATING_TYPE"]
    heuristic_course_dct = deepcopy(scored_course_dct)
    threshold = CONFIG["PRUNING"]["THRESHOLDS"]["COURSES"]
    for course in heuristic_course_dct:
        print(str(heuristic_course_dct[course]))
        no_tags = len(heuristic_course_dct[course])
        if no_tags > 0:#always itself
            for tag in heuristic_course_dct[course]:
                non_zero_keywords = 0
                for i in range(0,len(heuristic_course_dct[course][tag])):
                    if heuristic_course_dct[course][tag][i] < threshold:
                        heuristic_course_dct[course][tag][i] = 0.0
                    else:
                        non_zero_keywords = non_zero_keywords + 1
                print(str(heuristic_course_dct[course][tag]))
                no_keywords = non_zero_keywords
                if no_keywords > 0 :
                    if heuristic_type == "sum":
                        heuristic_course_dct[course][tag] = sum(heuristic_course_dct[course][tag])/no_keywords
                    elif heuristic_type == "max":
                        heuristic_course_dct[course][tag] = max(heuristic_course_dct[course][tag])
                    elif heuristic_type == "SoM":
                        heuristic_course_dct[course][tag] = sum(heuristic_course_dct[course][tag])
                    else:
                        ValueError(f"[ERROR]{function_name}: invalid heuristic type, check config")
                else: heuristic_course_dct[course][tag] = 0.0
        else:
            ValueError(F"[ERROR]{function_name}: no tags found, please revise config file or algorithm")
    if config.DEBUG["HEURISTIC_LOGGING"]:
        print(f"[HEURISTIC][COURSES][STEP0]{function_name}:HEURISTIC REPORT")
        print(f"[HEURISTIC]{function_name}: threshold: {threshold}; heuristic type: {heuristic_type}")
        for course in heuristic_course_dct:
            for tag in heuristic_course_dct[course]:
                if heuristic_course_dct[course][tag]>threshold:
                    if heuristic_type == max:
                        key_index = scored_course_dct[course][tag].index(heuristic_course_dct[course][tag])
                        print(f"[HEURISTIC]{function_name}: course {course}: tag: {tag}: keyword: {keywords[key_index]}: score (before heuristic): {scored_course_dct[course][tag][key_index]}; score (after heuristic) type {heuristic_type}: {heuristic_course_dct[course][tag]}")
                    else:
                        print(f"[HEURISTIC]{function_name}: course {course}: tag: {tag}: score (after heuristic) type {heuristic_type}: {heuristic_course_dct[course][tag]}")

    return heuristic_course_dct

def course_pruning_algorithm(job_desc, course_list):
    """
    Needs to be run per education;
    Returns list of courses in order of descending priority
    """
    if course_list == []:
        return course_list
    function_name = helpers.inspect_function()
    #Extract keyword list
    keywords = process_job_desc(job_desc)
    dct_to_score = {}
    for course in course_list:
        if config.DEBUG["INFO_LOGGING"]: print(f"[INFO]{function_name}: current course: {course}")
        dct_to_score[course] = {}
        dct_to_score[course]["itself"] = []
        tags = CONFIG["TAGS"]["COURSES"][course]
        if config.DEBUG["INFO_LOGGING"]: print(f"[INFO]{function_name}: current course tags: {str(tags)}")
        if tags == []:
            continue
        else:
            for tag in tags:
                if config.DEBUG["INFO_LOGGING"]: print(f"[INFO]{function_name}: current tag: {tag}")
                dct_to_score[course][tag] = []
    scored_courses = course_scoring(dct_to_score,keywords=keywords)
    heuristic_courses = course_heuristics(scored_courses,keywords)
    #Assign single score to course
    final_score_dct= {}
    pruning_type = config.CONFIG["PRUNING"]["COURSES_PRUNING_TYPE"]
    threshold = CONFIG["PRUNING"]["THRESHOLDS"]["COURSES"]
    for course in heuristic_courses:
        compare_list = []
        no_tags = len(heuristic_courses[course])
        for tag in heuristic_courses[course]:
            if heuristic_courses[course][tag] >= threshold:
                no_tags = no_tags -1
        if no_tags != 0 :
            for tag in heuristic_courses[course]:
                compare_list.append(heuristic_courses[course][tag])
            if pruning_type == "max":
                final_score_dct[course] = max(compare_list)
            elif pruning_type == "sum":
                final_score_dct[course] = sum(compare_list)/no_tags
            elif pruning_type == "SoM":
                final_score_dct[course] = sum(compare_list)
            else:
                ValueError(f"[ERROR]{function_name}: invalid pruning type, check config")
        else: final_score_dct[course] = 0.0
    if config.DEBUG["HEURISTIC_LOGGING"]:
        print(f"[HEURISTIC][COURSES][STEP1]{function_name}:HEURISTIC REPORT")
        print(f"[HEURISTIC]{function_name}: pruning type: {pruning_type}")
        for course in final_score_dct:
            print(f"[HEURISTIC]{function_name}: course {course}: score: {final_score_dct[course]}")

    sorted_courses = dict(sorted(final_score_dct.items(), reverse=True))
    sorted_list = []
    algo_th = CONFIG["PRUNING"]["NO_COURSES"]["ALGO_TH"]
    for course in sorted_courses:
        if sorted_courses[course]< algo_th:
            continue
        sorted_list.append(course)
    pref_list_courses = CONFIG["PRUNING"]["PREFS"]["COURSES"]
    max_algo = CONFIG["PRUNING"]["NO_COURSES"]["ALGO"]
    if max_algo > len(sorted_list):
        max_algo = len(sorted_list)
    sorted_list = sorted_list[:max_algo]
    if CONFIG["PRUNING"]["NO_COURSES"]["PREFERENCES"]:

        return_list = deepcopy(pref_list_courses) + deepcopy(sorted_list)
        unique = set()
        return_list_final = []
        for item in return_list:
            if item not in unique:
                unique.add(item)
                return_list_final.append(item)
    else:
        return_list_final = deepcopy(sorted_list)
    max_courses = CONFIG["PRUNING"]["NO_COURSES"]["MAX"]
    if config.DEBUG["HEURISTIC_LOGGING"]:
        print(f"[HEURISTIC][COURSES][STEP2]{function_name}:HEURISTIC REPORT")
        print(f"[HEURISTIC]{function_name}: max_courses: {max_courses}; preferences appended at the start: {str(pref_list_courses)}")
    return return_list_final[:int(max_courses)]

def tailor_courses_robust(call_info = template_call_info): 
    call_id = call_info["call_id"]
    payload_in = call_info["payload_in"]
    format = call_info["format"]
    prompt_in = call_info["prompt_in"]
    ollama_url = call_info["ollama_url"]
    job_description = format["job_description"]
    courses = format["courses"]
    standard_call = format["standard_calls"][0]
    function_name = helpers.inspect_function()
    model = payload_in["model"]
    system = payload_in["system"]
    #ALGO (ALGO +PREFS)
    if call_id != function_name:
        if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: call_id {call_id} is not {function_name}")
        return f"[ERROR][OLLAMA]{function_name}: call_id {call_id} is not {function_name}"
    courses0 = courses.replace("Courses:","").strip()
    courses1 = courses0.split(",")
    for i in range(0,len(courses1)):
        courses1[i]= courses1[i].strip()
    algo_courses = course_pruning_algorithm(job_description,courses1)
    #AI
    max_courses = CONFIG["PRUNING"]["NO_COURSES"]["MAX"]
    if len(algo_courses)< max_courses:
        #fill with AI
        runtime_info_temp = {
            "call_id": standard_call,
            "payload_in": {
                "model": model,
                "system": system
            },
            "format": {
                "courses": courses,
                "job_description": job_description,
            },
            "ollama_url":ollama_url
        }
        ##
        courses_ollama_txt = ollama_call(runtime_info=runtime_info_temp)
        step0 = courses_ollama_txt.replace("[1]Courses:","").strip()
        if step0 != "":
            step1 = [item.strip() for item in step0.split(",")]
        ai_courses = []
        for item in step1:
            if step1 != "":
                ai_courses.append(item)
        final_courses = list(set(deepcopy(algo_courses) + deepcopy(ai_courses)))
        if config.DEBUG["HEURISTIC_LOGGING"]:
            print(f"[HEURISTIC][COURSES][STEP3]{function_name}:HEURISTIC REPORT")
            print(f"[HEURISTIC]{function_name}: {max_courses-len(algo_courses)} ai_courses appended")
            print(f"[HEURISTIC]{function_name}: final_courses: {str(final_courses)}")
            print(f"[HEURISTIC]{function_name}: algo_courses: {str(algo_courses)}")
            print(f"[HEURISTIC]{function_name}: ai_courses: {str(ai_courses)}")

    else:
        #do not fill with AI
        final_courses = deepcopy(algo_courses)
    if len(final_courses)> max_courses:
        final_courses = final_courses[:max_courses]
    return_text = "Courses: " + ", ".join(final_courses)
    return return_text
    #Input is Courses: ..., ..., ...
        #And job description
    #Output is text Courses: ..., ..., ...
    
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
    v_list = []
    w_list = []
    p_list = []
    for item in reference_dct["volunteering_and_leadership"]:
        v_list.append(item["role"])
    for item in reference_dct["work_experience"]:
        w_list.append(item["job_title"])
    for item in reference_dct["projects"]:
        p_list.append(item["project_title"])
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
    max_exps = CONFIG["PRUNING"]["NO_EXPERIENCES"]["MAX"]
    if config.DEBUG["HEURISTIC_LOGGING"]:
        print(f"[HEURISTIC][EXPERIENCES][STEP1]{function_name}:HEURISTIC REPORT")
        print(f"[HEURISTIC]{function_name}: max_exps: {max_exps}")
    step1 = experience_pruning_algorithm(job_desc = job_description_summary,text = step0,v_list = v_list,w_list = w_list,p_list = p_list)
    step1_ai = ollama_call(runtime_info= runtime_info_temp)
    #step1 = step0_prune_experiences(model=model, system1=system1, ollama_url=ollama_url, experiences=step0, job_description=job_description_summary)
    if config.DEBUG["HEURISTIC_LOGGING"]: 
        print(f"[HEURISTIC]{function_name}: step1:\n" + step1)
        print(f"[HEURISTIC][OLLAMA]{function_name}: step1_ai:\n" + step1_ai)
    step1_clean = clean_first_step(step1).strip()
    step1_clean_ai = clean_first_step(step1_ai).strip()
    if config.DEBUG["HEURISTIC_LOGGING"]: 
        print(f"[HEURISTIC]{function_name}: step1:\n" + step1_clean)
        print(f"[HEURISTIC][OLLAMA]{function_name}: step1_ai:\n" + step1_clean_ai)
    step1_split = step1_clean.splitlines()
    step1_split_ai = step1_clean_ai.splitlines()
    for line in step1_split:
        if line in step1_split_ai:
            step1_split_ai.remove(line)
    step1_list = step1_split + step1_split_ai     
    #Keep min per section
    min_per_section = CONFIG["PRUNING"]["NO_EXPERIENCES"]["PER_SECTION"]
    step1_list_min = []
    ctr_v= 0 
    ctr_w= 0 
    ctr_p= 0 
    for item in step1_list:
        if ctr_v == min_per_section and ctr_w == min_per_section and ctr_p == min_per_section:
            break 
        temp_item = item.replace("[E]","").strip()
        if temp_item in v_list and ctr_v < min_per_section:
            step1_list_min.append(item)
            ctr_v += 1
        if temp_item in w_list and ctr_w < min_per_section:
            step1_list_min.append(item)
            ctr_w += 1
        if temp_item in p_list and ctr_p < min_per_section:
            step1_list_min.append(item)
            ctr_p += 1
    step1_remaining = list(set(step1_list) - set(step1_list_min))
    #Maintain max overall

    step1_merged_list = step1_list_min+step1_remaining
    if len(step1_merged_list) <= max_exps:
        max_exps = len(step1_merged_list)
    step1_merged_list = step1_merged_list[:max_exps]
    step1_merged = "\n".join(step1_merged_list)
    if config.DEBUG["HEURISTIC_LOGGING"]:
        print(f"[HEURISTIC]{function_name}: algorithm-chosen experiences:{len(step1_split)}; ai-chosen experiences:{len(step1_split_ai)}; max_exps after adjustment:{max_exps}")
        print(f"[HEURISTIC]{function_name}: step1_merged:\n" + step1_merged)
    step2_dct = augment_output(step1_merged, reference_dct, type=section)
    if config.DEBUG["HEURISTIC_LOGGING"]: print(f"[HEURISTIC]{function_name}: step2_dct:\n" + str(step2_dct))
    #helpers.filter_output()#REDUNDANT?
    step2_text = parsers.inv_parse_cv(step2_dct)
    if config.DEBUG["HEURISTIC_LOGGING"]: print(f"[HEURISTIC]{function_name}: step2_text:\n" + step2_text)
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

@log_time #USED IN MAIN ; returns ERROR as text
def tailor_experiences(call_info = template_call_info):
    call_id = call_info["call_id"]
    payload_in = call_info["payload_in"]
    format = call_info["format"]
    ollama_url = call_info["ollama_url"]
    function_name = helpers.inspect_function()
    if call_id != function_name:
        if config.DEBUG["ERROR_LOGGING"]: logging.error(f"[ERROR][OLLAMA]{function_name}: call_id {call_id} is not {function_name}")
        return f"[ERROR][OLLAMA]{function_name}: call_id {call_id} is not {function_name}"
    job_description_summary = format["job_description_summary"]
    reference_dct = format["reference_dct"]

    reference_dct_v = {"volunteering_and_leadership": deepcopy(reference_dct["volunteering_and_leadership"])}
    reference_dct_w = {"work_experience": deepcopy(reference_dct["work_experience"])}
    reference_dct_p = {"projects": deepcopy(reference_dct["projects"])}
    references = [reference_dct_v,reference_dct_w,reference_dct_p]
    names = ["volunteering_and_leadership","work_experience","projects"]
    sections_0 = ["[0]Volunteering and Leadership:","[0]Work Experience:","[0]Projects:"]
    sections_1 = ["[1]Role: ","[1]Job Title: ","[1]Project Title: "]
    return_l = []
    for i in range(0,3):
        if references[i][names[i]] == []:
            continue
        step0 = prepare_input_text(parsers.inv_parse_cv(references[i]), type=names[i])
        if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step0:\n" + step0)
        step1 = step0.replace("Experience:", "[E]Experience:")
        if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step1:\n" + step1)
        step1_clean = clean_first_step(step1).strip()
        if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step1_clean:\n" + step1_clean)
        step2_dct = augment_output(step1_clean, reference_dct, type='vl_w_p')
        if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step2_dct:\n" + str(step2_dct))
        step2_text = parsers.inv_parse_cv(step2_dct)
        if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step2_text:\n" + step2_text)
        step2_text = step2_text.replace(sections_0[i], "").strip()
        if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step2_text (No [0]):\n" + step2_text)
        step3_text = step2_text.split(sections_1[i])[1:]
        step3_text = [sections_1[i] + exp for exp in step3_text]
        step3_list = []
        keywords = ""
        for line in job_description_summary.splitlines():
            if "Keywords:" in line:
                keywords = line.strip()
                break
        for exp in step3_text:
            if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step3_text(loop): exp:\n" + exp)
            exp_dict = parsers.parse_subfields(exp.strip())
            first_part_dict = {k: v for k, v in exp_dict.items() if k in ["description"]}
            second_part_dict = {k: v for k, v in exp_dict.items() if k not in ["description"]}
            first_part_text = parsers.inv_parse_subfields(first_part_dict).strip()
            second_part_text = parsers.inv_parse_subfields(second_part_dict).strip()
            if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step3_text(loop): exp: first_part_text:\n" + first_part_text)
            if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step3_text(loop): exp: second_part_text:\n" + second_part_text)
            
            runtime_info_temp = {"call_id": format["standard_calls"][0],
                            "ollama_url": ollama_url,
                            "format": {
                                "experience": first_part_text,
                                #"job_keywords": keywords,
                            },
                            "payload_in":{
                                "system":payload_in["system"],
                                "model": payload_in["model"]
                            }                   
            }   
            first_part_text_new = ollama_call(runtime_info=runtime_info_temp)
            if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step3_text(loop): exp: {format.get("standard_calls", "")[0]}: first_part_text_new:\n" + first_part_text_new)
            first_part_text_new = first_part_text_new.strip()
            if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step3_text(loop): exp: {format.get("standard_calls", "")[0]}: first_part_text_new (filtered):\n" + first_part_text_new)
            temp = second_part_text + "\n" + first_part_text_new
            if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step3_text(loop): exp: {format.get("standard_calls", "")[0]}: temp(joined):\n" + temp)
            step3_list.append(temp)
        step3_text = "\n".join(step3_list)
        if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step3_text:\n" + step3_text)
        step4_text = f"{sections_0[i]}\n" + step3_text
        if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step4_text (before filtering):\n" + step4_text)
        step4_text = step4_text.strip()
        if config.DEBUG["INFO_LOGGING"]: print(f"[INFO][OLLAMA]{function_name}: step4_text (after filtering):\n" + step4_text)
        return_l.append(step4_text)
    return '\n'.join(return_l)
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
