from Sisyphus import runLocalModel, parsers, tailor, helpers
import os
import tkinter as tk
from tkinter import ttk
import io
import sys
import Sisyphus.fileGenerator as fileGenerator
import datetime
import logging


SISYPHUS_PATH = r"C:\CodeProjects\Sisyphus\Sisyphus"
DOCS_PATH =r"C:\CodeProjects\Sisyphus\Sisyphus\saved_docs"
OUT_CV_PATH = r"C:\CodeProjects\Sisyphus\Sisyphus\saved_outputs"
OUT_CL_PATH = r"C:\CodeProjects\Sisyphus\Sisyphus\saved_outputs_cl"

# Create a logs directory if it doesn't exist
log_dir = os.path.join(SISYPHUS_PATH, "log")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"run_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Replace all print statements with logging.info, logging.warning, etc. as needed.
print = logging.info

def tailor_cv(root):
    global tailor_cl_button
    global format_check_current_cv_button, filter_output_cv_button, current_cv_text
    selected_model = model_var.get()
    cv_file = cv_var.get()
    system_file = system_var.get()    
    job_desc = job_desc_textbox.get("1.0", tk.END)

    if not job_desc.strip():
        print("Job description is empty. Please enter a job description.")
        return
    if not selected_model:
        print("No model selected. Please select a model.")
        return
    if not cv_file:
        print("No CV file selected. Please select a CV file.")
        return
    if not system_file:
        print("No system file selected. Please select a system file.")
        return



    cv_text = helpers.read_text_file(os.path.join(SISYPHUS_PATH, "cvs", cv_file))
    system_text = helpers.read_text_file(os.path.join(SISYPHUS_PATH, "systems", system_file))

    print("Selected Model: \n" + str(selected_model))
    print("CV Text: \n" + helpers.indent_text(str(cv_text)))
    print("System: \n" + str(system_text))
    print("Job Description: \n" + str(job_desc))
    # Here you can call your tailoring functions

    cv_dict = parsers.parse_cv(cv_text)
    unchanged_dict = {}
    # Copy over unchanged fields
    print("Fetching unchanged fields...")
    for key in [
        'name',
        'contact_information',
        'title',
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
    # s_section = None
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

        # if 'summary' in field:
        #     print("Found summary section")
        #     s_section = {'summary': field['summary']}

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
        tailored_v_and_l = helpers.filter_output(tailored_v_and_l)
        if tailored_v_and_l:
            print("Tailored volunteering and leadership section")
            tailored_list.append(parsers.parse_cv(tailored_v_and_l))
            # tailored_list.append({'volunteering_and_leadership': tailored_v_and_l})
    if w_section:
        print("Tailoring work experience section...")
        w_text = parsers.inv_parse_cv(w_section)
        tailored_w = tailor.tailor_work_experience(
            model=selected_model,
            system=system_text,
            cv_data=w_text,
            job_description=job_desc
        )
        tailored_w = helpers.filter_output(tailored_w)
        if tailored_w:
            print("Tailored work experience section")
            tailored_list.append(parsers.parse_cv(tailored_w))
            # tailored_list.append({'work_experience': tailored_w})
    if p_section:
        print("Tailoring projects section...")
        p_text = parsers.inv_parse_cv(p_section)
        tailored_p = tailor.tailor_projects(
            model=selected_model,
            system=system_text,
            cv_data=p_text,
            job_description=job_desc
        )
        tailored_p = helpers.filter_output(tailored_p)
        if tailored_p:
            print("Tailored projects section")
            tailored_list.append(parsers.parse_cv(tailored_p))
            # tailored_list.append({'projects': tailored_p})
    tailored_dict = parsers.dict_grafter(tailored_list)
    # Merge unchanged fields back into the tailored dict
    for key, value in unchanged_dict.items():
        tailored_dict[key] = value


    # Convert the tailored dict back to text (no summary section yet)
    s_text = parsers.inv_parse_cv(tailored_dict)

    print("Resume before pruning (And before Summary): \n" + helpers.indent_text(str(s_text)))


    #Prune Volunteering and Leadership, Work Experience and Projects sections based on job description
    print("Pruning following sections: Volunteering and Leadership, Work Experience and Projects...")

    #Extract Volunteering and Leadership, Work Experience and Projects sections from the final CV text
    volunteering_and_leadership = tailored_dict.get("volunteering_and_leadership", {})
    work_experience = tailored_dict.get("work_experience", {})
    projects = tailored_dict.get("projects", {})
    #Graft to a single dict
    experiences = {
        "volunteering_and_leadership": volunteering_and_leadership,
        "work_experience": work_experience,
        "projects": projects
    }
    #Convert to text
    experiences_text = parsers.inv_parse_cv(experiences)
    print("Experiences text before pruning: \n" + helpers.indent_text(str(experiences_text)))
    #Prune Volunteering and Leadership, Work Experience and Projects sections based on job description
    pruned_experiences = tailor.prune_vl_w_p(
        model=selected_model,
        system=system_text,
        resume_experiences=experiences_text,
        job_description=job_desc
    )
    print("Remaining experiences before filtering: \n" + helpers.indent_text(str(pruned_experiences)))
    pruned_experiences = helpers.filter_output(pruned_experiences)
    print("Remaining experiences after filtering: \n" + helpers.indent_text(str(pruned_experiences)))
    if pruned_experiences:
##############################################################################
        print("[0]DEBUG")
        pruned_experiences_dict = parsers.parse_cv(pruned_experiences)
        for key in ['volunteering_and_leadership', 'work_experience', 'projects']:
            print("" + key + " section after pruning: " + str(pruned_experiences_dict.get(key, {})))
        #Replace the experiences section in the final tailored dict
        print("[1]DEBUG")
        vnl_s = pruned_experiences_dict.get('volunteering_and_leadership', {})
        print("Volunteering and Leadership section after pruning and .get(): \n" + str(vnl_s))
        tailored_dict['volunteering_and_leadership'] = vnl_s
        w_s = pruned_experiences_dict.get('work_experience', {})
        print("Work Experience section after pruning and .get(): \n" + str(w_s))
        tailored_dict['work_experience'] = w_s
        p_s = pruned_experiences_dict.get('projects', {})
        print("Projects section after pruning and .get(): \n" + str(p_s))
        tailored_dict['projects'] = p_s
        print("[2]DEBUG")
        cv_text0 = parsers.inv_parse_cv(tailored_dict)
        print("[3]DEBUG")
        s_text = helpers.format_output(cv_text0)

##############################################################################
    else:
        print("No experiences section tailored, using original experiences section")


    #Tailor summary section if it exists
    # if s_section:
    print("Tailoring summary section...")
    tailored_s = tailor.tailor_summary(
        model=selected_model,
        system=system_text,
        cv_data=s_text,
        job_description=job_desc
    )
    tailored_s = helpers.filter_output(tailored_s)
    if tailored_s:
        # Add the tailored summary to the dict
        tailored_list.append(parsers.parse_cv(tailored_s))
        #tailored_dict['summary'] = tailored_s
    final_tailored_dict = parsers.dict_grafter(tailored_list)
    #Merge unchanged fields back into the final tailored dict
    for key, value in unchanged_dict.items():
        final_tailored_dict[key] = value

    final_cv_text = helpers.format_output(parsers.inv_parse_cv(final_tailored_dict))


    print("All sections tailored successfully")

    print("CV text before separate skills section: " +  helpers.indent_text(str(final_cv_text)))
    final_final_cv_text = tailor.return_text_with_skills(final_cv_text)
    print("CV text after skills section: " +  helpers.indent_text(str(final_final_cv_text)))
    #Print final_final_cv_text
    # print('Checking tailor.return_text_with_skills output:')
    # print(final_final_cv_text)


    #Attempt to tailor skills section
    p_cv_out = parsers.parse_cv_out(final_final_cv_text)
    #print("p_cv_out: ", p_cv_out)
    final_final_split_dicts = parsers.dict_spliter(p_cv_out)
    #print("final_final_split_dicts: ", final_final_split_dicts)
    sk_text = parsers.inv_parse_cv_out(final_final_split_dicts[-1])
    #print("sk_text:", sk_text)

    
    print("Tailoring skills section...")
    tailored_sk = tailor.tailor_skills(
        model=selected_model,
        system=system_text,
        cv_data=sk_text,
        job_description=job_desc
    )
    tailored_sk = helpers.filter_output(tailored_sk)
    if tailored_sk:
        print("Tailored skills section")
        final_final_split_dicts[-1]= parsers.parse_cv_out(tailored_sk)
        current_cv_text = parsers.inv_parse_cv_out(parsers.dict_grafter(final_final_split_dicts))
    else:
        print("No skills section tailored, using original skills section")
        current_cv_text = final_final_cv_text
    
    print("Ordering Resume sections by end date/issue date...")
    temp_dct = parsers.parse_cv_out(current_cv_text)
    split_curr = parsers.dict_spliter(temp_dct)
    to_be_ordered = []
    for section in split_curr:
        # Check if key is one of the sections to be ordered
        for key in section:
            if key in ['education', 'work_experience', 'projects', 'volunteering_and_leadership', 'certifications', 'awards_and_scholarships']:
                print(f"Found section to order: {key}")
                to_be_ordered.append(section)
    grafted_curr = parsers.dict_grafter(to_be_ordered)
    helpers.order_chronologically(grafted_curr, mode='end_date')
    ordered_curr = grafted_curr
    #Replace all ordered sections from ordered_curr to temp_dct
    if 'education' in ordered_curr:
        temp_dct['education'] = ordered_curr['education']
        print("Ordered education section")
    if 'work_experience' in ordered_curr:
        temp_dct['work_experience'] = ordered_curr['work_experience']
        print("Ordered work experience section")
    if 'projects' in ordered_curr:
        temp_dct['projects'] = ordered_curr['projects']
        print("Ordered projects section")
    if 'volunteering_and_leadership' in ordered_curr:
        temp_dct['volunteering_and_leadership'] = ordered_curr['volunteering_and_leadership']
        print("Ordered volunteering and leadership section")
    if 'certifications' in ordered_curr:
        temp_dct['certifications'] = ordered_curr['certifications']
        print("Ordered certifications section")
    if 'awards_and_scholarships' in ordered_curr:
        temp_dct['awards_and_scholarships'] = ordered_curr['awards_and_scholarships']
        print("Ordered awards and scholarships section")

    current_cv_text = parsers.inv_parse_cv_out(temp_dct)
    print("Ordering complete")
    format_check_current_cv_text(root)

    

    print("The climb has ended, the CV is tailored!")
    # Show the tailored CV text in a new window
    global result_window, result_textbox, show_output_cv_button, save_output_cv_button, save_current_cv_text_button
    
    result_window = tk.Toplevel(root)
    result_window.title("Tailored CV")
    result_textbox = tk.Text(result_window, height=20, width=80)
    result_textbox.insert(tk.END, current_cv_text)
    result_textbox.pack(expand=True, fill=tk.BOTH)
    

    # Enable the save button when output is generated
    show_output_cv_button.config(state="normal")
    save_output_cv_button.config(state="normal")
    save_current_cv_text_button.config(state="normal")
    format_check_current_cv_button.config(state="normal")
    filter_output_cv_button.config(state="normal")
    tailor_cl_button.config(state="normal")


def tailor_cl(root):
    #Assumes existing system
    global filter_output_cl_button
    global save_current_cl_text_button
    global current_cv_text
    global current_cl_text
    global cl_window, cl_textbox
    global show_output_cl_button
    global save_output_cl_button
    global format_check_current_cl_button
    selected_model = model_var.get()  
    job_desc = job_desc_textbox.get("1.0", tk.END)

    if not job_desc.strip():
        print("Job description is empty. Please enter a job description.")
        return
    if not selected_model:
        print("No model selected. Please select a model.")
        return
    if not current_cv_text:
        print("No CV text available. Please tailor a CV first.")
        return
    
    print("Tailoring cover letter with model: " + str(selected_model))

    # Compose cover letter dictionary
    cover_letter_dict = tailor.compose_cover_letter_dictionary(
        model=selected_model,
        cv_text=current_cv_text,
        job_description=job_desc
    )
    cover_letter_text = parsers.inv_parse_cl(cover_letter_dict)
    current_cl_text = cover_letter_text


    print("Cover letter text generated successfully.")

    format_check_current_cl_text(root)

    global cl_window, cl_textbox
    
    cl_window = tk.Toplevel(root)
    cl_window.title("Tailored Cover Letter")
    cl_textbox = tk.Text(cl_window, height=20, width=80)
    cl_textbox.insert(tk.END, current_cl_text)
    cl_textbox.pack(expand=True, fill=tk.BOTH)

    show_output_cl_button.config(state="normal")
    save_current_cl_text_button.config(state="normal")
    filter_output_cl_button.config(state="normal")
    save_output_cl_button.config(state="normal")
    format_check_current_cl_button.config(state="normal")

def show_output_cl(root):
    global cl_window, cl_textbox, current_cl_text
    try:
        # If window exists and is open, update it
        if cl_window.winfo_exists():
            cl_window.title("Tailored Cover Letter")
            cl_textbox.delete("1.0", tk.END)
            cl_textbox.insert(tk.END, current_cl_text)
            cl_window.lift()
        else:
            raise Exception
    except:
        # If window doesn't exist or is closed, create a new one
        cl_window = tk.Toplevel(root)
        cl_window.title("Tailored Cover Letter")
        cl_textbox = tk.Text(cl_window, height=20, width=80)
        cl_textbox.insert(tk.END, current_cl_text)
        cl_textbox.pack(expand=True, fill=tk.BOTH)

def format_check_input_cv_file(root, cv_file):
    """
    Reads a CV file and checks its format.
    Returns True if the format is correct, False otherwise.
    """
    

    cv_text = helpers.read_text_file(os.path.join(SISYPHUS_PATH, "cvs", cv_file))
    
    # Prepare CV analysis output as a string
    analysis_stream = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = analysis_stream
    helpers.read_format_checker(helpers.format_checker(cv_text))
    sys.stdout = old_stdout
    analysis_text = analysis_stream.getvalue()

    # Show the CV analysis in a new window
    analysis_window = tk.Toplevel(root)
    analysis_window.title("Input CV Analysis:")
    analysis_label = tk.Label(analysis_window, text="Input CV Analysis:")
    analysis_label.pack()
    analysis_textbox = tk.Text(analysis_window, height=20, width=80)
    analysis_textbox.insert(tk.END, analysis_text)
    analysis_textbox.pack(expand=True, fill=tk.BOTH)

def format_check_current_cv_text(root):
    if job_desc_textbox.get("1.0", tk.END).strip() == "":
        print("Job description is empty. Please enter a job description.")
        return
    cv_text = current_cv_text

    # Prepare CV analysis output as a string
    analysis_stream = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = analysis_stream
    helpers.read_format_checker(helpers.format_checker_out(cv_text))
    sys.stdout = old_stdout
    analysis_text = analysis_stream.getvalue()
    cv_text_og = helpers.read_text_file(os.path.join(SISYPHUS_PATH, "cvs", cv_var.get()))
    selected_model = model_var.get()
    job_desc = job_desc_textbox.get("1.0", tk.END)
    con_systemm_text = helpers.read_text_file(os.path.join(SISYPHUS_PATH, "systems", "system_consistency.txt"))
    con_vs_job_desc = tailor.consistency_checker_vs_job_desc(
        model=selected_model,
        system=con_systemm_text,
        cv_data=cv_text,
        job_description=job_desc
    )
    con_vs_cv = tailor.consistency_checker_vs_cv(
        model=selected_model,
        system=con_systemm_text,
        cv_data=cv_text,
        cv_data_orig=cv_text_og
    )

    #Append consistency check results to analysis text
    analysis_text += "\n\nConsistency Checker Vs Job Description:\n"
    analysis_text += helpers.filter_output(con_vs_job_desc) + "\n\n"
    analysis_text += "Consistency Checker Vs CV:\n"
    analysis_text += helpers.filter_output(con_vs_cv) + "\n\n"

    # Show the CV analysis in a new window
    analysis_window = tk.Toplevel(root)
    analysis_window.title("Current Output CV Analysis:")
    analysis_label = tk.Label(analysis_window, text="Current Output CV Analysis:")
    analysis_label.pack()
    analysis_textbox = tk.Text(analysis_window, height=20, width=80)
    analysis_textbox.insert(tk.END, analysis_text)
    analysis_textbox.pack(expand=True, fill=tk.BOTH)

def format_check_current_cl_text(root):
    if job_desc_textbox.get("1.0", tk.END).strip() == "":
        print("Job description is empty. Please enter a job description.")
        return
    #Assumes current_cv_text is already defined and is the tailored resume relevant to the cover letter
    cl_text = current_cl_text
    # Prepare CV analysis output as a string
    analysis_stream = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = analysis_stream
    helpers.read_format_checker(helpers.format_checker_out_cl(cl_text))
    sys.stdout = old_stdout
    analysis_text = analysis_stream.getvalue()
    
    cv_text = current_cv_text
    selected_model = model_var.get()
    job_desc = job_desc_textbox.get("1.0", tk.END)

    con_system_text = helpers.read_text_file(os.path.join(SISYPHUS_PATH, "systems", "system_consistency_cl.txt"))
    con_vs_job_desc = tailor.consistency_checker_vs_job_desc(
        model=selected_model,
        system=con_system_text,
        cv_data=cl_text,
        job_description=job_desc,
        type = "CL"
    )
    con_vs_cv = tailor.consistency_checker_vs_cv(
        model=selected_model,
        system=con_system_text,
        cv_data=cl_text,
        cv_data_orig=cv_text,
        type = "CL"
    )

    #Append consistency check results to analysis text
    analysis_text += "\n\nConsistency Checker Vs Job Description:\n"
    analysis_text += helpers.filter_output(con_vs_job_desc) + "\n\n"
    analysis_text += "Consistency Checker Vs Tailored Resume:\n"
    analysis_text += helpers.filter_output(con_vs_cv) + "\n\n"

    # Show the CV analysis in a new window
    analysis_window = tk.Toplevel(root)
    analysis_window.title("Current Output CL Analysis:")
    analysis_label = tk.Label(analysis_window, text="Current Output CL Analysis:")
    analysis_label.pack()
    analysis_textbox = tk.Text(analysis_window, height=20, width=80)
    analysis_textbox.insert(tk.END, analysis_text)
    analysis_textbox.pack(expand=True, fill=tk.BOTH)

def filter_output_cv_text(root):
    global current_cv_text, result_window, result_textbox
    filtered_text = helpers.filter_output(current_cv_text)
    current_cv_text = filtered_text
    try:
        # If window exists and is open, update it
        if result_window.winfo_exists():
            result_window.title("Tailored CV (Filtered)")
            result_textbox.delete("1.0", tk.END)
            result_textbox.insert(tk.END, current_cv_text)
            result_window.lift()
        else:
            raise Exception
    except:
        # If window doesn't exist or is closed, create a new one
        result_window = tk.Toplevel(root)
        result_window.title("Tailored CV (Filtered)")
        result_textbox = tk.Text(result_window, height=20, width=80)
        result_textbox.insert(tk.END, current_cv_text)
        result_textbox.pack(expand=True, fill=tk.BOTH)

def filter_output_cl_text(root):
    global current_cl_text, cl_window, cl_textbox
    filtered_text = helpers.filter_output(current_cl_text)
    current_cl_text = filtered_text
    try:
        # If window exists and is open, update it
        if cl_window.winfo_exists():
            cl_window.title("Tailored Cover Letter (Filtered)")
            cl_textbox.delete("1.0", tk.END)
            cl_textbox.insert(tk.END, current_cl_text)
            cl_window.lift()
        else:
            raise Exception
    except:
        # If window doesn't exist or is closed, create a new one
        cl_window = tk.Toplevel(root)
        cl_window.title("Tailored Cover Letter (Filtered)")
        cl_textbox = tk.Text(cl_window, height=20, width=80)
        cl_textbox.insert(tk.END, current_cl_text)
        cl_textbox.pack(expand=True, fill=tk.BOTH)

def refresh_options_callback():
        global model_dropdown, cv_dropdown, system_dropdown, model_var, models, cv_var, cvs, system_var, systems, template_dropdown,templates, template_var
        global saved_out_dropdown, saved_outs, saved_out_var, load_cv_text_button
        global saved_out_dropdown_cl, saved_outs_cl, saved_out_var_cl, load_cl_text_button
        global cl_template_var, cl_templates, cl_template_dropdown
        options = helpers.refresh_options()
        models = options[0]
        systems = options[1]
        cvs = options[2]
        templates = options[3]
        saved_outs = options[4]
        saved_outs_cl = options[5]
        cl_templates = options[6]
        model_dropdown['values'] = models
        if models:
            model_var.set(models[0])
        system_dropdown['values'] = systems
        if systems:
            system_var.set(systems[0])
        cv_dropdown['values'] = cvs
        if cvs:
            format_check_input_cv_button.config(state="normal")
            cv_var.set(cvs[0])
        template_dropdown['values'] = templates
        if templates:
            template_var.set(templates[0])
        cl_template_dropdown['values'] = cl_templates
        if cl_templates:
            cl_template_var.set(cl_templates[0])
        saved_out_dropdown['values'] = saved_outs
        if saved_outs:
            saved_out_var.set(saved_outs[0])
            load_cv_text_button.config(state="normal")
        saved_out_dropdown_cl['values'] = saved_outs_cl
        if saved_outs_cl:
            saved_out_var_cl.set(saved_outs_cl[0])
            load_cl_text_button.config(state="normal")
        
def save_output_cv(template_name,output_name):
    output_n = output_name
    template_n = template_name.get().strip()
    if output_n == "":
        print("Output file name cannot be empty.")
        return
    if template_n == "":
        print("No template selected. Please select a template.")
        return
    global current_cv_text
    cv_dict = parsers.parse_cv_out(current_cv_text)
    template_path = os.path.join(SISYPHUS_PATH, "templates", f"{template_n}")
    output_path = os.path.join(SISYPHUS_PATH, "saved_docs", f"{output_n}.docx")
    if os.path.exists(output_path):
        print(f"Warning: {output_path} already exists and will be overwritten.")
    fileGenerator.generate_docx(template_path, cv_dict, output_path)

def save_output_cl(template_name, output_name):
    output_n = output_name
    template_n = template_name.get().strip()
    if output_n == "":
        print("Output file name cannot be empty.")
        return
    if template_n == "":
        print("No template selected. Please select a template.")
        return
    global current_cl_text
    cl_dict = parsers.parse_cl(current_cl_text)
    template_path = os.path.join(SISYPHUS_PATH, "templates_cl", f"{template_n}")
    output_path = os.path.join(SISYPHUS_PATH, "saved_docs_cl", f"{output_n}.docx")
    if os.path.exists(output_path):
        print(f"Warning: {output_path} already exists and will be overwritten.")
    fileGenerator.generate_docx(template_path, cl_dict, output_path)

def show_output_cv(root):
    global result_window, result_textbox, current_cv_text
    try:
        # If window exists and is open, update it
        if result_window.winfo_exists():
            result_window.title("Tailored CV")
            result_textbox.delete("1.0", tk.END)
            result_textbox.insert(tk.END, current_cv_text)
            result_window.lift()
        else:
            raise Exception
    except:
        # If window doesn't exist or is closed, create a new one
        result_window = tk.Toplevel(root)
        result_window.title("Tailored CV")
        result_textbox = tk.Text(result_window, height=20, width=80)
        result_textbox.insert(tk.END, current_cv_text)
        result_textbox.pack(expand=True, fill=tk.BOTH)

def save_cv_text(file_name):
    #On cv output, this function can be used to save the current CV text to a text file as a text file
    global current_cv_text
    output_name = f"{file_name.strip()}.txt"
    if not file_name:
        date= datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"out_cv_{date}.txt"
    #check if file already exists
    output_path = os.path.join(OUT_CV_PATH, output_name)
    if os.path.exists(output_path):
        print(f"Warning: {output_name} already exists.")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(current_cv_text)
    print(f"CV saved to {output_path}")
    return

def save_cl_text(file_name):
    #On cl output, this function can be used to save the current CL text to a text file as a text file
    global current_cl_text
    output_name = f"{file_name.strip()}.txt"
    if not file_name:
        date= datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"out_cl_{date}.txt"
    #check if file already exists
    output_path = os.path.join(OUT_CL_PATH, output_name)
    if os.path.exists(output_path):
        print(f"Warning: {output_name} already exists.")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(current_cl_text)
    print(f"Cover letter saved to {output_path}")
    return

def load_cv_text(file_name):
    """
    Loads CV text from a file and returns it.
    """
    global tailor_cl_button
    global current_cv_text, format_check_current_cv_button, filter_output_cv_button, show_output_cv_button, save_output_cv_button, save_current_cv_text_button
    file_path = os.path.join(OUT_CV_PATH, file_name)
    if not os.path.exists(file_path):
        print(f"File {file_name} does not exist.")
        return
    with open(file_path, 'r', encoding='utf-8') as f:
        #load the text from the file to string
        current_cv_text = f.read()
    format_check_current_cv_button.config(state="normal")
    filter_output_cv_button.config(state="normal")
    show_output_cv_button.config(state="normal")
    save_output_cv_button.config(state="normal")
    save_current_cv_text_button.config(state="normal")
    tailor_cl_button.config(state="normal")
    print(f"CV loaded from {file_path}")
    return 

def load_cl_text(file_name):
    """
    Loads Cover Letter text from a file and returns it.
    """
    global current_cl_text, show_output_cl_button, save_output_cl_button, save_current_cl_text_button, filter_output_cl_button, format_check_current_cl_button
    file_path = os.path.join(OUT_CL_PATH, file_name)
    if not os.path.exists(file_path):
        print(f"File {file_name} does not exist.")
        return
    with open(file_path, 'r', encoding='utf-8') as f:
        #load the text from the file to string
        current_cl_text = f.read()
    show_output_cl_button.config(state="normal")
    save_output_cl_button.config(state="normal")
    save_current_cl_text_button.config(state="normal")
    filter_output_cl_button.config(state="normal")
    format_check_current_cl_button.config(state="normal")
    print(f"Cover letter loaded from {file_path}")
    return

def init_color(root, bg_color, fg_color):
    """
    Set all window backgrounds to bg_color and all text/button/border colors to fg_color.
    Applies to both Tk and ttk widgets.
    """
    root.configure(bg=bg_color)
    # Set Tkinter default colors
    root.option_add("*Background", bg_color)
    root.option_add("*Foreground", fg_color)
    root.option_add("*insertBackground", fg_color)  # Cursor color in Text/Entry
    root.option_add("*highlightBackground", bg_color)
    root.option_add("*highlightColor", fg_color)
    root.option_add("*selectBackground", fg_color)
    root.option_add("*selectForeground", bg_color)

    # ttk styles
    style = ttk.Style(root)
    try:
        style.theme_use("alt")  # alt is more color-customizable
    except Exception:
        pass
    style.configure("TLabel", background=bg_color, foreground=fg_color)
    style.map("TLabel", 
              background=[("active", bg_color), ("disabled", "#FFFFFF00")], 
              foreground=[("active", fg_color), ("disabled", "#FFFFFF00")])  # Set your desired color for disabled labels
    style.configure("TButton", background=bg_color, foreground=fg_color, bordercolor=fg_color, focuscolor=fg_color)
    style.configure("TCombobox", fieldbackground=bg_color, background=bg_color, foreground=fg_color, bordercolor=fg_color)
    style.configure("TEntry", fieldbackground=bg_color, background=bg_color, foreground=fg_color, bordercolor=fg_color)
    style.configure("TText", background=bg_color, foreground=fg_color, bordercolor=fg_color)
    style.configure("TFrame", background=bg_color)
    style.configure("TMenubutton", background=bg_color, foreground=fg_color, bordercolor=fg_color)
    style.map("TButton", background=[("active", bg_color)], foreground=[("active", fg_color)])
    style.map("TButton",
    background=[("active", bg_color), ("disabled", "#FF0000")],  # Set your desired color for disabled buttons
    foreground=[("active", fg_color), ("disabled", "#FFFFFF")]  # Set your desired color for disabled text
)
    # For Text widgets (not ttk), set after creation if needed



def main():
    
    # Save Output CV Button (initially disabled)
    global current_cl_text
    global tailor_cl_button
    global save_output_cv_button
    global save_current_cl_text_button
    global saved_outs,saved_out_var,saved_out_dropdown
    global save_current_cv_text_button
    global load_cv_text_button
    global template_dropdown, templates, model_dropdown, cv_dropdown, system_dropdown, model_var, models, cv_var,cvs, system_var, systems,out_file_textbox,save_file_textbox,job_desc_textbox, current_cv_text, format_check_current_cv_button, filter_output_cv_button, template_var
    global saved_outs_cl, saved_out_var_cl, saved_out_dropdown_cl, load_cl_text_button
    global cl_template_var, cl_templates, cl_template_dropdown
    global save_output_cl_button
    global filter_output_cl_button
    global show_output_cv_button, show_output_cl_button
    global format_check_current_cl_button

    run = runLocalModel.wait_for_ollama()
    if not run:
        print("Ollama server is not running. Starting Ollama.")
        runLocalModel.start_ollama_server()
        run = runLocalModel.wait_for_ollama()
        if not run:
            print("Failed to start Ollama server.")
            return 1
    
    root = tk.Tk()
    
    root.title("Sisyphus Resume Tailor")
    init_color(root, bg_color="#3F1111", fg_color="#ffa013")  # Example: dark grey and white
    model_var = tk.StringVar()
    models =[]
    cv_var = tk.StringVar()
    system_var = tk.StringVar()
    systems = []
    cvs = []
    template_var = tk.StringVar()
    templates = []
    saved_outs = []
    saved_out_var = tk.StringVar()

    saved_outs_cl = []
    saved_out_var_cl = tk.StringVar()

    cl_template_var = tk.StringVar()
    cl_templates = []
    
    # models = options[0]
    # systems = options[1]
    # cvs = options[2]
    
    # Initialize the main application window
    

    #On start up show a window with the following:
    current_cl_text = "" 
    current_cv_text = ""
    #1. Dropdown to select Ollama model (must detect initialize server and scan for available models)
    # Dropdown for models
    
    # model_var = tk.StringVar()
    # if model_var:
    #     model_var.set(models[0])
    model_dropdown = ttk.Combobox(root, textvariable=model_var, values=models)
    model_dropdown.grid(row=0, column=1)
    ttk.Label(root, text="Select Model:").grid(row=0, column=0)

    #Dropdown for system
    
    # system_var = tk.StringVar()
    # if system_var:
    #     system_var.set(systems[0])
    system_dropdown = ttk.Combobox(root, textvariable=system_var, values=systems)
    system_dropdown.grid(row=1, column=1)
    ttk.Label(root, text="Select System:").grid(row=1, column=0)
    

    #Dropdown for cv

    # cv_var = tk.StringVar()
    # if cv_var:
    #     cv_var.set(cvs[0])
    cv_dropdown = ttk.Combobox(root, textvariable=cv_var, values=cvs)
    cv_dropdown.grid(row=2, column=1)
    ttk.Label(root, text="Select CV File:").grid(row=2, column=0)
    
    #Dropdown for template
    template_dropdown = ttk.Combobox(root, textvariable=template_var, values=templates)
    template_dropdown.grid(row=3, column=1)
    ttk.Label(root, text="Select Template:").grid(row=3, column=0)

    #Dropdown for CL template
    cl_template_dropdown = ttk.Combobox(root, textvariable=cl_template_var, values=cl_templates)
    cl_template_dropdown.grid(row=4, column=1)
    ttk.Label(root, text="Select CL Template:").grid(row=4, column=0)

    # Dropdown for saved output CVs
    saved_out_dropdown = ttk.Combobox(root, textvariable=saved_out_var, values=saved_outs)
    saved_out_dropdown.grid(row=5, column=1)
    ttk.Label(root, text="Select Saved Output CV:").grid(row=5, column=0)

    #Dropdown for saved output CLs
    saved_out_dropdown_cl = ttk.Combobox(root, textvariable=saved_out_var_cl, values=saved_outs_cl)
    saved_out_dropdown_cl.grid(row=6, column=1)
    ttk.Label(root, text="Select Saved Output CL:").grid(row=6, column=0)

    #2. 1 Text fields:
        #Job Description
    # Text fields
    # ttk.Label(root, text="CV Text:").grid(row=2, column=0)
    # cv_textbox = tk.Text(root, height=5, width=40)
    # cv_textbox.grid(row=2, column=1)

    # ttk.Label(root, text="System:").grid(row=2, column=0)
    # system_textbox = tk.Text(root, height=2, width=40)
    # system_textbox.grid(row=2, column=1)

    # Job Description Textbox

    ttk.Label(root, text="Job Description:").grid(row=7, column=0)
    job_desc_textbox = tk.Text(root, height=5, width=40)
    job_desc_textbox.grid(row=7, column=1)

    #Output file Textbox
    ttk.Label(root, text="Output CV Name:").grid(row=7, column=2)
    out_file_textbox = tk.Text(root, height=1, width=20)
    out_file_textbox.grid(row=7, column=3)

    #Output Cover Letter Textbox
    ttk.Label(root, text="Output CL File Name:").grid(row=7, column=4)
    out_file_cl_textbox = tk.Text(root, height=1, width=20)
    out_file_cl_textbox.grid(row=7, column=5)

    #Saved Text File Name
    ttk.Label(root, text="Saved Text File Name:").grid(row=7, column=6)
    save_file_textbox = tk.Text(root, height=1, width=20)
    save_file_textbox.grid(row=7, column=7)


    


    #Buttons

    #Format Check Input CV Button
    global format_check_input_cv_button, show_output_cv_button, show_output_cl_button
    format_check_input_cv_button = ttk.Button(root, text="Format Check Input CV", command=lambda: format_check_input_cv_file(root, cv_var.get()), state="disabled")
    format_check_input_cv_button.grid(row=0, column=4)
    
    #Refresh Options Button


    
    refresh_button = ttk.Button(root, text="Refresh Options", command=refresh_options_callback)
    refresh_button.grid(row=0, column=2)

   

    
    #Tailor Button
    tailor_button = ttk.Button(root, text="Tailor CV", command=lambda: tailor_cv(root))
    tailor_button.grid(row=8, column=0)

    

    # Show CV Output Button (initially disabled)
    show_output_cv_button = ttk.Button(root, text="Show Output CV", command=lambda: show_output_cv(root), state="disabled")
    show_output_cv_button.grid(row=8, column=1)

    # Filter Output CV Text Button (initially disabled)
    filter_output_cv_button = ttk.Button(root, text="Filter Output CV Text", command=lambda: filter_output_cv_text(root), state="disabled")
    filter_output_cv_button.grid(row=8, column=2)

    # Format Check Current CV Text Button (initially disabled)
    format_check_current_cv_button = ttk.Button(root, text="Format Check Current CV Text", command=lambda: format_check_current_cv_text(root), state="disabled")
    format_check_current_cv_button.grid(row=8, column=3)

    

    # Save Output CV Button (initially disabled)
    save_output_cv_button = ttk.Button(root, text="Save Output CV to DOCX", command=lambda:save_output_cv(template_name= template_var,output_name= out_file_textbox.get("1.0", tk.END).strip()), state="disabled")
    save_output_cv_button.grid(row=8, column=4)

    # Save Current CV Text Button to text file (disabled if no text in current_cv_text)
    save_current_cv_text_button = ttk.Button(root, text="Save Current CV Text", command=lambda: save_cv_text(save_file_textbox.get("1.0", tk.END).strip()), state="disabled")
    save_current_cv_text_button.grid(row=8, column=5)
    
    # Load CV Text Button (disabled if no saved output CVs)
    load_cv_text_button = ttk.Button(root, text="Load CV Text", command=lambda: load_cv_text(saved_out_var.get()), state="disabled")
    load_cv_text_button.grid(row=8, column=6)

    #Tailor Cover Letter Button (Initially disabled)
    tailor_cl_button =ttk.Button(root, text="Tailor CL", command=lambda: tailor_cl(root), state="disabled")
    tailor_cl_button.grid(row=9, column=0)

    # Show Output Cover Letter Button (Initially disabled)
    show_output_cl_button = ttk.Button(root, text="Show Output CL", command=lambda: show_output_cl(root), state="disabled")
    show_output_cl_button.grid(row=9, column=1)

    # Filter Output Cover Letter Button (Initially disabled)
    filter_output_cl_button = ttk.Button(root, text="Filter Output CL Text", command=lambda: filter_output_cl_text(root), state="disabled")
    filter_output_cl_button.grid(row=9, column=2)

    # Format Check Current CL Text Button (initially disabled)
    format_check_current_cl_button = ttk.Button(root, text="Format Check Current CL Text", command=lambda: format_check_current_cl_text(root), state="disabled")
    format_check_current_cl_button.grid(row=9, column=3)

    save_output_cl_button = ttk.Button(root, text="Save Output CL to DOCX", command=lambda:save_output_cl(template_name= cl_template_var,output_name= out_file_cl_textbox.get("1.0", tk.END).strip()), state="disabled")
    save_output_cl_button.grid(row=9, column=4)

    # Save Output Cover Letter Button (Initially disabled)
    save_current_cl_text_button = ttk.Button(root, text="Save Current CL Text", command=lambda:save_cl_text(save_file_textbox.get("1.0", tk.END).strip()), state="disabled")
    save_current_cl_text_button.grid(row=9, column=5)

    # Load Cover Letter Text Button (Initially disabled)
    load_cl_text_button = ttk.Button(root, text="Load CL Text", command=lambda: load_cl_text(saved_out_var_cl.get()), state="disabled")
    load_cl_text_button.grid(row=9, column=6)

    refresh_options_callback()


    #Show the window
    root.mainloop()
 
if __name__ == "__main__":
    main()