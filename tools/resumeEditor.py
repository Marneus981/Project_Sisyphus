import tkinter as tk
from tkinter import ttk, filedialog
import sv_ttk
import darkdetect
import pywinstyles
import sys
import os
from tkinterdnd2 import DND_FILES, TkinterDnD

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

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        print("Selected file:", file_path)

def drop(event):
        file_path = event.data
        if file_path.endswith('.txt'):
            print("Dropped file:", file_path)

def save_as(file_type = "edit"):
    if file_type == "edit":
        default_dir = os.path.join(os.path.dirname(__file__), '..', 'saved_outputs')
        default_dir = os.path.abspath(default_dir)
        os.makedirs(default_dir, exist_ok=True)
    elif file_type == "ref":
        default_dir = os.path.join(os.path.dirname(__file__), '..', 'cvs')
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
            f.write("Your text here")  # Replace with your actual content

def save_to_doc():
    pass  # To be implemented

MainWindow = TkinterDnD.Tk()
MainWindow.title("Sisyphus Resume Editor")

#UI Elements (UI elements must be boxed in and clearly separated from one another)
#"Parameters"

TopMenu = ttk.Frame(MainWindow, height=40)
TopMenu.pack(side='top', fill='x')
####

JobDescVar = tk.StringVar(value="Enter Job Description")  # Default text
AIKeywordsVar  = tk.StringVar(value="Enter comma-separated list of Job Description keywords")  # Default text 
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
EditFileBrowse = ttk.Button(FilesContainer, text="Browse or Drop Editable .txt File", command=lambda:browse_file(), cursor="hand2")
EditFileBrowse.grid(padx=10, pady=10, column=0, row=0, sticky='ew')
EditFileBrowse.drop_target_register(DND_FILES)
EditFileBrowse.dnd_bind('<<Drop>>', drop)
        #Load (Drag and drop) Reference txt CV File
RefFileBrowse = ttk.Button(FilesContainer, text="Browse or Drop Reference .txt File", command=lambda:browse_file(), cursor="hand2")
RefFileBrowse.grid(padx=10, pady=10, column=1, row=0, sticky='ew')
RefFileBrowse.drop_target_register(DND_FILES)
RefFileBrowse.dnd_bind('<<Drop>>', drop)


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

    
