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
    # - Work Experience
        # - Work Experience X
            # - Job Title
            # - Company
            # - Location
            # - Duration
            # - Description
    # - Projects
        # - Project X
            # - Project Title
            # - Type (e.g., Personal, Academic, Professional)
            # - Duration
            # - Description
    # - Skills
        # - Languages
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
    for line in lines:
        line = line.strip()
        if not line:
            continue
        parent_match = re.match(r'\[0\](\w[\w ]*):\s*(.*)', line)
        if parent_match:
            field, value = parent_match.groups()
            field_key = field.lower().replace(' ', '_')
            if field_key == 'contact_information':
                cv_data[field_key] = {}
                parent_field = field_key
                current_list = None
            elif field_key in ['education', 'certifications', 'awards_and_scholarships', 'volunteering_and_leadership', 'work_experience', 'projects']:
                cv_data[field_key] = []
                parent_field = field_key
                current_list = cv_data[field_key]
                last_entry = None
            elif field_key == 'skills':
                cv_data[field_key] = {}
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
            if parent_field == 'contact_information':
                cv_data[parent_field][field_key] = value
            elif parent_field in ['education', 'certifications', 'awards_and_scholarships', 'volunteering_and_leadership', 'work_experience', 'projects']:
                # If starting a new entry (first field in group), create new dict
                if field_key in ['degree', 'certification_name', 'award_name', 'role', 'job_title', 'project_title'] or last_entry is None:
                    last_entry = {}
                    current_list.append(last_entry)
                last_entry[field_key] = value
            elif parent_field == 'skills':
                # Split skills by comma and strip whitespace
                cv_data[parent_field][field_key] = [s.strip() for s in value.split(',') if s.strip()]
            continue
    return cv_data