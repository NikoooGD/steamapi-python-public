import subprocess
import tkinter as tk
from tkinter import filedialog


def open_file():
    file_path = filedialog.askopenfilename(
        title="Select a Python File", filetypes=[("Python files", "*.py")]
    )
    if file_path:
        try:
            # Execute the Python script and capture output
            result = subprocess.run(
                ["python3", file_path],
                capture_output=True,  # Capture stdout and stderr
                text=True,  # Return output as strings (not bytes)
                timeout=30,  # Prevent hanging (30 second limit)
            )

            # Clear the text widget
            text_widget.delete(1.0, tk.END)

            # Display the script path
            text_widget.insert(tk.END, f"Script: {file_path}\n")
            text_widget.insert(tk.END, "-" * 50 + "\n\n")

            # Show stdout (the print statements)
            if result.stdout:
                text_widget.insert(tk.END, result.stdout)

            # Show stderr (errors) in red if they exist
            if result.stderr:
                text_widget.insert(tk.END, f"\nErrors:\n{result.stderr}")

        except subprocess.TimeoutExpired:
            text_widget.delete(1.0, tk.END)
            text_widget.insert(tk.END, "Error: Script took too long to run (>30s)")
        except Exception as e:
            text_widget.delete(1.0, tk.END)
            text_widget.insert(tk.END, f"Error: {str(e)}")


root = tk.Tk()
root.title("Python Script Executor")

text_widget = tk.Text(root, wrap="word", width=40, height=10)
text_widget.pack(pady=10)

open_button = tk.Button(root, text="Open & Run File", command=open_file)
open_button.pack(pady=10)

root.mainloop()
