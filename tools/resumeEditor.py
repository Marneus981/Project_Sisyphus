import tkinter as tk
from tkinter import ttk, filedialog
import sv_ttk
import darkdetect
import pywinstyles
import sys
import os
from tkinterdnd2 import DND_FILES, TkinterDnD

# Add the parent directory to sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from Sisyphus import helpers  # Now you can import
from Sisyphus import parsers
#Resume Editor Tool (opened at the end of a tailor or batch tailor cycle)
    #[ToBeImplementedAtALaterDate]"Separate Skills" on write toggle?
    #[ToBeImplementedAtALaterDate]Scrap LinkedIn page(s)
    #[ToBeImplementedAtALaterDate]Scrap Indeed page(s)
    #[ToBeImplementedAtALaterDate] Save to pdf button
        #Save dir dafaults to Sisyphus\saved_docs

#Functions
def apply_theme_to_titlebar(root):
    version = sys.getwindowsversion()

    if version.major == 10 and version.build >= 22000:
        # Set the title bar color to the background color on Windows 11 for better appearance
        pywinstyles.change_header_color(root, "#1c1c1c" if sv_ttk.get_theme() == "dark" else "#fafafa")
    elif version.major == 10:
        pywinstyles.apply_style(root, "dark" if sv_ttk.get_theme() == "dark" else "normal")

        # A hacky way to update the title bar's color on Windows 10 (it doesn't update instantly like on Windows 11)
        root.wm_attributes("-alpha", 0.99)
        root.wm_attributes("-alpha", 1)

def toggle_menu():
    if TopMenu.winfo_viewable():
        TopMenu.pack_forget()
    else:
        TopMenu.pack(side='top', fill='x')
        HideMenu.pack_forget()
        HideMenu.pack(side='top', anchor='w')
        EditorContainer.pack_forget()
        EditorContainer.pack(side='top', fill='both', expand=True)

def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def browse_file(type = ""):
    global EditFileScrollableFrame, RefFileScrollableFrame, EditFileResume, RefFileResume, EditFilePathVar, EditFileText, RefFilePathVar, RefFileText
    if type == "edit":
        default_dir = os.path.join(os.path.dirname(__file__), '..',"Sisyphus", 'saved_outputs')
        default_dir = os.path.abspath(default_dir)
        file_path = filedialog.askopenfilename(initialdir=default_dir,filetypes=[("Text files", "*.txt")])
        if file_path:
            print("Selected file:", file_path)
        EditFilePathVar.set(file_path)
        EditFileText = helpers.read_text_file(str(EditFilePathVar.get()))
        resume_dct = parsers.parse_cv(EditFileText)
        resume_sk_dct = parsers.parse_cv_out(EditFileText)
        clear_frame(EditFileScrollableFrame)
        EditFileResume = StandardResume(name="Editable Resume", resume_data=resume_dct, resume_data_sk=resume_sk_dct)
        EditFileResume.draw_self(EditFileScrollableFrame)
    elif type == "ref":
        default_dir = os.path.join(os.path.dirname(__file__), '..',"Sisyphus", 'cvs')
        default_dir = os.path.abspath(default_dir)
        file_path = filedialog.askopenfilename(initialdir=default_dir,filetypes=[("Text files", "*.txt")])
        if file_path:
            print("Selected file:", file_path)
        RefFilePathVar.set(file_path)
        RefFileText = helpers.read_text_file(str(RefFilePathVar.get()))
        ref_resume_dct = parsers.parse_cv(RefFileText)
        ref_resume_sk_dct = parsers.parse_cv_out(RefFileText)
        clear_frame(RefFileScrollableFrame)
        RefFileResume = StandardResume(name="Reference Resume", resume_data=ref_resume_dct, resume_data_sk=ref_resume_sk_dct)
        RefFileResume.draw_self(RefFileScrollableFrame)
    else:
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            print("Selected file:", file_path)

