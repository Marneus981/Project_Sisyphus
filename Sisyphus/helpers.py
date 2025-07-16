import os
from Sisyphus import parsers, runLocalModel
def read_text_file(file_path):
    """
    Reads a text file from the given file location and returns its contents as a string.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()



def list_text_files(folder_path):
    """
    Returns a list of strings denoting the text files present in the given folder.
    """
    return [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f.lower().endswith('.txt')]

def list_docx_files(folder_path):
    """
    Returns a list of strings denoting the docx files present in the given folder.
    """
    return [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f.lower().endswith('.docx')]

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

def refresh_options():
    print("Refreshing options...")
    # Fetch available models, systems, and CVs
    models = runLocalModel.fetch_available_ollama_models()
    systems = list_text_files("Sisyphus/systems")
    cvs = list_text_files("Sisyphus/cvs")
    templates = list_docx_files("Sisyphus/templates")
    saved_outs = list_text_files("Sisyphus/saved_outputs")
    print("Options refreshed:")
    print("Models:", models)
    print("Systems:", systems)
    print("CVs:", cvs)
    print("Templates:", templates)
    print("Previously Saved Outputs:", saved_outs)
    return [models, systems, cvs, templates, saved_outs]

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

def filter_output(model_output):
    """
    Filters model output, keeping only lines that start with [X], where X is a number (e.g., [0], [1], etc.).
    Returns the filtered output as a string.
    """
    filtered_lines = []
    for line in model_output.splitlines():
        line = line.strip()
        if line.startswith("[") and len(line) > 2 and line[2] == "]" and line[1].isdigit():
            filtered_lines.append(line)
    return "\n".join(filtered_lines)

def read_format_checker(format_checker_output):
    """
    Prints out sequentially:
    - Names of missing sections
    - Names of empty sections
    - Names and number of missing subsections
    - Names and number of empty subsections
    """
    print("Missing Sections:")
    for section in format_checker_output.get('missing_sections', []):
        print(f"  {section}")
    print("\nEmpty Sections:")
    for section in format_checker_output.get('empty_sections', []):
        print(f"  {section}")
    print("\nMissing Subsections:")
    for sub, count in format_checker_output.get('missing_subsections', []):
        print(f"  {sub} (missing {count})")
    print("\nEmpty Subsections:")
    for sub, count in format_checker_output.get('empty_subsections', []):
        print(f"  {sub} (empty {count})")