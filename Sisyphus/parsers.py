#CV Parser
#Expected input: CV in text format
#Expected output: Parsed CV data in a structured format
#The idea is to support both a UI for manual input (each field) and a raw text input for parsing.
import re
def parse_cv(cv_text):
    """
    Parses a CV in text format and returns structured data.
    
    Args:
        cv_text (str): The CV text to parse.
        
    Returns:
        dict: A dictionary containing parsed CV data.
    """
    cv_data = {}
    
    # Example parsing logic
    #name_match = re.search(r'Name:\s*(.*)', cv_text)
    #if name_match:
        #cv_data['name'] = name_match.group(1).strip()

    # Fields to parse:
    # - Name
    # - Languages
    # - Contact Information
        # - Address
        # - Phone
        # - Email
        # - LinkedIn
        # - Github
        # - Portfolio
    # - Title
    # - Summary
    # - Education
        # - Education X
            # - Degree
            # - University
            # - Location
            # - Duration
            # - Courses
    # - Certifications
        # - Certification X
            # - Certification Name
            # - Issuing Organization
            # - Issue Date
    # - Awards and Scholarships
        # - Award X
            # - Award Name
            # - Issuing Organization
            # - Issue Date
    # - Volunteering and Leadership
        # - Volunteering X
            # - Role
            # - Organization
            # - Location
            # - Duration
            # - Description
            # - Skills
                # - Programming Languages
                # - Technical Skills
                # - Soft Skills
    # - Work Experience
        # - Work Experience X
            # - Job Title
            # - Company
            # - Location
            # - Duration
            # - Description
            # - Skills
                # - Programming Languages
                # - Technical Skills
                # - Soft Skills
    # - Projects
        # - Project X
            # - Project Title
            # - Type (e.g., Personal, Academic, Professional)
            # - Duration
            # - Description
            # - Skills     
                # - Programming Languages
                # - Technical Skills
                # - Soft Skills


    # - To make parsing simpler, every field will have [X]field_name at the start of the line; X represents the parent order.
    # - The first field will be [0]Name, followed by [0]Contact Information, and so on.
    # - Each Field and Subfield will start on a new line.
    # - Each field will be followed by a colon and the content.
    # - Example:
    #   [0]Name: John Doe
    #   [0]Contact Information:
        #   [1]Address: 123 Main St, City, Country
        #   [1]Phone: +1234567890
        #   [1]Email: jd@hotmail.com
        #   [1]LinkedIn: https://linkedin.com/in/johndoe
        #   [1]Github: https://github.com/johndoe
        #   [1]Portfolio: https://johndoe.com

    # - The output will be a dictionary with the following structure:
    #   {
    #       'name': 'John Doe',
    #       'contact_information': {
    #           'address': '123 Main St, City, Country',
    #           'phone': '+1234567890',
    #           'email': '
    #           'linkedin': 'https://linkedin.com/in/johndoe',
    #           'github': '
    #           'portfolio': 'https://johndoe.com'
    #       },
    #       'title': 'Software Engineer',
    #       'summary': 'Experienced software engineer with a passion for developing innovative solutions.',
    #       'education': [
    #           {
    #               'degree': 'Bachelor of Science in Computer Science',
    #               'university': 'University of Example',
    #               'location': 'City, Country',
    #               'duration': '2015 - 2019'
    #           },
    #           {
    #               'degree': 'Master of Science in Software Engineering',
    #               'university': 'Example University',
    #               'location': 'City, Country',
    #               'duration': '2019 - 2021'
    #           }
    #       ],
    #       ETC.

    #Code to parse the CV text
    lines = cv_text.splitlines()
    parent_field = None
    current_list = None
    last_entry = None
    allowed_parents = [
        'name', 'languages', 'contact_information', 'title', 'summary',
        'education', 'certifications', 'awards_and_scholarships',
        'volunteering_and_leadership', 'work_experience', 'projects'
    ]
    allowed_subfields = {
        'contact_information': ['address', 'phone', 'email', 'linkedin', 'github', 'portfolio'],
        'education': ['degree', 'university', 'location', 'duration', 'courses'],
        'certifications': ['certification_name', 'issuing_organization', 'issue_date'],
        'awards_and_scholarships': ['award_name', 'issuing_organization', 'issue_date'],
        'volunteering_and_leadership': ['role', 'organization', 'location', 'duration', 'description', 'skills'],
        'work_experience': ['job_title', 'company', 'location', 'duration', 'description', 'skills'],
        'projects': ['project_title', 'type', 'duration', 'description', 'skills']
    }
    for line in lines:
        line = line.strip()
        if not line:
            continue
        parent_match = re.match(r'\[0\](\w[\w ]*):\s*(.*)', line)
        if parent_match:
            field, value = parent_match.groups()
            field_key = field.lower().replace(' ', '_')
            if field_key not in allowed_parents:
                continue
            if field_key == 'contact_information':
                cv_data[field_key] = {}
                parent_field = field_key
                current_list = None
            elif field_key in ['education', 'certifications', 'awards_and_scholarships', 'volunteering_and_leadership', 'work_experience', 'projects']:
                cv_data[field_key] = []
                parent_field = field_key
                current_list = cv_data[field_key]
                last_entry = None
            elif field_key == 'languages':
                cv_data[field_key] = [s.strip() for s in value.split(',') if s.strip()]
                parent_field = field_key
                current_list = None
            else:
                cv_data[field_key] = value
                parent_field = field_key
                current_list = None
            continue
        sub_match = re.match(r'\[1\](\w[\w ]*):\s*(.*)', line)
        if sub_match:
            field, value = sub_match.groups()
            field_key = field.lower().replace(' ', '_')
            if parent_field in allowed_subfields:
                if field_key not in allowed_subfields[parent_field]:
                    continue
            if parent_field == 'contact_information':
                cv_data[parent_field][field_key] = value
            elif parent_field == 'education':
                if field_key == 'degree' or last_entry is None:
                    last_entry = {}
                    current_list.append(last_entry)
                if field_key == 'courses':
                    last_entry['courses'] = [c.strip() for c in value.split(',') if c.strip()]
                else:
                    last_entry[field_key] = value
            elif parent_field in ['certifications', 'awards_and_scholarships']:
                if field_key in ['certification_name', 'award_name'] or last_entry is None:
                    last_entry = {}
                    current_list.append(last_entry)
                last_entry[field_key] = value
            elif parent_field in ['volunteering_and_leadership', 'work_experience', 'projects']:
                if field_key in ['role', 'job_title', 'project_title'] or last_entry is None:
                    last_entry = {}
                    current_list.append(last_entry)
                if field_key == 'skills':
                    skills_dict = {}
                    for skill_line in value.split(';'):
                        if ':' in skill_line:
                            cat, vals = skill_line.split(':', 1)
                            cat_key = cat.strip().lower().replace(' ', '_')
                            if cat_key in ['programming_languages', 'technical_skills', 'soft_skills']:
                                skills_dict[cat_key] = [s.strip() for s in vals.split(',') if s.strip()]
                    last_entry['skills'] = skills_dict
                else:
                    last_entry[field_key] = value
            continue
    return cv_data