def drop(event, type = "edit"):
    global EditFileResume, RefFileResume, EditFilePathVar, EditFileText, RefFilePathVar, RefFileText, JobDescPathVar, JobDescText
    file_path = event.data
    if type == "edit":
        if file_path.endswith('.txt'):
            EditFilePathVar.set(file_path)
            EditFileText = helpers.read_text_file(str(EditFilePathVar.get()))
            resume_dct = parsers.parse_cv(EditFileText)
            resume_sk_dct = parsers.parse_cv_out(EditFileText)
            clear_frame(EditFileScrollableFrame)
            EditFileResume = StandardResume(name="Editable Resume", resume_data=resume_dct, resume_data_sk=resume_sk_dct)
            EditFileResume.draw_self(EditFileScrollableFrame)
            print("Edit file dropped:", file_path)
    elif type == "ref":
        if file_path.endswith('.txt'):
            RefFilePathVar.set(file_path)
            RefFileText = helpers.read_text_file(str(RefFilePathVar.get()))
            ref_resume_dct = parsers.parse_cv(RefFileText)
            ref_resume_sk_dct = parsers.parse_cv_out(RefFileText)
            clear_frame(RefFileScrollableFrame)
            RefFileResume = StandardResume(name="Reference Resume", resume_data=ref_resume_dct, resume_data_sk=ref_resume_sk_dct)
            RefFileResume.draw_self(RefFileScrollableFrame)
            print("Reference file dropped:", file_path)
    else:
        if file_path.endswith('.txt'):
            JobDescPathVar.set(file_path)
            JobDescText = helpers.read_text_file(JobDescPathVar)
            print("Job description file dropped:", file_path)


def save_as(file_type = "edit"):
    if file_type == "edit":
        default_dir = os.path.join(os.path.dirname(__file__), '..',"Sisyphus", 'saved_outputs')
        default_dir = os.path.abspath(default_dir)
        os.makedirs(default_dir, exist_ok=True)
    elif file_type == "ref":
        default_dir = os.path.join(os.path.dirname(__file__), '..',"Sisyphus", 'cvs')
        default_dir = os.path.abspath(default_dir)
        os.makedirs(default_dir, exist_ok=True)
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt")],
        title="Save As...",
        initialdir=default_dir
    )
    if file_path:
        with open(file_path, 'w', encoding='utf-8') as f:
            if file_type == "ref":
                f.write(RefFileText)  # Replace with your actual content
            else:
                f.write(EditFileText) 

def save_to_doc():
    pass  # To be implemented

def add_label(container, label_text = "",padx=5, pady=5):
    label = ttk.Label(container, text=label_text)
    label.pack(padx=padx, pady=pady)
    return label

def add_frame(container, type = "pack",column = 0, row = 0, sticky ="nsew", side = "top", fill = "x"):
    frame = ttk.Frame(container)
    if type == "grid":
        frame.grid(column=column, row=row, sticky=sticky)
    else:
        frame.pack(side=side, fill=fill)
    return frame

def add_entry(container, text_var = None, width=50,padx=10, pady=10, side="left"):
    print(f"Add Entry: {text_var}")
    v = tk.StringVar()
    entry = ttk.Entry(container, width=width, textvariable=v)
    # entry.insert(index = 0, string= text_var)
    entry.pack(padx=padx, pady=pady, side=side)
    v.set(text_var)
    return v

#Classes
class ResumeSubSection:
    def __init__(self, title = "SubSectionPlaceholder", content = None):
        self.title = title
        self.content = tk.StringVar(value=str(content))

    def __repr__(self):
        return f"SubSection(title={self.title}: {str(self.content)})"

    def draw_self(self, container):
        frame = ttk.Frame(container)
        frame.pack(side='top', fill='both', expand=True)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        # frame.columnconfigure(2, weight=1)
        frame.rowconfigure(0, weight=1)
        frame_title = ttk.Frame(frame)
        frame_title.grid(column=0, row=0, sticky="nsew")
        frame_edit = ttk.Frame(frame)
        frame_edit.grid(column=1, row=0, sticky="nsew")
        # frame_txt = ttk.Frame(frame)
        # frame_txt.grid(column=2, row=0, sticky="nsew")
        title = ttk.Label(frame_title, text=self.title)
        title.pack(padx=10, pady=10, side="left")
        editable_entry = ttk.Entry(frame_edit, width=50, textvariable=self.content)
        editable_entry.pack(padx=10, pady=10, side="left")
        # text_label = ttk.Label(frame_txt, textvariable=self.content)
        # text_label.pack(padx=10, pady=10, side="left")
        
        

