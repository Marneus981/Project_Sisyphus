import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import tqdm
import datetime

# Color scheme from init_color
BG_COLOR = "#3F1111"
FG_COLOR = "#ffa013"

SAVE_PATH = r"C:\CodeProjects\Sisyphus\tools\log_reader_output"

# UI setup
def process_log(processed = "",by_iter = True, by_step  = False, rsrv_trcbck = True):
    # global progressbar
    if processed == "":
        raise ValueError("[ERROR]Empty log file")
    by_iter_list = []
    current_iter = ""
    by_step_list = []
    current_step = ""
    rsrv_trcbck_list = []
    lines = processed.splitlines()
    lines_l = len(lines)
    # steps = 0
    progress_bar_0 = tqdm.tqdm(total=lines_l)
    for line in lines:
        line = line.strip()
        if "[BATCH][START]Parameters: start_n: " in line:
            if current_iter == "":
                current_iter = line
            else:
                by_iter_list.append(current_iter)
                current_iter = line
        else:
            if current_iter != "":
                current_iter = current_iter +"\n"+ line

        if "[STEP " in line and "][INPUT]" in line:
            if current_step == "":
                current_step = line
            else:
                by_step_list.append(current_step)
                current_step = line
        else:
            if current_step != "":
                current_step = current_step +"\n"+ line
        progress_bar_0.update(1) 
    if current_step != "":
        by_step_list.append(current_step)
    else:
        by_step_list =[processed]
    if current_iter != "":
        by_iter_list.append(current_iter)
    else:
        by_iter_list =[processed]
    if rsrv_trcbck:
        if by_step:
            progress_bar_1 = tqdm.tqdm(total=len(by_step_list))
            for step in by_step_list:
                if "Traceback:" in step:
                    rsrv_trcbck_list.append(step)
                progress_bar_1.update(1)
        elif by_iter:
            progress_bar_2 = tqdm.tqdm(total=len(by_step_list))
            for iter in by_iter_list:
                if "Traceback:" in iter:
                    rsrv_trcbck_list.append(iter)
                progress_bar_2.update(1)
    else:
        if by_step:
            progress_bar_1 = tqdm.tqdm(total=len(by_step_list))
            for step in by_step_list:
                rsrv_trcbck_list.append(step)
                progress_bar_1.update(1)
        elif by_iter:
            progress_bar_2 = tqdm.tqdm(total=len(by_step_list))
            for iter in by_iter_list:
                rsrv_trcbck_list.append(iter)
                progress_bar_2.update(1)
    date= datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"folder_{date}"
    folder_path = os.path.join(SAVE_PATH, folder_name)
    if os.path.exists(SAVE_PATH):
        print(f"[WARNING]{SAVE_PATH} already exists.")
    else:
        os.mkdir(SAVE_PATH)
    if os.path.exists(folder_path):
        print(f"[WARNING]{folder_path} already exists.")
    else:
        os.mkdir(folder_path)
    no = 0
    for traceback in rsrv_trcbck_list:
        output_name = f"{no}_traceback_log.txt"
        file_path = os.path.join(folder_path, output_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(traceback)
        no = no + 1
    # progressbar.step(100)
    print(f"[INFO]by_iter_list LENGTH: {len(by_iter_list)}; by_step_list LENGTH: {len(by_step_list)}; rsrv_trcbck_list LENGTH: {len(rsrv_trcbck_list)};")
    return

class LogProcessorApp:
    def __init__(self, root):
        # global progressbar
        self.root = root
        self.root.title("Process Batch Applications Log")
        self.init_color(BG_COLOR, FG_COLOR)
        self.file_path = tk.StringVar()
        self.split_by_iter_var = tk.BooleanVar()
        self.split_by_step_var = tk.BooleanVar()
        self.reserve_tracebacks = tk.BooleanVar()

        # File selection field
        tk.Label(root, text="Select Text File:", bg=BG_COLOR, fg=FG_COLOR).grid(row=0, column=0, padx=10, pady=10)
        self.file_entry = tk.Entry(root, textvariable=self.file_path, width=50, bg=BG_COLOR, fg=FG_COLOR, insertbackground=FG_COLOR)
        self.file_entry.grid(row=0, column=1, padx=10, pady=10)
        browse_btn = tk.Button(root, text="Browse", command=self.browse_file, bg=BG_COLOR, fg=FG_COLOR)
        browse_btn.grid(row=0, column=2, padx=10, pady=10)

        # Checkbox for splitting by iteration
        self.split_by_iter = tk.Checkbutton(root, text="Split log by iterations", variable=self.split_by_iter_var, bg=BG_COLOR, fg=FG_COLOR, selectcolor=BG_COLOR)
        self.split_by_iter.grid(row=1, column=1, sticky="w", padx=10)

        # Checkbox for splitting by iteration
        self.split_by_iter = tk.Checkbutton(root, text="Split log by STEP", variable=self.split_by_step_var, bg=BG_COLOR, fg=FG_COLOR, selectcolor=BG_COLOR)
        self.split_by_iter.grid(row=2, column=1, sticky="w", padx=10)

        # Checkbox for splitting by iteration
        self.split_by_iter = tk.Checkbutton(root, text="Reserve tracebacks", variable=self.reserve_tracebacks, bg=BG_COLOR, fg=FG_COLOR, selectcolor=BG_COLOR)
        self.split_by_iter.grid(row=3, column=1, sticky="w", padx=10)

        # Process button
        process_btn = tk.Button(root, text="Process File", command=self.process_file, bg=BG_COLOR, fg=FG_COLOR)
        process_btn.grid(row=4, column=0, columnspan=3, pady=20)

        # # Progress bar
        # progressbar = ttk.Progressbar(orient=tk.HORIZONTAL, length=320)
        # progressbar.grid(row=5,column=0,sticky="w",columnspan=3,padx=10, pady=10)

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
        file_path = filedialog.askopenfilename(filetypes=[("Log files", "*.log")])
        if file_path:
            self.file_path.set(file_path)


    def process_file(self):
        path = self.file_path.get()
        if not path or not os.path.isfile(path):
            messagebox.showerror("[ERROR]", "Please select a valid log file.")
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            processed = text.strip()
            by_iter = self.split_by_iter_var.get()
            by_step = self.split_by_step_var.get()
            rsrv_trcbck = self.reserve_tracebacks.get()
            process_log(processed,by_iter, by_step,rsrv_trcbck)
            messagebox.showinfo("[SUCCESS]", "Check log_reader_output folder.")
        except Exception as e:
            messagebox.showerror("[ERROR]", f"Failed to process log file: {e}")

    


if __name__ == "__main__":
    root = tk.Tk()
    app = LogProcessorApp(root)
    root.mainloop()
