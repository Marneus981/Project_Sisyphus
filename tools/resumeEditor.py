import tkinter
from tkinter import ttk
import sv_ttk
import darkdetect
import pywinstyles
import sys

#Resume Editor Tool (opened at the end of a tailor or batch tailor cycle)

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

MainWindow = tkinter.Tk()

#UI Elements (UI elements must be boxed in and clearly separated from one another)
#Test Button
TrialButton = ttk.Button(MainWindow, text="Click me!")
TrialButton.pack()

#"Parameters"
    #Load (Drag and drop/input address) txt File to Edit
    #Load (Drag and drop) Reference txt CV File
    #[ToBeImplementedAtALaterDate]Scrap LinkedIn Job Page
    #Load (Drag and drop/input address) Job Desc from txt File
    #Text Field (Writeable, updates on File Job Desc Load) 
    #"Generate Keywords(AI)" button
    #Text Field (Writeable, updates on "Generate Keywords(AI)" button) 
    #[ToBeImplementedAtALaterDate]"Separate Skills" on write toggle?

#"Editable/Reference Display"
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

#"Save/Export"
#Save text file pop-up (defaults to rewriting loaded editable file if provided)
    #Save dir defaults to Sisyphus\saved_outputs
#Save to odt or docx button
    #Save dir dafaults to Sisyphus\saved_docs
#[ToBeImplementedAtALaterDate] Save to pdf button
    #Save dir dafaults to Sisyphus\saved_docs

#Apply theme
sv_ttk.set_theme(darkdetect.theme())
apply_theme_to_titlebar(MainWindow)
MainWindow.mainloop()

    