class ResumeSection:
    def __init__(self, title = "SectionPlaceholder", value=None):
        self.title = title
        if isinstance(value,str):
            self.value = tk.StringVar(value=value)
        else:
            self.value = value
    
    def add_subsection(self, name, value):
        subsec = ResumeSubSection(title=name, content=value)
        setattr(self, name, subsec)
    
    def __repr__(self):
        additional = ""
        for subsection in self.__dict__.values():
            if subsection != self.title and subsection != self.value:
                additional += f"    {subsection}\n"
        return f"Section(title={self.title} : {str(self.value)})\n" + f"{additional}"
    
    def draw_self(self, container):
        print(f"Drawing Section: {self.title}")
        SectionFrame = ttk.Frame(container)
        SectionFrame.pack(padx=10, pady=10, anchor="nw")

        SectionTitle = ttk.Label(SectionFrame, text=self.title, font=("Arial", 16))
        SectionTitle.pack(padx=10, pady=10, anchor="nw")

        if isinstance(self.value, tk.StringVar):
            print(f"Section value is a tk.StringVar: {self.value.get()}")
            ContentFrame = ttk.Frame(SectionFrame)
            ContentFrame.pack(side='top', fill='both', expand=True)
            ContentFrame.columnconfigure(0, weight=1)
            ContentFrame.columnconfigure(1, weight=1)
            
            ContentEntryFrame = ttk.Frame(ContentFrame)
            ContentEntryFrame.grid(column=0, row=0,sticky="ew")
            ContentEntry = ttk.Entry(ContentEntryFrame, textvariable=self.value)
            ContentEntry.pack(padx=10, pady=10, side="left", anchor="nw")

            ContentTextFrame = ttk.Frame(ContentFrame)
            ContentTextFrame.grid(column=1, row=0,sticky="ew")
            ContentText = ttk.Label(ContentTextFrame, textvariable=self.value)
            ContentText.pack(padx=10, pady=10, side="left", anchor="nw")

        elif isinstance(self.value,list):
            print(f"Section value is a list with len: {len(self.value)}")
            for section in self.value:
                if hasattr(section, "draw_self"):
                    print(f"Recursive: Drawing Section {section.title} inside {self.title}")
                    section.draw_self(SectionFrame)

        for subsection in self.__dict__.values():
            if hasattr(subsection, "draw_self"):
                print("Drawing SubSection:", subsection.title)
                print("Content:", subsection.content)
                subsection.draw_self(SectionFrame)
        
                      
class Resume:
    def __init__(self, name ="ResumePlaceholder"):
        self.title = name

    def add_section(self, name, value = ResumeSection()):
        setattr(self, name, value)

    def __repr__(self):
        additional = ""
        for section in self.__dict__.values():
            if section != self.title:
                additional += f"    {section}\n"
        return f"Resume(title={self.title})\n" + f"{additional}"

    def draw_self(self, container):
        resume_label = ttk.Label(container, text=self.title, font=("Arial", 16, "bold"))
        resume_label.pack(padx=10, pady=10, anchor="nw")
        resume_frame = ttk.Frame(container)
        resume_frame.pack(padx=10, pady=10, anchor="nw")
        for section in self.__dict__.values():
            if hasattr(section, "draw_self"):
                print(f"Section: {section.title} has draw_self attibute, drawing...")
                section.draw_self(resume_frame)
        


class StandardResume(Resume):
    def __init__(self, name="Standard Resume", resume_data={}, resume_data_sk = {}):
        super().__init__(name)
        print(f"Name: {resume_data.get("name", "")}")
        self.add_section("Name", Name(value=resume_data.get("name", "")))
        print(f"Contact Info: {resume_data.get("contact_information", {})}")
        self.add_section("Contact Information", ContactInfo(value=resume_data.get("contact_information", {})))
        print(f"Title: {resume_data.get("title", "")}")
        self.add_section("Title", Title(value=resume_data.get("title", "")))
        print(f"Summary: {resume_data.get("summary", "")}")
        self.add_section("Summary", Summary(value=resume_data.get("summary", "")))
        print(f"Languages: {resume_data.get("languages", [])}")
        self.add_section("Languages", Languages(value=resume_data.get("languages", [])))
        print(f"Education: {resume_data.get("education", [])}")
        self.add_section("Education", Education(value=resume_data.get("education", [])))
        print(f"Certifications: {resume_data.get("certifications", [])}")
        self.add_section("Certifications", Certifications(value=resume_data.get("certifications", [])))
        print(f"Awards and Scholarships: {resume_data.get("awards_and_scholarships", [])}")
        self.add_section("Awards and Scholarships", AwardsAndScholarships(value=resume_data.get("awards_and_scholarships", [])))
        print(f"Volunteering and Leadership: {resume_data.get("volunteering_and_leadership", [])}")
        self.add_section("Volunteering and Leadership", VolunteeringAndLeadership(value=resume_data.get("volunteering_and_leadership", [])))
        print(f"Work Experience: {resume_data.get("work_experience", [])}")
        self.add_section("Work Experience", WorkExperience(value=resume_data.get("work_experience", [])))
        print(f"Projects: {resume_data.get("projects", [])}")
        self.add_section("Projects", Projects(value=resume_data.get("projects", [])))
        print(f"Skills: {resume_data_sk.get("skills", {})}")
        self.add_section("Skills", Skills(value=resume_data_sk.get("skills", {})))

