import tkinter as tk
from tkinter import ttk, filedialog
import sv_ttk
import tkinter.ttk as ttk

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
        #Clear previous resume object
        EditFileResume = None
        EditFileText = helpers.read_text_file(str(EditFilePathVar.get()))
        # resume_dct = parsers.parse_cv(EditFileText)
        resume_sk_dct = parsers.parse_cv_out(EditFileText)
        clear_frame(EditFileScrollableFrame)
        EditFileResume = StandardResume(name="Editable Resume", resume_data=resume_sk_dct, separate_sk=True)
        EditFileResume.draw_self(EditFileScrollableFrame)
    elif type == "ref":
        default_dir = os.path.join(os.path.dirname(__file__), '..',"Sisyphus", 'cvs')
        default_dir = os.path.abspath(default_dir)
        file_path = filedialog.askopenfilename(initialdir=default_dir,filetypes=[("Text files", "*.txt")])
        if file_path:
            print("Selected file:", file_path)
        RefFilePathVar.set(file_path)
        RefFileResume = None
        RefFileText = helpers.read_text_file(str(RefFilePathVar.get()))
        ref_resume_dct = parsers.parse_cv(RefFileText)
        # ref_resume_sk_dct = parsers.parse_cv_out(RefFileText)
        clear_frame(EditFileScrollableFrame)
        clear_frame(RefFileScrollableFrame)
        RefFileResume = StandardResume(name="Reference Resume", resume_data=ref_resume_dct, separate_sk=False)
        RefFileResume.draw_self(RefFileScrollableFrame)
        EditFileResume.draw_self(EditFileScrollableFrame)
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
            EditFileResume = None
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
            RefFileResume = None
            RefFileText = helpers.read_text_file(str(RefFilePathVar.get()))
            ref_resume_dct = parsers.parse_cv(RefFileText)
            ref_resume_sk_dct = parsers.parse_cv_out(RefFileText)
            clear_frame(RefFileScrollableFrame)
            clear_frame(EditFileScrollableFrame)
            RefFileResume = StandardResume(name="Reference Resume", resume_data=ref_resume_dct, resume_data_sk=ref_resume_sk_dct)
            RefFileResume.draw_self(RefFileScrollableFrame)
            EditFileResume.draw_self(EditFileScrollableFrame)
            print("Reference file dropped:", file_path)
    else:
        if file_path.endswith('.txt'):
            JobDescPathVar.set(file_path)
            JobDescText = helpers.read_text_file(JobDescPathVar)
            print("Job description file dropped:", file_path)

def resume_to_dict(resume_obj):
    result = {}
    name = str(resume_obj.title).lower().replace(" ", "_")
    if isinstance(resume_obj, ResumeSubSection):
        if isinstance(resume_obj,SkillSubSection):
            for key, section in resume_obj.__dict__.items():
                if hasattr(section, "draw_self"):
                    name_tmp = str(section.title).lower().replace(" ", "_")
                    result[name_tmp] = resume_to_dict(section)
            return result
        else:
            #if isinstance(section.content,tk.StringVar):
            str_tmp = str(resume_obj.content.get())
            if str_tmp.startswith("[") and str_tmp.endswith("]"):
                str_tmp = str_tmp.strip().replace("'","").replace("[","").replace("]","").split(",")
                str_tmp = [item.strip() for item in str_tmp]
                return str_tmp
            else:
                return str_tmp
    elif isinstance(resume_obj,ResumeSection):
        #with str:Name, Title,Summary
            #into list: Languages
        if isinstance(resume_obj.value, tk.StringVar):
            str_tmp = str(resume_obj.value.get())
            print(f"resume_to_dict: Processing tk.StringVar value: {str_tmp}")
            if str_tmp.startswith("[") and str_tmp.endswith("]"):
                str_tmp = str_tmp.strip().replace("'","").replace("[","").replace("]","").split(",")
                str_tmp = [item.strip() for item in str_tmp]
                return str_tmp
            else:
                return str_tmp
        #with self.value list: Education,Certifications,AwardsAndScholarships...
        elif isinstance(resume_obj.value, list):
            tmp_list = []
            for item in resume_obj.value:
                tmp_list.append(resume_to_dict(item))
            return tmp_list
        #with subsections:Contact Information, EducationObject,CertificationsObject,AwardsAndScholarshipsObject..., Skills
        else:
            for key, section in resume_obj.__dict__.items():
                if hasattr(section, "draw_self"):
                    name = str(section.title).lower().replace(" ", "_")
                    result[name] = resume_to_dict(section)
            return result
    elif isinstance(resume_obj,Resume):
        for key, section in resume_obj.__dict__.items():
            if hasattr(section, "draw_self"):
                name = section.title.lower().replace(" ", "_")
                result[name] = resume_to_dict(section)
        return result
        

