from Sisyphus import runLocalModel, parsers, tailor, helpers
import os
import tkinter as tk
from tkinter import ttk

SISYPHUS_PATH = r"C:\CodeProjects\Sisyphus\Sisyphus"

def tailor_cv(root):
    selected_model = model_var.get()
    cv_file = cv_var.get()
    system_file = system_var.get()
    cv_text = helpers.read_text_file(os.path.join(SISYPHUS_PATH, "cvs", cv_file)) if cv_file else ""
    system_text = helpers.read_text_file(os.path.join(SISYPHUS_PATH, "systems", system_file)) if system_file else ""
    
    job_desc = job_desc_textbox.get("1.0", tk.END)
    print("Selected Model:", selected_model)
    print("CV Text:", cv_text)
    print("System:", system_text)
    print("Job Description:", job_desc)
    # Here you can call your tailoring functions

    cv_dict = parsers.parse_cv(cv_text)
    unchanged_dict = {}
    # Copy over unchanged fields
    print("Fetching unchanged fields...")
    for key in [
        'name',
        'contact_information',
        'languages',
        'education',
        'certifications',
        'awards_and_scholarships'
    ]:
        if key in cv_dict:
            print(f"Found field: {key} Keeping unchanged field: {key}")
            unchanged_dict[key] = cv_dict[key]

    

    # Tailor each remaining section
    tailored_list = []
    cv_fields = parsers.dict_spliter(cv_dict)
    v_and_l_section = None
    w_section = None
    p_section = None
    s_section = None
    print("Searching fields to tailor...")
    for field in cv_fields:
        if 'volunteering_and_leadership' in field:
            print("Found volunteering_and_leadership section")
            v_and_l_section = {'volunteering_and_leadership':  field['volunteering_and_leadership']}

        if 'work_experience' in field:
            print("Found work_experience section")
            w_section = {'work_experience': field['work_experience']}

        if 'projects' in field:
            print("Found projects section")
            p_section = {'projects': field['projects']}

        if 'summary' in field:
            print("Found summary section")
            s_section = {'summary': field['summary']}

    # Tailor each section if it exists
    print("Tailoring sections...")
    if v_and_l_section:
        print("Tailoring volunteering and leadership section...")
        v_and_l_text = parsers.inv_parse_cv(v_and_l_section)
        tailored_v_and_l = tailor.tailor_volunteering_and_leadership(
            model=selected_model,
            system=system_text,
            cv_data=v_and_l_text,
            job_description=job_desc
        )
        if tailored_v_and_l:
            print("Tailored volunteering and leadership section:", tailored_v_and_l)
        tailored_list.append({'volunteering_and_leadership': tailored_v_and_l})
    if w_section:
        print("Tailoring work experience section...")
        w_text = parsers.inv_parse_cv(w_section)
        tailored_w = tailor.tailor_work_experience(
            model=selected_model,
            system=system_text,
            cv_data=w_text,
            job_description=job_desc
        )
        if tailored_w:
            print("Tailored work experience section:", tailored_w)
        tailored_list.append({'work_experience': tailored_w})
    if p_section:
        print("Tailoring projects section...")
        p_text = parsers.inv_parse_cv(p_section)
        tailored_p = tailor.tailor_projects(
            model=selected_model,
            system=system_text,
            cv_data=p_text,
            job_description=job_desc
        )
        if tailored_p:
            print("Tailored projects section:", tailored_p)
        tailored_list.append({'projects': tailored_p})
    tailored_dict = parsers.dict_grafter(tailored_list)
    # Merge unchanged fields back into the tailored dict
    for key, value in unchanged_dict.items():
        tailored_dict[key] = value
    # Convert the tailored dict back to text
    s_text = parsers.inv_parse_cv(tailored_dict)
    if s_section:
        print("Tailoring summary section...")
        tailored_s = tailor.tailor_summary(
            model=selected_model,
            system=system_text,
            cv_data=s_text,
            job_description=job_desc
        )
        if tailored_s:
            print("Tailored summary section:", tailored_s)
        tailored_dict['summary'] = tailored_s
    final_cv_text = helpers.format_output(tailored_dict)
    print("The climb has ended, the CV is tailored!")
    # Show the tailored CV text in a new window
    result_window = tk.Toplevel(root)
    result_window.title("Tailored CV")
    result_textbox = tk.Text(result_window, height=20, width=80)
    result_textbox.insert(tk.END, final_cv_text)
    result_textbox.pack(expand=True, fill=tk.BOTH)

def main():

    

    run = runLocalModel.wait_for_ollama()
    if not run:
        print("Ollama server is not running. Starting Ollama.")
        runLocalModel.start_ollama_server()
        run = runLocalModel.wait_for_ollama()
        if not run:
            print("Failed to start Ollama server.")
            return 1
    models = runLocalModel.fetch_available_ollama_models()
    systems = helpers.list_text_files("Sisyphus/systems")
    cvs = helpers.list_text_files("Sisyphus/cvs")
    # Initialize the main application window
    root = tk.Tk()
    root.title("Sisyphus Resume Tailor")

    #On start up show a window with the following:
    global model_var, cv_var, system_var, job_desc_textbox
    #1. Dropdown to select Ollama model (must detect initialize server and scan for available models)
    # Dropdown for models
    
    model_var = tk.StringVar()
    if model_var:
        model_var.set(models[0])
    model_dropdown = ttk.Combobox(root, textvariable=model_var, values=models)
    model_dropdown.grid(row=0, column=1)
    ttk.Label(root, text="Select Model:").grid(row=0, column=0)

    #Dropdown for system
    
    system_var = tk.StringVar()
    if system_var:
        system_var.set(systems[0])
    system_dropdown = ttk.Combobox(root, textvariable=system_var, values=systems)
    system_dropdown.grid(row=1, column=1)
    ttk.Label(root, text="Select System:").grid(row=1, column=0)
    

    #Dropdown for cv

    cv_var = tk.StringVar()
    if cv_var:
        cv_var.set(cvs[0])
    cv_dropdown = ttk.Combobox(root, textvariable=cv_var, values=cvs)
    cv_dropdown.grid(row=2, column=1)
    ttk.Label(root, text="Select CV File:").grid(row=2, column=0)
    




    #2. 1 Text fields:
        #Job Description
    # Text fields
    # ttk.Label(root, text="CV Text:").grid(row=2, column=0)
    # cv_textbox = tk.Text(root, height=5, width=40)
    # cv_textbox.grid(row=2, column=1)

    # ttk.Label(root, text="System:").grid(row=2, column=0)
    # system_textbox = tk.Text(root, height=2, width=40)
    # system_textbox.grid(row=2, column=1)

    ttk.Label(root, text="Job Description:").grid(row=3, column=0)
    job_desc_textbox = tk.Text(root, height=5, width=40)
    job_desc_textbox.grid(row=3, column=1)




    #3. 1 Buttons:
        #Tailor CV

    # Button
    tailor_button = ttk.Button(root, text="Tailor CV", command=lambda: tailor_cv(root))
    tailor_button.grid(row=4, column=1)

    #Show the window
    root.mainloop()
 
if __name__ == "__main__":
    main()