class Name(ResumeSection):
    def __init__(self, title="Name", value=None):
        super().__init__(title)
        self.value = tk.StringVar(value= value)
class ContactInfo(ResumeSection):
    def __init__(self, title="Contact Information", value={}):
        super().__init__(title)
        self.add_subsection("Address", value=value.get("address", ""))
        self.add_subsection("Phone", value=value.get("phone", ""))
        self.add_subsection("Email", value=value.get("email", ""))
        self.add_subsection("LinkedIn", value=value.get("linkedin", ""))
        self.add_subsection("GitHub", value=value.get("github", ""))
        self.add_subsection("Portfolio", value=value.get("portfolio", ""))
        for key, val in value.items():
            if key not in {"address", "phone", "email", "linkedin", "github", "portfolio"}:
                self.add_subsection(key, value=val)
class Title(ResumeSection): 
    def __init__(self, title="Title", value=None):
        super().__init__(title)
        self.value = tk.StringVar(value= value)
class Summary(ResumeSection):
    def __init__(self, title="Summary", value=None):
        super().__init__(title)
        self.value = tk.StringVar(value= value)
class Languages(ResumeSection): 
    def __init__(self, title="Languages", value=[]):
        super().__init__(title)
        self.value = tk.StringVar(value= str(value))
class EducationObject(ResumeSection):
    def __init__(self, title="Education Object", education_info={}):
        super().__init__(title)
        self.add_subsection("Degree", value=education_info.get("degree", ""))
        self.add_subsection("University", value=education_info.get("university", ""))
        self.add_subsection("Location", value=education_info.get("location", ""))
        self.add_subsection("Duration", value=education_info.get("duration", ""))
        self.add_subsection("Courses", value=education_info.get("courses", []))
class Education(ResumeSection): 
    def __init__(self, title="Education", value=[]): #list of dicts as input
        super().__init__(title)
        i = 0
        tmp_edu_list = []
        for edu in value:
            tmp_edu = EducationObject(title=f"Education{i+1}", education_info=edu)
            i += 1
            tmp_edu_list.append(tmp_edu)
        self.value = tmp_edu_list
class CertificationsObject(ResumeSection):
    def __init__(self, title="Certification Object", value={}):
        super().__init__(title)
        self.add_subsection("Certification Name", value=value.get("certification_name", ""))
        self.add_subsection("Issuing Organization", value=value.get("issuing_organization", ""))
        self.add_subsection("Issue Date", value=value.get("issue_date", ""))
        for key, val in value.items():
            if key not in {"certification_name", "issuing_organization", "issue_date"}:
                self.add_subsection(key, value=val)
class Certifications(ResumeSection):
    def __init__(self, title="Certifications", value=[]): #list of dicts as input
        super().__init__(title)
        i = 0
        tmp_cert_list = []
        for cert in value:
            tmp_cert = CertificationsObject(title=f"Certification{i+1}", value=cert)
            i += 1
            tmp_cert_list.append(tmp_cert)
        self.value = tmp_cert_list
class AwardsAndScholarshipsObject(ResumeSection):
    def __init__(self, title="Award/Scholarship Object", value={}):
        super().__init__(title)
        self.add_subsection("Award Name", value=value.get("award_name", ""))
        self.add_subsection("Issuing Organization", value=value.get("issuing_organization", ""))
        self.add_subsection("Issue Date", value=value.get("issue_date", ""))
        for key, val in value.items():
            if key not in {"award_name", "issuing_organization", "issue_date"}:
                self.add_subsection(key, value=val)
