import tkinter as tk
from tkinter import filedialog, messagebox
import requests
import os

FLASK_URL = "http://127.0.0.1:5000/process"

def select_file():
    file_path = filedialog.askopenfilename(title="Select Transaction File", filetypes=[("CSV Files", "*.csv")])
    
    if not file_path:
        return

    try:
        if os.path.getsize(file_path) == 0:
            messagebox.showerror("Error", "Selected file is empty.")
            return

        response = requests.get(f"{FLASK_URL}", params={"file_path": file_path})

        if response.status_code == 200:
            result = response.json()
            messagebox.showinfo("Recommendations", f"Suggested Services: {', '.join(map(str, result['recommended_services']))}")
        else:
            messagebox.showerror("Error", response.json().get("error", "Unknown error"))
    except Exception as e:
        messagebox.showerror("Request Failed", f"Could not connect to server:\n{e}")

# GUI Window
root = tk.Tk()
root.title("Bank Service Recommender")

label = tk.Label(root, text="Select a transaction file:", font=("Arial", 12))
label.pack(pady=10)

btn = tk.Button(root, text="Choose File", command=select_file, font=("Arial", 12), bg="blue", fg="white")
btn.pack(pady=10)

root.mainloop()
