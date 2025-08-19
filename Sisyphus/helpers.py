import os
from xml.parsers.expat import model
from Sisyphus import parsers, runLocalModel
import datetime
import subprocess
import logging
import re
from Sisyphus.decorators import log_time
from Sisyphus.decorators import FUNCTION_STATS
# Set up logging
print = logging.info


TOKENIZER_PATH = r"C:\CodeProjects\Sisyphus\Sisyphus\tokenizers"
LLAMA_MAX_TOKENS = 4096


def performance_check(descending=True, mode="runtime"):
    # Log performance statistics, in descending order of runtime
    for fname, stats in sorted(FUNCTION_STATS.items(), key=lambda item: item[1][mode], reverse=descending):
        logging.info(f"[PERFORMANCE] {fname} called {stats['counter']} times, total {mode}: {stats[mode]:.4f} seconds")
    # Provide summary statistics
    total_calls = sum(stats['counter'] for stats in FUNCTION_STATS.values())
    total_runtime = sum(stats['runtime'] for stats in FUNCTION_STATS.values())
    logging.info(f"[PERFORMANCE] Total function calls: {total_calls}, Total runtime: {total_runtime:.4f} seconds")
    # Clear function statistics
    FUNCTION_STATS.clear()


@log_time
def optimize_summarize_sections_calls(no_sections = 0, chunk_sz = 4):
    return_calls = []
    if no_sections <= 0:
        raise ValueError("[ERROR]optimize_summarize_section_calls: No sections to summarize")
    remainder = no_sections
    chunk_size = chunk_sz # Number of sections to summarize in one call
    while chunk_size > 0:
        # Optimize calls to summarize_sections
        times = remainder // chunk_size
        remainder = remainder % chunk_size
        return_calls += [chunk_size] * times
        chunk_size -= 1
    return return_calls
        
        


@log_time
def count_tokens_with_js(text):
    tokenizer_js_path = os.path.join(TOKENIZER_PATH, "llama3", "tokenizer.js")
    result = subprocess.run(
        ["node", tokenizer_js_path],
        input=text,
        capture_output=True, 
        text=True
    )
    if result.stderr:
        print("JS Error: " + result.stderr)
    print("JS Output: " + result.stdout)
    if not result.stdout.strip().isdigit():
        raise RuntimeError("Token JS script did not return a valid number.")
    return int(result.stdout.strip())

@log_time
def token_math(model, input_text, type = "input", offset = 0):
    
    
    if model.startswith("llama3"):
        tokens = count_tokens_with_js(input_text.strip())
        max_tokens = LLAMA_MAX_TOKENS

    else:
        print(f"Token calculation not implemented for model: {model}")
        return

    remaining_tokens = max_tokens - tokens - offset
    percent_used = (tokens / max_tokens) * 100
    if type == "input":
        print(f"[MODEL: {model}] Input token usage: {percent_used:.2f}%")
        if remaining_tokens < 0:
            print(f"[MODEL: {model}] Input exceeds max tokens by {-remaining_tokens}.")
        else:
            print(f"[MODEL: {model}] Input uses {tokens} tokens, remaining for response: {remaining_tokens}.")

    if type == "output":
        print(f"[MODEL: {model}] Output token usage: {percent_used:.2f}%")
        if remaining_tokens < 0:
            print(f"[MODEL: {model}] Output exceeds max tokens by {-remaining_tokens}.")
        else:
            print(f"[MODEL: {model}] Output uses {tokens} tokens, remaining for response: {remaining_tokens}.")
    return tokens