class AwardsAndScholarships(ResumeSection): 
    def __init__(self, title="Awards and Scholarships", value=[]): #list of dicts as input
        super().__init__(title)
        i = 0
        tmp_award_list = []
        for award in value:
            tmp_award = AwardsAndScholarshipsObject(title=f"Award/Scholarship{i+1}", value=award)
            i += 1
            tmp_award_list.append(tmp_award)
        self.value = tmp_award_list
class VolunteeringAndLeadershipObject(ResumeSection):
    def __init__(self, title="Volunteering and Leadership Object", value={}):
        super().__init__(title)
        self.add_subsection("Role", value=value.get("role", ""))
        self.add_subsection("Organization", value=value.get("organization", ""))
        self.add_subsection("Location", value=value.get("location", ""))
        self.add_subsection("Duration", value=value.get("duration", ""))
        self.add_subsection("Description", value=value.get("description", ""))
        self.add_subsection("Skills", value=value.get("skills", {}))
        for key, val in value.items():
            if key not in {"role", "organization", "duration", "location", "description", "skills"}:
                self.add_subsection(key, value=val)
class VolunteeringAndLeadership(ResumeSection):
    def __init__(self, title="Volunteering and Leadership", value=[]): #list of dicts as input
        super().__init__(title)
        i = 0
        tmp_vol_list = []
        for vol in value:
            tmp_vol = VolunteeringAndLeadershipObject(title=f"Volunteering/Leadership{i+1}", value=vol)
            i += 1
            tmp_vol_list.append(tmp_vol)
        self.value = tmp_vol_list
class WorkExperienceObject(ResumeSection):
    def __init__(self, title="Work Experience Object", value={}):
        super().__init__(title)
        self.add_subsection("Job Title", value=value.get("job_title", ""))
        self.add_subsection("Company", value=value.get("company", ""))
        self.add_subsection("Location", value=value.get("location", ""))
        self.add_subsection("Duration", value=value.get("duration", ""))
        self.add_subsection("Description", value=value.get("description", []))
        self.add_subsection("Skills", value=value.get("skills", {}))
        for key, val in value.items():
            if key not in {"job_title", "company", "location", "duration", "description", "skills"}:
                self.add_subsection(key, value=val)
class WorkExperience(ResumeSection):
    def __init__(self, title="Work Experience", value=[]): #list of dicts as input
        super().__init__(title)
        i = 0
        tmp_work_list = []
        for work in value:
            tmp_work = WorkExperienceObject(title=f"WorkExperience{i+1}", value=work)
            i += 1
            tmp_work_list.append(tmp_work)
        self.value = tmp_work_list
class ProjectsObject(ResumeSection):
    def __init__(self, title="Project Object", value={}):
        super().__init__(title)
        self.add_subsection("Project Title", value=value.get("project_title", ""))
        self.add_subsection("URL", value=value.get("url", ""))
        self.add_subsection("Type", value=value.get("type", ""))
        self.add_subsection("Location", value=value.get("location", ""))
        self.add_subsection("Duration", value=value.get("duration", ""))
        self.add_subsection("Description", value=value.get("description", ""))
        self.add_subsection("Skills", value=value.get("skills", ""))
        for key, val in value.items():
            if key not in {"project_title", "description", "type", "location", "duration", "skills", "url"}:
                self.add_subsection(key, value=val)
class Projects(ResumeSection):
    def __init__(self, title="Projects", value=[]): #list of dicts as input
        super().__init__(title)
        i = 0
        tmp_project_list = []
        for project in value:
            tmp_project = ProjectsObject(title=f"Project{i+1}", value=project)
            i += 1
            tmp_project_list.append(tmp_project)
        self.value = tmp_project_list
class Skills(ResumeSection):
    def __init__(self, title="Skills", value={}): #dict as input
        super().__init__(title)
        self.add_subsection("Programming Languages", value=value.get("programming_languages", []))
        self.add_subsection("Technical Skills", value=value.get("technical_skills", []))
        self.add_subsection("Soft Skills", value=value.get("soft_skills", []))
        

#Application code
MainWindow = TkinterDnD.Tk()
MainWindow.title("Sisyphus Resume Editor")

#UI Elements (UI elements must be boxed in and clearly separated from one another)
#"Parameters"

TopMenu = ttk.Frame(MainWindow, height=40)
TopMenu.pack(side='top', fill='x')
####

