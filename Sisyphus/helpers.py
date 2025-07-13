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

def format_output(dict):
    """
    Formats keys in cv dict in the following order, returning a string:
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
        if key in dict:
            output +=  parsers.inv_parse_cv({key: dict[key]})
            output += "\n"
    return output

def refresh_options():
    print("Refreshing options...")
    # Fetch available models, systems, and CVs
    models = runLocalModel.fetch_available_ollama_models()
    systems = list_text_files("Sisyphus/systems")
    cvs = list_text_files("Sisyphus/cvs")
    print("Options refreshed:")
    print("Models:", models)
    print("Systems:", systems)
    print("CVs:", cvs)
    return [models, systems, cvs]
    