def update_resume_text_vars(type = "edit"):
    global EditFileResume, RefFileResume, EditFileText, RefFileText
    if type == "edit":
        if EditFileResume is not None:
            resume_dict = resume_to_dict(EditFileResume)
            EditFileText = parsers.inv_parse_cv_out(resume_dict)
    elif type == "ref":
        if RefFileResume is not None:
            resume_dict = resume_to_dict(RefFileResume)
            RefFileText = parsers.inv_parse_cv(resume_dict)

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
        update_resume_text_vars(type=file_type)
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
        if not isinstance(content,dict) and content != None:
            if isinstance(content,list):
                content_str = ", ".join(content)
                self.content = tk.StringVar(value=content_str)
            else:
                self.content = tk.StringVar(value=str(content))
        else:
            self.content = content
    def __repr__(self):
        return f"SubSection(title={self.title}: {str(self.content)})"

    def draw_self(self, container):
        if self.content != {}:
            frame = ttk.Frame(container)
            frame.pack(side='top', fill='both', expand=True, padx=1, pady=1)
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
            title.pack(padx=10, pady=10, fill='both', expand=True)
            if isinstance(self.content, tk.StringVar):
                content_str = self.content.get()
                if self.title not in ["Technical Skills", "Soft Skills","Programming Languages"]:
                    width = max(10, min(100, max(len(line) for line in content_str.split("\n")) + 2))
                    approx_lines = max(1, (len(content_str) // width) + 1)
                    text_widget = tk.Text(frame_edit, width=width, height=approx_lines, wrap='word')
                else:
                    width = max(10, min(100, max(len(line) for line in content_str.split("\n")) + 2))
                    approx_lines = max(1, (len(content_str) // width) + 1)
                    text_widget = tk.Text(frame_edit, height=approx_lines, wrap='word')
                text_widget.insert('1.0', content_str)
                text_widget.pack(padx=10, pady=10, side="top", fill='both', expand=True)
                def update_var(event, var=self.content, widget=text_widget):
                    var.set(widget.get('1.0', 'end-1c'))
                text_widget.bind('<KeyRelease>', update_var)
            for subsection in self.__dict__.values():
                if hasattr(subsection, "draw_self"):
                    print("Drawing SubSection:", subsection.title)
                    print("Content:", subsection.content)
                    subsection.draw_self(frame_edit)

            # text_label = ttk.Label(frame_txt, textvariable=self.content)
            # text_label.pack(padx=10, pady=10, side="left")

    def add_subsection(self, name, value):
        subsec = ResumeSubSection(title=name, content=value)
        setattr(self, name, subsec)
        

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
    
    def add_skill_subsection(self, name, value):
        subsec = SkillSubSection(title=name, value=value)
        setattr(self, name, subsec)
    
    def __repr__(self):
        additional = ""
        for subsection in self.__dict__.values():
            if subsection != self.title and subsection != self.value:
                additional += f"    {subsection}\n"
        return f"Section(title={self.title} : {str(self.value)})\n" + f"{additional}"
    
    def draw_self(self, container, parent=None, section_name=None):
        print(f"Drawing Section: {self.title}")
        SectionFrame = ttk.Frame(container, style='Rounded.TFrame', borderwidth=1, relief='solid')
        SectionFrame.pack(side='top', fill='both', expand=True, padx=6, pady=6)

        top_row = ttk.Frame(SectionFrame)
        top_row.pack(fill='x',padx=1, pady=1)
        SectionTitle = ttk.Label(top_row, text=self.title, font=("Arial", 16))
        SectionTitle.pack(padx=10, pady=10, anchor="nw", fill='both', expand=True, side='left')
        if parent and section_name is not None:
            delete_btn = ttk.Button(top_row, text=" - ", command=lambda: self.delete_section(SectionFrame, parent, section_name))
            delete_btn.pack(padx=10, pady=10, side='right')

        if isinstance(self.value, tk.StringVar):
            print(f"Section value is a tk.StringVar: {self.value.get()}")
            content_str = self.value.get()
            width = max(10, min(100, max(len(line) for line in content_str.split("\n")) + 2))
            approx_lines = max(1, (len(content_str) // width) + 1)
            ContentFrame = ttk.Frame(SectionFrame)
            ContentFrame.pack(side='top', fill='both', expand=True, padx=1, pady=1)
            ContentEntryFrame = ttk.Frame(ContentFrame)
            ContentEntryFrame.pack(side='top', fill='both', expand=True)
            text_widget = tk.Text(ContentEntryFrame, width=width, height=approx_lines, wrap='word')
            text_widget.insert('1.0', content_str)
            text_widget.pack(padx=10, pady=10, side="top", fill='both', expand=True)
            def update_var(event, var=self.value, widget=text_widget):
                var.set(widget.get('1.0', 'end-1c'))
            text_widget.bind('<KeyRelease>', update_var)

        elif isinstance(self.value, list):
            print(f"Section value is a list with len: {len(self.value)}")
            for idx, section in enumerate(self.value):
                if hasattr(section, "draw_self"):
                    print(f"Recursive: Drawing Section {section.title} inside {self.title}")
                    section.draw_self(SectionFrame, parent=self, section_name=idx)

        for key, subsection in self.__dict__.items():
            if hasattr(subsection, "draw_self"):
                print("Drawing SubSection:", subsection.title)
                print("Content:", subsection.content)
                subsection.draw_self(SectionFrame)

    def delete_section(self, frame, parent, section_name):
        frame.destroy()
        # Remove from parent (works for both attribute and list index)
        if isinstance(parent, Resume):
            if hasattr(parent, section_name):
                delattr(parent, section_name)
        elif isinstance(parent, ResumeSection) and isinstance(section_name, int) and isinstance(parent.value, list):
            try:
                parent.value.pop(section_name)
            except Exception:
                pass
        elif hasattr(parent, section_name):
            delattr(parent, section_name)
        
                      
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
        global RefFileResume, EditFileScrollableFrame
        top_frame = ttk.Frame(container)

        top_frame.pack(fill='x',padx=1, pady=1)
        resume_label = ttk.Label(top_frame, text=self.title, font=("Arial", 16, "bold"))
        resume_label.pack(padx=10, pady=10, anchor="nw", fill='both', expand=True, side='left')
        if RefFileResume is not None:
            add_frame = ttk.Frame(top_frame)
            add_frame.pack(side='right')
            add_section_btn = ttk.Button(top_frame, text=" + ", command=lambda: self.check_reference_match(add_frame, EditFileScrollableFrame))
            add_section_btn.pack(padx=10, pady=10, side='right')
        resume_frame = ttk.Frame(container)
        resume_frame.pack(side = 'top', fill='both', expand=True)
        
        
        for key, section in self.__dict__.items():
            if hasattr(section, "draw_self"):
                print(f"Section: {section.title} has draw_self attibute, drawing...")
                section.draw_self(resume_frame, parent=self, section_name=key)
    def check_reference_match(self, menu_container, sections_container):
        global RefFileResume
        for widget in menu_container.winfo_children():
            widget.destroy()
        #Meant to be called by a button
        #Compares resume sections vs reference sections
        #On call: Displays dropdown of missing sections
            #On dropdown selection: adds the missing section to the resume
                #Call draw_self on resume to refresh display
        sections = {}
        for key, section in RefFileResume.__dict__.items():
            if hasattr(section, "draw_self"):
                if not hasattr(self, key):
                    sections[key] = section
        if sections != {}:
            def add_section_callback(selected_key):
                selected_section = sections[selected_key]
                self.add_section(selected_key, selected_section)
                #Refresh display
                clear_frame(sections_container)
                self.order_sections()
                self.draw_self(sections_container)
                

            section_names = list(sections.keys())
            selected_section = tk.StringVar()
            selected_section.set(section_names[0])  # Set default value

            dropdown = ttk.OptionMenu(menu_container, selected_section, section_names[0], *section_names)
            dropdown.pack(side='left', padx=10, pady=10)

            add_button = ttk.Button(menu_container, text="Add Section", command=lambda: add_section_callback(selected_section.get()))
            add_button.pack(side='left', padx=10, pady=10)
        
    def order_sections(self):
        #Reorders sections to a standard order
        standard_order = ["Name", "Contact Information", "Title", "Summary", "Languages", "Education", "Certifications", "Awards and Scholarships", "Volunteering and Leadership", "Work Experience", "Projects", "Skills"]
        ordered_sections = {}
        for section_name in standard_order:
            if hasattr(self, section_name):
                ordered_sections[section_name] = getattr(self, section_name)
        #Add any remaining sections that were not in the standard order
        for key, section in self.__dict__.items():
            if key not in ordered_sections and hasattr(section, "draw_self"):
                ordered_sections[key] = section
        #Reassign sections in the new order
        for key in list(self.__dict__.keys()):
            if hasattr(self, key) and hasattr(getattr(self, key), "draw_self"):
                delattr(self, key)
        for key, section in ordered_sections.items():
            setattr(self, key, section)


class StandardResume(Resume):
    def __init__(self, name="Standard Resume", resume_data={}, separate_sk = True):
        #Assumes separate skill data
        self.resume_data = resume_data
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
        self.add_section("Volunteering and Leadership", VolunteeringAndLeadership(value=resume_data.get("volunteering_and_leadership", []),separate_sk=separate_sk))
        print(f"Work Experience: {resume_data.get("work_experience", [])}")
        self.add_section("Work Experience", WorkExperience(value=resume_data.get("work_experience", []),separate_sk=separate_sk))
        print(f"Projects: {resume_data.get("projects", [])}")
        self.add_section("Projects", Projects(value=resume_data.get("projects", []),separate_sk=separate_sk))
        if separate_sk:
            print(f"Skills: {resume_data.get("skills", {})}")
            self.add_section("Skills", Skills(value=resume_data.get("skills", {}))) 

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
        val_tmp = ", ".join(value)
        self.value = tk.StringVar(value= val_tmp)
class EducationObject(ResumeSection):
    def __init__(self, title="Education Object", education_info={}):
        super().__init__(title)
        self.add_subsection("Degree", value=education_info.get("degree", ""))
        self.add_subsection("University", value=education_info.get("university", ""))
        self.add_subsection("Location", value=education_info.get("location", ""))
        self.add_subsection("Duration", value=education_info.get("duration", ""))
        courses_tmp = education_info.get("courses", [])
        courses_tmp = ", ".join(courses_tmp)
        self.add_subsection("Courses", value=courses_tmp)
class Education(ResumeSection): 
    def __init__(self, title="Education", value=[]): #list of dicts as input
        super().__init__(title)
        i = 0
        tmp_edu_list = []
        for edu in value:
            tmp_edu = EducationObject(title=f"{edu.get("degree", f"Education{i+1}")}", education_info=edu)
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
            tmp_cert = CertificationsObject(title=f"{cert.get("certification_name", f"Certification{i+1}")}", value=cert)
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
            tmp_award = AwardsAndScholarshipsObject(title=f"{award.get("award_name", f"Award{i+1}")}", value=award)
            i += 1
            tmp_award_list.append(tmp_award)
        self.value = tmp_award_list
class VolunteeringAndLeadershipObject(ResumeSection):
    def __init__(self, title="Volunteering and Leadership Object", value={}, separate_sk=True):
        super().__init__(title)
        self.add_subsection("Role", value=value.get("role", ""))
        self.add_subsection("Organization", value=value.get("organization", ""))
        self.add_subsection("Location", value=value.get("location", ""))
        self.add_subsection("Duration", value=value.get("duration", ""))
        desc_tmp = value.get("description", [])
        desc_tmp = ". ".join(desc_tmp)
        self.add_subsection("Description", value=desc_tmp)
        if not separate_sk:
            self.add_skill_subsection("Skills", value=value.get("skills", {}))
        for key, val in value.items():
            if key not in {"role", "organization", "duration", "location", "description", "skills"}:
                self.add_subsection(key, value=val)

class VolunteeringAndLeadership(ResumeSection):
    def __init__(self, title="Volunteering and Leadership", value=[], separate_sk=True): #list of dicts as input
        super().__init__(title)
        i = 0
        tmp_vol_list = []
        for vol in value:
            tmp_vol = VolunteeringAndLeadershipObject(title=f"{vol.get("role", f"Volunteering/Leadership{i+1}")}", value=vol, separate_sk=separate_sk)
            i += 1
            tmp_vol_list.append(tmp_vol)
        self.value = tmp_vol_list
class WorkExperienceObject(ResumeSection):
    def __init__(self, title="Work Experience Object", value={},separate_sk=True):
        super().__init__(title)
        self.add_subsection("Job Title", value=value.get("job_title", ""))
        self.add_subsection("Company", value=value.get("company", ""))
        self.add_subsection("Location", value=value.get("location", ""))
        self.add_subsection("Duration", value=value.get("duration", ""))
        desc_tmp = value.get("description", [])
        desc_tmp = ". ".join(desc_tmp)
        self.add_subsection("Description", value=desc_tmp)
        if not separate_sk:
            self.add_skill_subsection("Skills", value=value.get("skills", {}))
        for key, val in value.items():
            if key not in {"job_title", "company", "location", "duration", "description", "skills"}:
                self.add_subsection(key, value=val)
class WorkExperience(ResumeSection):
    def __init__(self, title="Work Experience", value=[], separate_sk=True): #list of dicts as input
        super().__init__(title)
        i = 0
        tmp_work_list = []
        for work in value:
            tmp_work = WorkExperienceObject(title=f"{work.get("job_title", f"WorkExperience{i+1}")}", value=work, separate_sk=separate_sk)
            i += 1
            tmp_work_list.append(tmp_work)
        self.value = tmp_work_list
class ProjectsObject(ResumeSection):
    def __init__(self, title="Project Object", value={}, separate_sk=True):
        super().__init__(title)
        self.add_subsection("Project Title", value=value.get("project_title", ""))
        self.add_subsection("URL", value=value.get("url", ""))
        self.add_subsection("Type", value=value.get("type", ""))
        self.add_subsection("Duration", value=value.get("duration", ""))
        desc_tmp = value.get("description", [])
        desc_tmp = ". ".join(desc_tmp)
        self.add_subsection("Description", value=desc_tmp)
        if not separate_sk:
            self.add_skill_subsection("Skills", value=value.get("skills", {}))
        for key, val in value.items():
            if key not in {"project_title", "description", "type", "location", "duration", "skills", "url"}:
                self.add_subsection(key, value=val)
class Projects(ResumeSection):
    def __init__(self, title="Projects", value=[], separate_sk=True): #list of dicts as input
        super().__init__(title)
        i = 0
        tmp_project_list = []
        for project in value:
            tmp_project = ProjectsObject(title=f"{project.get("project_title", f"Project{i+1}")}", value=project, separate_sk=separate_sk)
            i += 1
            tmp_project_list.append(tmp_project)
        self.value = tmp_project_list
class Skills(ResumeSection):
    def __init__(self, title="Skills", value={}): #dict as input
        super().__init__(title)
        self.add_subsection("Programming Languages", value=value.get("programming_languages", []))
        self.add_subsection("Technical Skills", value=value.get("technical_skills", []))
        self.add_subsection("Soft Skills", value=value.get("soft_skills", []))
        
class SkillSubSection(ResumeSubSection):
    def __init__(self, title="Skills", value={}):
        super().__init__(title,value)
        for key, val in value.items():
            key_formatted = key.replace("_", " ").title()
            if isinstance(val, list):
                val = ", ".join(val)
            self.add_subsection(key_formatted, value=val)
#Application code
MainWindow = TkinterDnD.Tk()
MainWindow.title("Sisyphus Resume Editor")
# Custom style for rounded border frames
style = ttk.Style()
style.configure('Rounded.TFrame', background='#f8f8f8', borderwidth=1, relief='solid')
try:
    style.element_create('RoundedFrame', 'from', 'clam')
    style.layout('Rounded.TFrame', [
        ('RoundedFrame', {'sticky': 'nswe'})
    ])
except Exception:
    pass  # fallback if not supported

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

    