JobDescVar = tk.StringVar(value="Enter Job Description")  # Default text
AIKeywordsVar  = tk.StringVar(value="Enter comma-separated list of Job Description keywords")  # Default text 
EditFilePathVar = tk.StringVar()
RefFilePathVar = tk.StringVar()
JobDescPathVar = tk.StringVar()
EditFileText = str()
RefFileText = str()
JobDescText = str()
    #"Save/Export"
SaveExportContainer = ttk.Frame(TopMenu)
SaveExportContainer.pack(side='top', fill='x')
        #Save text file pop-up (defaults to rewriting loaded editable file if provided)
            #Save dir defaults to Sisyphus\saved_outputs
SaveEditFile = ttk.Button(SaveExportContainer, text="Save Editable Resume As...", command=lambda: save_as(file_type="edit"), cursor="hand2")
SaveEditFile.pack(padx=10, pady=10, side="left")
        #Save text file pop-up (defaults to rewriting loaded editable file if provided)
                    #Save dir defaults to Sisyphus\cvs
SaveRefFile = ttk.Button(SaveExportContainer, text="Save Reference Resume As...", command=lambda: save_as(file_type="ref"), cursor="hand2")
SaveRefFile.pack(padx=10, pady=10, side="left")
        #Save to odt or docx button
            #Save dir dafaults to Sisyphus\saved_docs
SaveToDocButton = ttk.Button(SaveExportContainer, text="Save Editable Resume to .docx/.odt", command=lambda: save_to_doc(), cursor="hand2")
SaveToDocButton.pack(padx=10, pady=10, side="left")

    #""Job Description and AI Keywords"
JobDescContainer = ttk.Frame(TopMenu)
JobDescContainer.pack(side='top', fill='x')
JobDescLabel = ttk.Label(JobDescContainer, text="Job Description Input")
JobDescLabel.pack(padx=10, pady=5, side="left")
        #Load (Drag and drop/input address) Job Desc from txt File
JobDescBrowse = ttk.Button(JobDescContainer, text="Browse or Drop Job Description .txt File", command=lambda:browse_file(), cursor="hand2")
JobDescBrowse.pack(padx=10, pady=10, side="left")
JobDescBrowse.drop_target_register(DND_FILES)
JobDescBrowse.dnd_bind('<<Drop>>', drop)
        #Text Field (Writeable, updates on File Job Desc Load)
JobDescTextField = ttk.Entry(JobDescContainer, width=50, textvariable=JobDescVar)
JobDescTextField.pack(padx=10, pady=10, side="left")
        #"Generate Keywords(AI)" button
GenerateAIKeywords = ttk.Button(JobDescContainer, text="Generate AI Keywords", cursor="hand2")
GenerateAIKeywords.pack(padx=10, pady=10, side="left")
        #Text Field (Writeable, updates on "Generate Keywords(AI)" button) 
AIKeywordsTextField = ttk.Entry(JobDescContainer, width=50, textvariable=AIKeywordsVar)
AIKeywordsTextField.pack(padx=10, pady=10, side="left")
    #"Load Files"
FilesContainer = ttk.Frame(TopMenu)
FilesContainer.pack(side='top', fill='x')
FilesContainer.columnconfigure(0, weight=1)
FilesContainer.columnconfigure(1, weight=1)
        #Load (Drag and drop/input address) txt File to Edit
EditFileBrowse = ttk.Button(FilesContainer, text="Browse or Drop Editable .txt File", command=lambda:browse_file( type="edit"), cursor="hand2")
EditFileBrowse.grid(padx=10, pady=10, column=0, row=0, sticky='ew')
EditFileBrowse.drop_target_register(DND_FILES)
EditFileBrowse.dnd_bind('<<Drop>>', lambda event: drop(event, "edit"))
        #Load (Drag and drop) Reference txt CV File
RefFileBrowse = ttk.Button(FilesContainer, text="Browse or Drop Reference .txt File", command=lambda:browse_file( type="ref"), cursor="hand2")
RefFileBrowse.grid(padx=10, pady=10, column=1, row=0, sticky='ew')
RefFileBrowse.drop_target_register(DND_FILES)
RefFileBrowse.dnd_bind('<<Drop>>', lambda event: drop(event, "ref"))


