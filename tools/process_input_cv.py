import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import filedialog, messagebox
import os

# Color scheme from init_color
BG_COLOR = "#3F1111"
FG_COLOR = "#ffa013"

# UI setup
def remove_duplicates(text):
    items = text.strip().split(",")
    unique_items = list(set(item.strip() for item in items))
    text = ", ".join(unique_items)
    return text

def rmv_dupe_skills(cv_text):
    print("[DEBUG] rmv_dupe_skills")
    lines = cv_text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("[1]Skills"):
            print(f"[DEBUG] rmv_dupe_skills: line (before): {line}")
            types = line.split(":")
            types = [type.strip() for type in types]
            header = types[0]
            print(f"[DEBUG] rmv_dupe_skills: header: {header}")
            content = ": ".join(types[1:]).strip()
            print(f"[DEBUG] rmv_dupe_skills: content: {content}")
            subheaders = content.split(";")
            print(f"[DEBUG] rmv_dupe_skills: subheaders (before): {subheaders}")
            new_subheaders = []
            for subheader in subheaders:
                print(f"[DEBUG] rmv_dupe_skills: subheader (before): {subheader}")
                subheader_temp = subheader.split(": ")
                print(f"[DEBUG] rmv_dupe_skills: subheader_temp (before strip): {subheader_temp}")
                subheader_temp = [subheader.strip() for subheader in subheader_temp]
                print(f"[DEBUG] rmv_dupe_skills: subheader_temp (after strip): {subheader_temp}")
                if len(subheader_temp) == 2:
                    subheader_temp[1] = remove_duplicates(subheader_temp[1])
                    print(f"[DEBUG] rmv_dupe_skills: subheader_temp[1] (processed): {subheader_temp[1]}")
                subheader = ": ".join(subheader_temp)
                print(f"[DEBUG] rmv_dupe_skills: subheader (after): {subheader}")
                new_subheaders.append(subheader)
            print(f"[DEBUG] rmv_dupe_skills: subheaders (after): {new_subheaders}")
            modified_line = header + ": " + "; ".join(new_subheaders)
            print(f"[DEBUG] rmv_dupe_skills: line (after): {modified_line}")
            lines[i] = modified_line
    return "\n".join(lines)

class InputCVProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Process Input Curriculum Vitae")
        self.init_color(BG_COLOR, FG_COLOR)
        self.file_path = tk.StringVar()
        self.remove_dupes_var = tk.BooleanVar()

        # File selection field
        tk.Label(root, text="Select Text File:", bg=BG_COLOR, fg=FG_COLOR).grid(row=0, column=0, padx=10, pady=10)
        self.file_entry = tk.Entry(root, textvariable=self.file_path, width=50, bg=BG_COLOR, fg=FG_COLOR, insertbackground=FG_COLOR)
        self.file_entry.grid(row=0, column=1, padx=10, pady=10)
        browse_btn = tk.Button(root, text="Browse", command=self.browse_file, bg=BG_COLOR, fg=FG_COLOR)
        browse_btn.grid(row=0, column=2, padx=10, pady=10)

        # Checkbox for removing duplicate skills
        self.remove_dupes_checkbox = tk.Checkbutton(root, text="Remove Duplicate Skills", variable=self.remove_dupes_var, bg=BG_COLOR, fg=FG_COLOR, selectcolor=BG_COLOR)
        self.remove_dupes_checkbox.grid(row=1, column=1, sticky="w", padx=10)

        # Process button
        process_btn = tk.Button(root, text="Process File", command=self.process_file, bg=BG_COLOR, fg=FG_COLOR)
        process_btn.grid(row=2, column=0, columnspan=3, pady=20)

    def init_color(self, bg_color, fg_color):
        self.root.configure(bg=bg_color)
        self.root.option_add("*Background", bg_color)
        self.root.option_add("*Foreground", fg_color)
        self.root.option_add("*insertBackground", fg_color)
        self.root.option_add("*highlightBackground", bg_color)
        self.root.option_add("*highlightColor", fg_color)
        self.root.option_add("*selectBackground", fg_color)
        self.root.option_add("*selectForeground", bg_color)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            self.file_path.set(file_path)


    def process_file(self):
        path = self.file_path.get()
        if not path or not os.path.isfile(path):
            messagebox.showerror("Error", "Please select a valid text file.")
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            processed = text.strip()
            if self.remove_dupes_var.get():
                processed = rmv_dupe_skills(processed)
                messagebox.showinfo("Success", "Duplicate skills removed and file updated.")
            with open(path, "w", encoding="utf-8") as f:
                f.write(processed)
            messagebox.showinfo("Success", "File processed and updated.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process file: {e}")

    


if __name__ == "__main__":
    root = tk.Tk()
    app = InputCVProcessorApp(root)
    root.mainloop()