@log_time
def read_text_file(file_path):
    """
    Reads a text file from the given file location and returns its contents as a string.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

@log_time
def indent_text(text):
    #Indents text based on first 3 characters of each line: [0] indicates no indent, [1] indicates 1 indent, etc.
    lines = text.splitlines()
    indented_lines = []
    for line in lines:
        if line.startswith('[') and len(line) > 2 and line[1].isdigit() and line[2] == ']':
            indent_level = line[1]
            if indent_level == '0':
                indent = ''
            else:
                indent = ' ' * (int(indent_level) * 4)
            indented_lines.append(f"{indent}{line.strip()}")
    return "\n".join(indented_lines)

@log_time
def list_text_files(folder_path):
    """
    Returns a list of strings denoting the text files present in the given folder.
    """
    return [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f.lower().endswith('.txt')]

@log_time
def list_docx_files(folder_path):
    """
    Returns a list of strings denoting the docx files present in the given folder.
    """
    return [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f.lower().endswith('.docx')]

@log_time
def format_output(cv_text):
    """
    Takes a CV text string, parses it to a dict, and formats keys in the following order, returning a string:
    [0]Name
    [0]Contact Information
    [0]Title
    [0]Summary
    [0]Languages
    [0]Education
    [0]Certifications
    [0]Awards and Scholarships
    [0]Volunteering and Leadership
    [0]Work Experience
    [0]Projects
    """
    cv_dict = parsers.parse_cv(cv_text)
    output = ""
    for key in [
        'name',
        'contact_information',
        'title',
        'summary',
        'languages',
        'education',
        'certifications',
        'awards_and_scholarships',
        'volunteering_and_leadership',
        'work_experience',
        'projects'
    ]:
        if key in cv_dict:
            print(f"Processing section: {key}")
            output += parsers.inv_parse_cv({key: cv_dict[key]})
            output += "\n"
    return output

@log_time
def refresh_options():
    print("Refreshing options...")
    # Fetch available models, systems, and CVs
    models = runLocalModel.fetch_available_ollama_models()
    systems = list_text_files("Sisyphus/systems")
    cvs = list_text_files("Sisyphus/cvs")
    templates = list_docx_files("Sisyphus/templates")
    saved_outs = list_text_files("Sisyphus/saved_outputs")
    saved_outs_cl = list_text_files("Sisyphus/saved_outputs_cl")
    cl_templates = list_docx_files("Sisyphus/templates_cl")
    print("Options refreshed:")
    print("Models: " + str(models))
    print("Systems: " + str(systems))
    print("CVs: " + str(cvs))
    print("CV Templates: " + str(templates))
    print("CL Templates: " + str(cl_templates))
    print("Previously Saved CV Outputs: " + str(saved_outs))
    print("Previously Saved CL Outputs: " + str(saved_outs_cl))

    return [models, systems, cvs, templates, saved_outs, saved_outs_cl, cl_templates]

@log_time
def format_checker(cv_text):
    """
    Checks if cv_text follows the strict format/order of sections/subsections.
    Returns a dict with lists of missing or empty sections/subsections.
    """
    import re
    # Define expected sections and subsections
    expected = {
        '[0]Name:': [],
        '[0]Contact Information:': [
            '[1]Address:', '[1]Phone:', '[1]Email:', '[1]LinkedIn:', '[1]Github:', '[1]Portfolio:'
        ],
        '[0]Title:': [],
        '[0]Summary:': [],
        '[0]Languages:': [],
        '[0]Education:': [
            '[1]Degree:', '[1]University:', '[1]Location:', '[1]Duration:', '[1]Courses:'
        ],
        '[0]Certifications:': [
            '[1]Certification Name:', '[1]Issuing Organization:', '[1]Issue Date:'
        ],
        '[0]Awards and Scholarships:': [
            '[1]Award Name:', '[1]Issuing Organization:', '[1]Issue Date:'
        ],
        '[0]Volunteering and Leadership:': [
            '[1]Role:', '[1]Organization:', '[1]Location:', '[1]Duration:', '[1]Description:', '[1]Skills:'
        ],
        '[0]Work Experience:': [
            '[1]Job Title:', '[1]Company:', '[1]Location:', '[1]Duration:', '[1]Description:', '[1]Skills:'
        ],
        '[0]Projects:': [
            '[1]Project Title:', '[1]Type:', '[1]Duration:', '[1]Description:', '[1]Skills:'
        ]
    }

    # Find all section headers and their lines
    lines = [line.strip() for line in cv_text.splitlines() if line.strip()]
    found_sections = {key: [] for key in expected}
    current_section = None
    for line in lines:
        for section in expected:
            if line.startswith(section):
                current_section = section
                found_sections[section].append(line)
                break
        else:
            # Check for subsections
            if current_section and any(line.startswith(sub) for sub in expected[current_section]):
                found_sections[current_section].append(line)

    missing_sections = []
    missing_subsections = []
    empty_subsections = []

    # Helper: for sections with multiple entries, count the number of main entries
    def count_entries(section, entry_key):
        return sum(1 for l in found_sections[section] if l.startswith(entry_key))

    empty_sections = []
    for section, subs in expected.items():
        section_lines = [l for l in found_sections[section] if l.startswith(section)]
        if not section_lines:
            missing_sections.append(section)
        else:
            # Special handling for sections without subsections
            if section in ['[0]Name:', '[0]Title:', '[0]Summary:', '[0]Languages:']:
                # Check if the section line contains a non-empty string after the colon
                non_empty = False
                for l in section_lines:
                    # Remove header and check if anything remains
                    content = l[len(section):].strip()
                    if content:
                        non_empty = True
                        break
                if not non_empty:
                    empty_sections.append(section)
                continue
            # For multi-entry sections, count expected occurrences
            entry_counts = {}
            if section == '[0]Education:':
                n = count_entries(section, '[1]Degree:')
                entry_counts = {
                    '[1]Degree:': n,
                    '[1]University:': n,
                    '[1]Location:': n,
                    '[1]Duration:': n,
                    '[1]Courses:': n
                }
            elif section == '[0]Certifications:':
                n = count_entries(section, '[1]Certification Name:')
                entry_counts = {
                    '[1]Certification Name:': n,
                    '[1]Issuing Organization:': n,
                    '[1]Issue Date:': n
                }
            elif section == '[0]Awards and Scholarships:':
                n = count_entries(section, '[1]Award Name:')
                entry_counts = {
                    '[1]Award Name:': n,
                    '[1]Issuing Organization:': n,
                    '[1]Issue Date:': n
                }
            elif section == '[0]Volunteering and Leadership:':
                n = count_entries(section, '[1]Role:')
                entry_counts = {
                    '[1]Role:': n,
                    '[1]Organization:': n,
                    '[1]Location:': n,
                    '[1]Duration:': n,
                    '[1]Description:': n,
                    '[1]Skills:': n
                }
            elif section == '[0]Work Experience:':
                n = count_entries(section, '[1]Job Title:')
                entry_counts = {
                    '[1]Job Title:': n,
                    '[1]Company:': n,
                    '[1]Location:': n,
                    '[1]Duration:': n,
                    '[1]Description:': n,
                    '[1]Skills:': n
                }
            elif section == '[0]Projects:':
                n = count_entries(section, '[1]Project Title:')
                entry_counts = {
                    '[1]Project Title:': n,
                    '[1]Type:': n,
                    '[1]Duration:': n,
                    '[1]Description:': n,
                    '[1]Skills:': n
                }
            # For each subsection, count actual occurrences and compare
            total_subs_found = 0
            for sub in subs:
                if entry_counts:
                    expected_n = entry_counts.get(sub, 1)
                    actual_n = sum(1 for l in found_sections[section] if l.startswith(sub))
                    total_subs_found += actual_n
                    missing_n = expected_n - actual_n
                    if missing_n > 0:
                        missing_subsections.append((f"{section}:{sub}", missing_n))
                    if actual_n == 0 and expected_n > 0:
                        empty_subsections.append((f"{section}:{sub}", expected_n))
                else:
                    # For single-entry subsections
                    actual_n = sum(1 for l in found_sections[section] if l.startswith(sub))
                    total_subs_found += actual_n
                    if actual_n == 0:
                        empty_subsections.append((f"{section}:{sub}", 1))
            # If section exists but has no valid subsections/entries, mark as empty section
            if total_subs_found == 0:
                empty_sections.append(section)
    return {
        'missing_sections': missing_sections,
        'empty_sections': empty_sections,
        'missing_subsections': missing_subsections,
        'empty_subsections': empty_subsections
    }

@log_time
def format_checker_out (cv_text):
    """
    Checks if cv_text follows the strict format/order of sections/subsections.
    Returns a dict with lists of missing or empty sections/subsections.
    """
    import re
    # Define expected sections and subsections
    expected = {
        '[0]Name:': [],
        '[0]Contact Information:': [
            '[1]Address:', '[1]Phone:', '[1]Email:', '[1]LinkedIn:', '[1]Github:', '[1]Portfolio:'
        ],
        '[0]Title:': [],
        '[0]Summary:': [],
        '[0]Languages:': [],
        '[0]Education:': [
            '[1]Degree:', '[1]University:', '[1]Location:', '[1]Duration:', '[1]Courses:'
        ],
        '[0]Certifications:': [
            '[1]Certification Name:', '[1]Issuing Organization:', '[1]Issue Date:'
        ],
        '[0]Awards and Scholarships:': [
            '[1]Award Name:', '[1]Issuing Organization:', '[1]Issue Date:'
        ],
        '[0]Volunteering and Leadership:': [
            '[1]Role:', '[1]Organization:', '[1]Location:', '[1]Duration:', '[1]Description:'
        ],
        '[0]Work Experience:': [
            '[1]Job Title:', '[1]Company:', '[1]Location:', '[1]Duration:', '[1]Description:'
        ],
        '[0]Projects:': [
            '[1]Project Title:', '[1]Type:', '[1]Duration:', '[1]Description:'
        ],
         '[0]Skills:': [
            '[1]Programming Languages:', '[1]Technical Skills:', '[1]Soft Skills:'
         ]
    }

    # Find all section headers and their lines
    lines = [line.strip() for line in cv_text.splitlines() if line.strip()]
    found_sections = {key: [] for key in expected}
    current_section = None
    for line in lines:
        for section in expected:
            if line.startswith(section):
                current_section = section
                found_sections[section].append(line)
                break
        else:
            # Check for subsections
            if current_section and any(line.startswith(sub) for sub in expected[current_section]):
                found_sections[current_section].append(line)

    missing_sections = []
    missing_subsections = []
    empty_subsections = []

    # Helper: for sections with multiple entries, count the number of main entries
    def count_entries(section, entry_key):
        return sum(1 for l in found_sections[section] if l.startswith(entry_key))

    empty_sections = []
    for section, subs in expected.items():
        section_lines = [l for l in found_sections[section] if l.startswith(section)]
        if not section_lines:
            missing_sections.append(section)
        else:
            # Special handling for sections without subsections
            if section in ['[0]Name:', '[0]Title:', '[0]Summary:', '[0]Languages:']:
                # Check if the section line contains a non-empty string after the colon
                non_empty = False
                for l in section_lines:
                    # Remove header and check if anything remains
                    content = l[len(section):].strip()
                    if content:
                        non_empty = True
                        break
                if not non_empty:
                    empty_sections.append(section)
                continue
            # For multi-entry sections, count expected occurrences
            entry_counts = {}
            if section == '[0]Education:':
                n = count_entries(section, '[1]Degree:')
                entry_counts = {
                    '[1]Degree:': n,
                    '[1]University:': n,
                    '[1]Location:': n,
                    '[1]Duration:': n,
                    '[1]Courses:': n
                }
            elif section == '[0]Certifications:':
                n = count_entries(section, '[1]Certification Name:')
                entry_counts = {
                    '[1]Certification Name:': n,
                    '[1]Issuing Organization:': n,
                    '[1]Issue Date:': n
                }
            elif section == '[0]Awards and Scholarships:':
                n = count_entries(section, '[1]Award Name:')
                entry_counts = {
                    '[1]Award Name:': n,
                    '[1]Issuing Organization:': n,
                    '[1]Issue Date:': n
                }
            elif section == '[0]Volunteering and Leadership:':
                n = count_entries(section, '[1]Role:')
                entry_counts = {
                    '[1]Role:': n,
                    '[1]Organization:': n,
                    '[1]Location:': n,
                    '[1]Duration:': n,
                    '[1]Description:': n,
                    '[1]Skills:': n
                }
            elif section == '[0]Work Experience:':
                n = count_entries(section, '[1]Job Title:')
                entry_counts = {
                    '[1]Job Title:': n,
                    '[1]Company:': n,
                    '[1]Location:': n,
                    '[1]Duration:': n,
                    '[1]Description:': n,
                    '[1]Skills:': n
                }
            elif section == '[0]Projects:':
                n = count_entries(section, '[1]Project Title:')
                entry_counts = {
                    '[1]Project Title:': n,
                    '[1]Type:': n,
                    '[1]Duration:': n,
                    '[1]Description:': n,
                    '[1]Skills:': n
                }
            # For each subsection, count actual occurrences and compare
            total_subs_found = 0
            for sub in subs:
                if entry_counts:
                    expected_n = entry_counts.get(sub, 1)
                    actual_n = sum(1 for l in found_sections[section] if l.startswith(sub))
                    total_subs_found += actual_n
                    missing_n = expected_n - actual_n
                    if missing_n > 0:
                        missing_subsections.append((f"{section}:{sub}", missing_n))
                    if actual_n == 0 and expected_n > 0:
                        empty_subsections.append((f"{section}:{sub}", expected_n))
                else:
                    # For single-entry subsections
                    actual_n = sum(1 for l in found_sections[section] if l.startswith(sub))
                    total_subs_found += actual_n
                    if actual_n == 0:
                        empty_subsections.append((f"{section}:{sub}", 1))
            # If section exists but has no valid subsections/entries, mark as empty section
            if total_subs_found == 0:
                empty_sections.append(section)
    return {
        'missing_sections': missing_sections,
        'empty_sections': empty_sections,
        'missing_subsections': missing_subsections,
        'empty_subsections': empty_subsections
    }

@log_time
def format_checker_out_cl(cl_text):
    """
    Checks if cv_text follows the strict format/order of sections/subsections.
    Returns a dict with lists of missing or empty sections/subsections.
    """
    import re
    # Define expected sections and subsections
    expected = {
        '[0]Name:': [],
        '[0]Contact Information:': [
            '[1]Address:', '[1]Phone:', '[1]Email:', '[1]LinkedIn:', '[1]Github:', '[1]Portfolio:'
        ],
        '[0]Title:': [],
        '[0]Languages:': [],
        '[0]Cover Letter:': [
            '[1]New Paragraph0:', '[1]New Paragraph1:', '[1]New Paragraph2:', '[1]New Paragraph3:'
        ]
    }

    # Find all section headers and their lines
    lines = [line.strip() for line in cl_text.splitlines() if line.strip()]
    found_sections = {key: [] for key in expected}
    current_section = None
    for line in lines:
        for section in expected:
            if line.startswith(section):
                current_section = section
                found_sections[section].append(line)
                break
        else:
            # Check for subsections
            if current_section and any(line.startswith(sub) for sub in expected[current_section]):
                found_sections[current_section].append(line)

    missing_sections = []
    missing_subsections = []
    empty_subsections = []

    # Helper: for sections with multiple entries, count the number of main entries
    def count_entries(section, entry_key):
        return sum(1 for l in found_sections[section] if l.startswith(entry_key))

    empty_sections = []
    for section, subs in expected.items():
        section_lines = [l for l in found_sections[section] if l.startswith(section)]
        if not section_lines:
            missing_sections.append(section)
        else:
            # Special handling for sections without subsections
            if section in ['[0]Name:', '[0]Title:', '[0]Languages:']:
                # Check if the section line contains a non-empty string after the colon
                non_empty = False
                for l in section_lines:
                    # Remove header and check if anything remains
                    content = l[len(section):].strip()
                    if content:
                        non_empty = True
                        break
                if not non_empty:
                    empty_sections.append(section)
                continue
            # For each subsection, count actual occurrences and compare
            total_subs_found = 0
            for sub in subs:
                # For single-entry subsections
                actual_n = sum(1 for l in found_sections[section] if l.startswith(sub))
                total_subs_found += actual_n
                if actual_n == 0:
                    empty_subsections.append((f"{section}:{sub}", 1))
            # If section exists but has no valid subsections/entries, mark as empty section
            if total_subs_found == 0:
                empty_sections.append(section)
    return {
        'missing_sections': missing_sections,
        'empty_sections': empty_sections,
        'missing_subsections': missing_subsections,
        'empty_subsections': empty_subsections
    }

@log_time
def filter_output(model_output, mode = "digits"):
    """
    Filters model output, keeping only lines that start with [X], where X is a number (e.g., [0], [1], etc.).
    Returns the filtered output as a string.
    """
    filtered_lines = []
    for line in model_output.splitlines():
        line = line.strip()
        if mode == "digits":
            if line.startswith("[") and len(line) > 2 and line[2] == "]" and line[1].isdigit():
                filtered_lines.append(line)
        elif mode == "cap_letters":
            if line.startswith("[") and len(line) > 2 and line[2] == "]" and line[1].isupper():
                filtered_lines.append(line)

    return "\n".join(filtered_lines)

@log_time
def read_format_checker(format_checker_output):
    """
    Prints out sequentially:
    - Names of missing sections
    - Names of empty sections
    - Names and number of missing subsections
    - Names and number of empty subsections
    """
    return_str = ""
    return_str += "Missing Sections:\n"
    for section in format_checker_output.get('missing_sections', []):
        return_str += f"  {section}\n"
    return_str += "\nEmpty Sections:\n"
    for section in format_checker_output.get('empty_sections', []):
        return_str += f"  {section}\n"
    return_str += "\nMissing Subsections:\n"
    for sub, count in format_checker_output.get('missing_subsections', []):
        return_str += f"  {sub} (missing {count})\n"
    return_str += "\nEmpty Subsections:\n"
    for sub, count in format_checker_output.get('empty_subsections', []):
        return_str += f"  {sub} (empty {count})\n"
    return return_str

@log_time
def parse_date(date_str):
    """
    Parse a date string in the format 'Year/Month' and return a datetime.date object.
    """
    print("[DEBUG] parse_date")
    year, month = map(int, date_str.split('/'))
    return datetime.date(year, month, 1)

@log_time
def parse_duration(duration_str):
    """
    Parse a duration string in the format 'Start Year/Start Month - End Year/End Month'
    and return a tuple of start and end dates as datetime.date objects.
    Output is a tuple of datetime.date objects.
    """
    print("[DEBUG] parse_duration")
    start_str, end_str = duration_str.split(' - ')
    if start_str:
        start_date = parse_date(start_str)
    else:
        start_date = None
    if end_str:
        if end_str.strip().lower() in ["present","current"]:
            end_date = datetime.date.today()
        else:
            end_date = parse_date(end_str)
    else:
        end_date = None
    return start_date, end_date

@log_time
def order_section(section, type_key = 'end_date', reverse = False):
    """
    Order the items in a section based on their start and end dates.
    """
    print("[DEBUG] order_section")
    allowed_sections1 = ['education', 'work_experience', 'projects', 'volunteering_and_leadership']
    allowed_sections2 = ['certifications', 'awards_and_scholarships']
    allowed_keys = ['start_date', 'end_date', 'issue_date']
    #Section is a dictionary of the form {'key': list of things that need to be ordered}
    #first determine if the sole key in dictionary is in one of the allowed sections
    if len(section) != 1:
        raise ValueError("Section must be a dictionary with a single key.")
    else:
        key = next(iter(section))
        if key in allowed_sections1:
            if type_key not in allowed_keys[0:2]:
                raise ValueError(f"Invalid type_key for section '{key}'. Choose from {allowed_keys[0:2]}.")
            # Handle allowed_sections1
            else:
                items = section[key] #list of dictionaries to be sorted
                if type_key == 'start_date':
                    items.sort(reverse=reverse, key=lambda x: parse_duration(x['duration'])[0])
                    return items                           
                elif type_key == 'end_date':
                    items.sort(reverse=reverse, key=lambda x: parse_duration(x['duration'])[1])
                    return items

        elif key in allowed_sections2:
            if type_key not in allowed_keys[2:]:
                raise ValueError(f"Invalid type_key for section '{key}'. Choose from {allowed_keys[2:]}.")
            # Handle allowed_sections2
            else:
                items = section[key] #list of dictionaries to be sorted
                if type_key == 'issue_date':
                    items.sort(reverse=reverse, key=lambda x: parse_date(x['issue_date']))
                    return items

        else:
            raise ValueError("Invalid section. Choose from 'education', 'work_experience', 'projects', 'volunteering_and_leadership', 'certifications', or 'awards_and_scholarships'.")

@log_time
def order_chronologically(cv_dict, mode = 'end_date', reverse = False):
    """
    This will be called once the CV is tailored and the final dict is ready.
    Mode can be 'end_date', 'start_date' or 'issue_date'.
    Orders the resume entries in cv_dict chronologically based on the specified mode.
    Particularly, on the following keys:

    (only works with mode set to 'start_date' or 'end_date')
    - education
    - work_experience
    - projects
    - volunteering_and_leadership

    (only works with mode set to 'issue_date')
    - certifications
    - awards_and_scholarships

    If any of the entries in the first 4 sections (education, work_experience, projects, volunteering_and_leadership)
     lack a start_date OR end_date, and the missing date is the opposite of the mode, the available date will be used for ordering.
    
    If any of the entries in the first 4 sections (education, work_experience, projects, volunteering_and_leadership)
     lack both start_date and end_date, the entry will be pushed to the end.

    If any of the entries in the last 2 sections (certifications, awards_and_scholarships)
     lack an issue_date, the entry will be pushed to the end. 
    
    The input cv_dict is modified in place, and the ordered sections are returned. This is its format:
        {
            'name': 'Name',
            'contact_information': {
                'address': 'Address, City, Country',
                'phone': 'Phone Number',
                'email': 'E-Mail Address',
                'linkedin': 'LinkedIn Link',
                'github': 'Github Link',
                'portfolio': 'Portfolio Link'
            },
            'title': 'Title ( Software Engineer, etc.)',
            'summary': 'Summary.',
            'languages': ['Language 1', 'Language 2', ..., 'Language N'],
            'education': [
                {
                    'degree': 'Degree 1',
                    'university': 'Issuing University 1',
                    'location': 'City 1, Country 1',
                    'duration': 'Start Year 1/Start Month 1 - End Year 1/End Month 1',
                    'courses': ['Course 1', ..., 'Course N']
                },
                ...
                {
                    'degree': 'Degree N',
                    'university': 'Issuing University N',
                    'location': 'City N, Country N',
                    'duration': 'Start Year N/Start Month N - End Year N/End Month N',
                    'courses': ['Course N1', ..., 'Course NN']
                }
            ],
            'certifications': [
                {
                    'certification_name': 'Certification Name 1',
                    'issuing_organization': 'Issuing Organization 1',
                    'issue_date': 'Issue Year 1/Issue Month 1'
                },
                ...
                {
                    'certification_name': 'Certification Name N',
                    'issuing_organization': 'Issuing Organization N',
                    'issue_date': 'Issue Year N/Issue Month N'
                }
            ],
            awards_and_scholarships: [
                {
                    'award_name': 'Award Name 1',
                    'issuing_organization': 'Issuing Organization 1',
                    'issue_date': 'Issue Year 1/Issue Month 1'
                },
                ...
                {
                    'award_name': 'Award Name N',
                    'issuing_organization': 'Issuing Organization N',
                    'issue_date': 'Issue Year N/Issue Month N'
                }
            ],
            'volunteering_and_leadership': [
                {
                    'role': 'Role Name 1',
                    'organization': 'Organization Name 1',
                    'location': 'City 1, Country 1',
                    'duration': 'Start Year 1/Start Month 1 - End Year 1/End Month 1',
                    'description': 'Brief description of the role and responsibilities for Role 1.',
                },
                ...
                {
                    'role': 'Role Name N',
                    'organization': 'Organization Name N',
                    'location': 'City N, Country N',
                    'duration': 'Start Year N/Start Month N - End Year N/End Month N',
                    'description': 'Brief description of the role and responsibilities for Role N.',
                }
            ],
            'work_experience': [
                {
                    'job_title': 'Job Title 1',
                    'company': 'Company 1',
                    'location': 'City 1, Country 1',
                    'duration': 'Start Year 1/Start Month 1 - End Year 1/End Month 1',
                    'description': 'Brief description of the role and responsibilities for Role 1.',
                },
                ...
                {
                    'job_title': 'Job Title N',
                    'company': 'Company N',
                    'location': 'City N, Country N',
                    'duration': 'Start Year N/Start Month N - End Year N/End Month N',
                    'description': 'Brief description of the role and responsibilities for Role N.',
                }
            ],
            'projects': [
                {
                    'project_title': 'Project Title 1',
                    'type': 'Type of Project 1 (e.g., Personal, Academic, Professional)',
                    'duration': 'Start Year 1/Start Month 1 - End Year 1/End Month 1',
                    'description': 'Brief description of the role and responsibilities for Role 1.',
                },
                ...
                {
                    'project_title': 'Project Title N',
                    'type': 'Type of Project N (e.g., Personal, Academic, Professional)',
                    'duration': 'Start Year N/Start Month N - End Year N/End Month N',
                    'description': 'Brief description of the role and responsibilities for Role N.',
                }
            ],
            'skills': {
                'programming_languages': ['Programming Language 1', ..., 'Programming Language N'],
                'technical_skills': ['Event Technical Skill 1', ..., 'Technical Skill N'],
                'soft_skills': ['Soft Skill 1', ..., 'Soft Skill N']
            }
        }

    """
    print(f"[DEBUG] order_chronologically: Starting with mode {mode}")
    if mode not in ['start_date', 'end_date', 'issue_date']:
        raise ValueError("Invalid mode. Choose from 'start_date', 'end_date', or 'issue_date'.")
    return_dict = cv_dict.copy()  # Create a copy of the input dictionary to avoid modifying the original

    # Order each section based on the specified mode
    for entry in return_dict:
        print(f"[DEBUG] order_chronologically: {entry} with content {return_dict[entry]}")
        temp_mode = mode
        if entry in ['certifications', 'awards_and_scholarships']:
            temp_mode = 'issue_date'
        temp_dct_cpy = {entry: return_dict[entry]}
        return_dict[entry] = order_section(temp_dct_cpy, type_key=temp_mode, reverse=reverse)
        print(f"[DEBUG] order_chronologically: {entry} with ordered content {return_dict[entry]}")
    return return_dict

@log_time
def label_repeated_experiences(cv_text):
    #Given a complete resume text:
    #Transform to dct
    resume_dct =parsers.parse_cv(cv_text)
    #Scan keys that have lists as their value
    for key, value in resume_dct.items():
        if isinstance(value, list):
            #Add a [XX] label at the end of each entry, corresponding to the times its repeated
            if key in ['education', 'certifications', 'awards_and_scholarships', 'work_experience', 'projects', 'volunteering_and_leadership']:
                #Create dict of labels, along with the number of occurrences
                labels = {}
                label_dct = {
                    'education': 'degree',
                    'certifications': 'certification_name',
                    'awards_and_scholarships': 'award_name',
                    'volunteering_and_leadership': 'role',
                    'work_experience': 'job_title',
                    'projects': 'project_title'
                }
                for item in value:
                    strp = item[label_dct[key]].strip()
                    labels[strp] = labels.get(strp, 0) + 1
                #Scan value and add a [X] label at the end of entry that matches with an object in labels
                for item in value:
                    strp = item[label_dct[key]].strip()
                    if strp in labels:
                        if labels[strp] > 1:
                            item[label_dct[key]] = strp + f"({labels[strp]-1})"
                            labels[strp] -= 1
                        else:
                            continue
    return_txt = parsers.inv_parse_cv(resume_dct)
    return return_txt

    #Transform back to text

@log_time
def clean_labels(cv_text):
    #Remove all [X] labels from the text
    #Search lines in cv_text for the pattern (digit)
    lines = cv_text.splitlines()
    for line in lines:
        if re.search(r"\(\d+\)", line):
            line = re.sub(r"\(\d+\)", "", line)
    return_txt = "\n".join(lines).strip()
    return return_txt