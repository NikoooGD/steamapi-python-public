import subprocess
import tkinter as tk
from tkinter import filedialog


def open_file():
    file_path = filedialog.askopenfilename(
        title="Select a Python File", filetypes=[("Python files", "*.py")]
    )
    if file_path:
        # TODO: Execute the file and capture output
        # Hint: Use subprocess.run() or subprocess.Popen()
        pass


root = tk.Tk()
root.title("Python Script Executor")

text_widget = tk.Text(root, wrap="word", width=40, height=10)
text_widget.pack(pady=10)

open_button = tk.Button(root, text="Open & Run File", command=open_file)
open_button.pack(pady=10)

root.mainloop()
