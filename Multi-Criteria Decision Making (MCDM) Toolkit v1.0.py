import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import rasterio
from rasterio.transform import from_origin
import matplotlib.pyplot as plt


def ahp_method(dataset):
    inc_rat = np.array([0, 0, 0.58, 0.9, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49, 1.51, 1.48, 1.56, 1.57, 1.59])
    size = dataset.shape[0]
    weights = np.mean(dataset / np.sum(dataset, axis=0), axis=1)
    vector = np.sum(dataset * weights, axis=1)
    lamb_max = np.mean(vector / weights)
    ci = (lamb_max - size) / (size - 1) if size > 1 else 0
    cr = ci / inc_rat[size - 1] if size > 1 else 0
    return weights, ci, cr



class AHPApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Multi-Criteria Decision Making (MCDM) Toolkit")

        self.variables = []
        self.files = {}
        
        self.weights = None
        self.cr = None
        self.ci = None

        self.add_variable_section()
        self.add_matrix_section()
        self.add_calculate_section()
        self.add_upload_section()

    def add_variable_section(self):
        tk.Label(self.master, text="Enter Variable Names").grid(row=0, column=0, padx=10, pady=10, columnspan=2)
        self.var_entry = tk.Entry(self.master, width=30)
        self.var_entry.grid(row=1, column=0, padx=10, pady=10)
        tk.Button(self.master, text="Add Variable", command=self.add_variable).grid(row=1, column=1, padx=10, pady=10)

    def add_variable(self):
        variable = self.var_entry.get()
        if variable and variable not in self.variables:
            self.variables.append(variable)
            self.update_matrix()
        self.var_entry.delete(0, tk.END)

    def update_matrix(self):
        for widget in self.matrix_frame.winfo_children():
            widget.destroy()

        size = len(self.variables)
        self.matrix_entries = [[tk.Entry(self.matrix_frame, width=10) for _ in range(size)] for _ in range(size)]

        for i, var in enumerate(self.variables):
            tk.Label(self.matrix_frame, text=var).grid(row=i + 1, column=0)
            tk.Label(self.matrix_frame, text=var).grid(row=0, column=i + 1)
            for j in range(size):
                entry = self.matrix_entries[i][j]
                entry.grid(row=i + 1, column=j + 1)
                if i == j:
                    entry.insert(0, "1")
                    entry.config(state="disabled")

        self.matrix_frame.update_idletasks()

    def add_matrix_section(self):
        tk.Label(self.master, text="Pairwise Comparison Matrix").grid(row=2, column=0, padx=10, pady=10, columnspan=2)
        self.matrix_frame = tk.Frame(self.master)
        self.matrix_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    def add_calculate_section(self):
        self.calculate_button = tk.Button(self.master, text="Calculate CR & CI", command=self.calculate_cr_ci)
        self.calculate_button.grid(row=4, column=0, padx=10, pady=10)

        self.result_label = tk.Label(self.master, text="")
        self.result_label.grid(row=4, column=1, padx=10, pady=10)

    def calculate_cr_ci(self):
        size = len(self.variables)
        matrix = np.zeros((size, size))
        try:
            for i in range(size):
                for j in range(size):
                    if i == j:
                        matrix[i][j] = 1
                    else:
                        value = float(self.matrix_entries[i][j].get())
                        matrix[i][j] = value
                        matrix[j][i] = 1 / value

            self.weights, self.ci, self.cr = ahp_method(matrix)

            if self.cr > 0.1:
                messagebox.showwarning("Consistency Issue", f"Consistency ratio too high: {self.cr:.3f}. Revise the matrix.")
            else:
                self.result_label.config(text=f"CI: {self.ci:.3f}, CR: {self.cr:.3f}")
                self.create_upload_buttons()

        except Exception as e:
            messagebox.showerror("Error", f"Error in computation: {e}")

    def add_upload_section(self):
        self.upload_frame = tk.Frame(self.master)
        self.upload_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    def create_upload_buttons(self):
        for widget in self.upload_frame.winfo_children():
            widget.destroy()

        for var in self.variables:
            tk.Label(self.upload_frame, text=f"Upload raster for {var}:").pack(pady=5)
            frame = tk.Frame(self.upload_frame)
            frame.pack(pady=5)
            
            # Button for browsing the file
            btn = tk.Button(frame, text="Browse", command=lambda v=var: self.upload_file(v))
            btn.pack(side=tk.LEFT, padx=5)
            
            # Label for showing the uploaded file name
            tk.Label(frame, text=f"").pack(side=tk.LEFT)
            
        tk.Button(self.master, text="Compute Suitability Map", command=self.compute_habitat_suitability).grid(row=6, column=0, padx=10, pady=10)


    def upload_file(self, variable):
        file_path = filedialog.askopenfilename(filetypes=[("TIFF files", "*.tif")])
        if file_path:
            self.files[variable] = file_path
            # Update the button label to show the file name
            for child in self.upload_frame.winfo_children():
                if isinstance(child, tk.Label) and child.cget("text").startswith(f"Upload raster for {variable}:"):
                    child.config(text=f"{variable} file uploaded: {file_path}")
            messagebox.showinfo("File Uploaded", f"{variable} file uploaded successfully.")


    def compute_habitat_suitability(self):
        if not all(var in self.files for var in self.variables):
            messagebox.showerror("Missing Files", "Please upload raster files for all variables.")
            return

        stack = []
        profile = None
        for var in self.variables:
            file_path = self.files[var]
            with rasterio.open(file_path) as src:
                stack.append(src.read(1))
                if profile is None:
                    profile = src.profile

        stack = np.array(stack)
        normalized_stack = np.array([(layer - np.min(layer)) / (np.max(layer) - np.min(layer)) for layer in stack])
        suitability_map = np.sum(normalized_stack * self.weights[:, np.newaxis, np.newaxis], axis=0)

        plt.imshow(suitability_map, cmap="viridis")
        plt.colorbar(label="Suitability")
        plt.title("Habitat Suitability Map")
        plt.show()

        # Save suitability map as TIFF
        def save_tiff():
            save_path = filedialog.asksaveasfilename(defaultextension=".tif", filetypes=[("TIFF files", "*.tif")])
            if save_path:
                profile.update(dtype=rasterio.float32, count=1)
                with rasterio.open(save_path, 'w', **profile) as dst:
                    dst.write(suitability_map.astype(np.float32), 1)
                messagebox.showinfo("Saved", "Suitability map saved successfully.")

        tk.Button(self.master, text="Save Suitability Map as TIFF", command=save_tiff).grid(row=7, column=0, padx=10, pady=10)


# Run the GUI
root = tk.Tk()
app = AHPApp(root)
root.mainloop()