####
HideMenu = ttk.Button(MainWindow, text="Toggle Menu", command=lambda:toggle_menu(), cursor="hand2")
HideMenu.pack(side='top', anchor='w')

#"Editable/Reference Display"
EditorContainer = ttk.Frame(MainWindow)
EditorContainer.pack(side='top', fill='both', expand=True)
EditorContainer.columnconfigure(0, weight=1)
EditorContainer.columnconfigure(1, weight=1)
EditorContainer.rowconfigure(0, weight=1)

#Test Button
# TrialButton = ttk.Button(EditorContainer, text="Click me!", cursor="hand2")
# TrialButton.pack()
EditorContainerEditFile = ttk.Frame(EditorContainer)
EditorContainerEditFile.grid(column=0, row=0, sticky="nsew")
EditFileCanvas = tk.Canvas(EditorContainerEditFile)
EditFileScrollbar = ttk.Scrollbar(EditorContainerEditFile, orient='vertical', command=EditFileCanvas.yview)
EditFileScrollableFrame = ttk.Frame(EditFileCanvas)
EditFileScrollableFrame.bind(
    "<Configure>",
    lambda e: EditFileCanvas.configure(
        scrollregion=EditFileCanvas.bbox("all")
    )
)
EditFileCanvas.create_window((0, 0), window=EditFileScrollableFrame, anchor='nw')
EditFileCanvas.configure(yscrollcommand=EditFileScrollbar.set)
EditFileCanvas.pack(side='left', fill='both', expand=True)
EditFileScrollbar.pack(side='right', fill='y')

EditorContainerRefFile = ttk.Frame(EditorContainer)
EditorContainerRefFile.grid(column=1, row=0, sticky="nsew")
RefFileCanvas = tk.Canvas(EditorContainerRefFile)
RefFileScrollbar = ttk.Scrollbar(EditorContainerRefFile, orient='vertical', command=RefFileCanvas.yview)
RefFileScrollableFrame = ttk.Frame(RefFileCanvas)
RefFileScrollableFrame.bind(
    "<Configure>",
    lambda e: RefFileCanvas.configure(
        scrollregion=RefFileCanvas.bbox("all")
    )
)
RefFileCanvas.create_window((0, 0), window=RefFileScrollableFrame, anchor='nw')
RefFileCanvas.configure(yscrollcommand=RefFileScrollbar.set)
RefFileCanvas.pack(side='left', fill='both', expand=True)
RefFileScrollbar.pack(side='right', fill='y')

EditFileResume = None
RefFileResume = None

    #Reads editable using parser functions, into dict (not keeping skills as a separate section)
    #Display editable text in a per field/subfield basis (editable) according to dict hierarchy (can add subfields depending on hierarchy + available subfields):
        #Example:
            #Work Experience:
                #Job Title: 
                    #PEY VR Technical Assistant
                #Company: 
                    #Medica Providencia Clinic
                #Location:
                    #Tuxtla Gtz, CS, Mexico
                #Duration: 
                    #2022/12 - 2023/03
                #Description: 
                    #Performed hardware troubleshooting on Oculus Quest VR equipment, reducing weekly downtime through systematic diagnostics and repairs. Collaborated with healthcare professionals during the testing process, resulting in a more patient-centred approach and improved satisfaction scores.
                #Skills: 
                    #Programming Languages:
                        #[BUTTON: PLUS SIGN(text field + drop down with AI generated suggestions, if generated)]
                    #Technical Skills: 
                        #VR Technologies, Hardware Troubleshooting, Software Troubleshooting, Oculus Quest VR equipment, Repairs, Neurodivergent Testing
                        #[BUTTON: PLUS SIGN(text field + drop down with AI generated suggestions, if generated)]
                    #Soft Skills: 
                        #Teamwork, Analytical Problem Solving, Good Written and Communication Skills, Problem Solving
                        #[BUTTON: PLUS SIGN(text field + drop down with AI generated suggestions, if generated)]
                    #[BUTTON: PLUS SIGN(displays drop down with list of available "Skills" subsections)]
                #[BUTTON: PLUS SIGN(displays drop down with list of available "Work Experience" subsections)]
            #[BUTTON: PLUS SIGN(displays drop down with list of available sections)]


#Apply theme
MainWindow.state('zoomed') 
sv_ttk.set_theme(darkdetect.theme())
apply_theme_to_titlebar(MainWindow)
MainWindow.mainloop()

    
