import tkinter as tk
from tkinter import filedialog

def choose_directory():
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory()
    return folder_selected