def inv_parse_cv(cv_dict):
    """
    Converts a cv_dict dictionary back to multiline text in the format expected by parse_cv.
    Each field/subfield is written on a new line, with [0] for parent fields and [1] for subfields.
    """
    def format_key(key, parent_key=None):
        # Special case for LinkedIn under Contact Information
        if parent_key == 'contact_information' and key.lower() == 'linkedin':
            return 'LinkedIn'
        # Title-case except for 'and' (keep lowercase)
        words = key.replace('_', ' ').split()
        formatted = []
        for w in words:
            if w.lower() == 'and':
                formatted.append('and')
            else:
                formatted.append(w.capitalize())
        return ' '.join(formatted)

    lines = []
    for parent_key, parent_value in cv_dict.items():
        parent_field = format_key(parent_key)
        if isinstance(parent_value, dict):
            lines.append(f"[0]{parent_field}:")
            for sub_key, sub_value in parent_value.items():
                sub_field = format_key(sub_key, parent_key)
                lines.append(f"[1]{sub_field}: {sub_value}")
        elif isinstance(parent_value, list):
            #List of Dictionaries or List of Strings
            if parent_key in ['education', 'certifications', 'awards_and_scholarships', 'volunteering_and_leadership', 'work_experience', 'projects']:
                lines.append(f"[0]{parent_field}:")
                for entry in parent_value:
                    if isinstance(entry, dict):
                        for sub_key, sub_value in entry.items():
                            sub_field = format_key(sub_key)
                            if isinstance(sub_value, list):
                                # For lists (e.g., courses, languages, skills)
                                lines.append(f"[1]{sub_field}: {', '.join(str(v) for v in sub_value)}")
                            elif isinstance(sub_value, dict):
                                # For skills dict
                                skill_lines = []
                                for skill_cat, skill_list in sub_value.items():
                                    skill_cat_field = format_key(skill_cat)
                                    skill_lines.append(f"{skill_cat_field}: {', '.join(str(s) for s in skill_list)}")
                                lines.append(f"[1]{sub_field}: {'; '.join(skill_lines)}")
                            else:
                                lines.append(f"[1]{sub_field}: {sub_value}")

            else:
                lines.append(f"[0]{parent_field}: {', '.join(str(v) for v in parent_value)}")

        else:
            lines.append(f"[0]{parent_field}: {parent_value}")
    return '\n'.join(lines)

def dict_spliter(cv_dict):
    """
    Splits a cv_dict dictionary into multiple dictionaries, each containing one field.
    
    Args:
        cv_dict (dict): The CV dictionary to split.
        
    Returns:
        list: A list of dictionaries, each containing one field from the CV.
    """
    split_dicts = []
    for key, value in cv_dict.items():
        if isinstance(value, dict):
            # Convert sub-dictionary to a single dictionary with the parent key
            new_dict = {key: value}
            split_dicts.append(new_dict)
        elif isinstance(value, list):
            # Convert list to a dictionary with the parent key
            new_dict = {key: value}
            split_dicts.append(new_dict)
        else:
            # Single value case
            new_dict = {key: value}
            split_dicts.append(new_dict)
    return split_dicts

def dict_grafter(split_dicts):
    """
    Grafts a list of dictionaries back into a single CV dictionary.
    
    Args:
        split_dicts (list): A list of dictionaries to graft.
        
    Returns:
        dict: A single dictionary containing all fields from the split dictionaries.
    """
    cv_dict = {}
    for d in split_dicts:
        for key, value in d.items():
            if key in cv_dict:
                if isinstance(cv_dict[key], list):
                    cv_dict[key].append(value)
                else:
                    cv_dict[key] = [cv_dict[key], value]
            else:
                cv_dict[key] = value
    return cv_dict
