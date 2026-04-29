import tkinter as tk
from tkinter import filedialog


def open_file():
    file_path = filedialog.askopenfilename(
        title="Select a Text File", filetypes=[("Text files", "*.txt")]
    )
    if file_path:
        with open(file_path, "r") as file:
            content = file.read()  # Fixed: was [file.read](http://file.read)()
            text_widget.delete(1.0, tk.END)
            text_widget.insert(tk.END, content)


root = tk.Tk()  # Fixed: was [tk.Tk](http://tk.Tk)()
root.title("Text File Reader")

text_widget = tk.Text(root, wrap="word", width=40, height=10)
text_widget.pack(pady=10)

open_button = tk.Button(root, text="Open File", command=open_file)
open_button.pack(pady=10)

root.mainloop()
