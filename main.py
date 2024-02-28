import time
import tkinter as tk
from tkinter import DISABLED, filedialog, ttk, messagebox, Toplevel, Label
import ast
import os
import autopep8

LONG_METHOD_TRESHOLD = 15
LONG_PARAMETER_TRESHOLD = 3
DUPLICATED_CODE_THRESHOLD = 0.5
PROGRESS_BAR_TIME = 5000
POPUP_WINDOW_WIDTH = 650
POPUP_WINDOW_HEIGHT = 250
FONT_TUPLE = ("Helvetica", 20)

class CodeSmellDetectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Code Smell Detector")
        
        self.create_widgets()

    def create_widgets(self):
        self.upload_button = tk.Button(root, text="Upload File", command=self.upload_file, font=FONT_TUPLE)
        self.detect_button = tk.Button(root, text="Detect Code Smells", command=self.detect_smells, font=FONT_TUPLE)
        self.clear_button = tk.Button(root, text="Clear", command=self.clear_text_fields, font=FONT_TUPLE)
        self.refactor_button = tk.Button(root, text= "Refactor Duplicated Code", command= self.refactor_duplicated_code, font=FONT_TUPLE)

        self.progress_bar = ttk.Progressbar(root, orient='horizontal', length=160)
        self.progress_bar.place(x=30, y=30)

        self.uploaded_file = tk.Text(root, height=1, width=100, bg="light yellow", font=FONT_TUPLE)
        self.code_smell_results = tk.Text(root, height=18, width=100, bg="light cyan", font=FONT_TUPLE)

        self.upload_button.pack(pady=20)
        self.uploaded_file.pack()
        self.detect_button.pack(pady=20)
        self.progress_bar.pack()
        self.code_smell_results.pack(pady=20)
        self.clear_button.pack()
        self.refactor_button.pack_forget()


    def upload_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if (self.file_path != ""):
            self.uploaded_file.config(state="normal")
            self.uploaded_file.delete('1.0', tk.END)
            self.uploaded_file.insert(tk.END, "File Uploaded: " + self.file_path + "\n")

    def detect_smells(self):
        if not hasattr(self, 'file_path') or not self.file_path:
            self.uploaded_file.insert(tk.END, f"No file selected!\n")
        else:
            self.progress_bar.start()
            self.progress_bar.after(PROGRESS_BAR_TIME, self.display_results)

    def display_results(self):
        self.progress_bar.stop()
        self.analyze_code(self.file_path)

    def clear_text_fields(self):
        self.uploaded_file.config(state="normal")
        self.uploaded_file.delete('1.0', tk.END)
        self.code_smell_results.delete('1.0', tk.END)
        self.refactor_button.pack_forget()
        self.file_path = ""

    def refactor_duplicated_code(self):
        with open(self.file_path, 'r') as file:
            code_content = file.read()

        functions = {}
        tree = ast.parse(code_content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_code = ast.get_source_segment(code_content, node)
                functions[node.name] = function_code

        # Get the names of duplicated functions
        duplicates = self.detect_duplicate_functions(functions)

        # Extract the names of duplicated functions
        duplicate_names = [dup[1] for dup in duplicates]

        # Remove duplicate functions from the code content
        for name in duplicate_names:
            function_def_start = code_content.find(f"def {name}")
            if function_def_start != -1:
                function_def_end = code_content.find('\n\n', function_def_start)
                if function_def_end == -1:
                    function_def_end = len(code_content)
                function_code = code_content[function_def_start:function_def_end]
                code_content = code_content.replace(function_code, '', 1)

        # Replace function calls to deleted functions with the first function left
        for name in duplicate_names:
            code_content = code_content.replace(name + '(', duplicates[0][0] + '(', 1)

        # Write the refactored code to a new file
        file_name, file_extension = os.path.splitext(os.path.basename(self.file_path))
        refactored_file_path = f"refactored_{file_name}.py"
        formatted_code = autopep8.fix_code(code_content)
        with open(refactored_file_path, 'w') as refactored_file:
            refactored_file.write(formatted_code)

        self.code_smell_results.insert(tk.END, f"\nRefactoring Complete. Refactored code written to {refactored_file_path}\n")
    
    def jaccard_similarity(self, set1, set2):
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union else 0
        
    def detect_duplicate_functions(self, functions):
        duplicates = []

        function_names = list(functions.keys())
        for i in range(len(function_names)):
            for j in range(i+1, len(function_names)):
                function1 = functions[function_names[i]]
                function2 = functions[function_names[j]]
                similarity = self.jaccard_similarity(set(function1.split()), set(function2.split()))
                if similarity >= DUPLICATED_CODE_THRESHOLD:
                    duplicates.append((function_names[i], function_names[j], similarity))

        return duplicates

    def analyze_code(self, file_path):
        with open(file_path, 'r') as file:
            code_content = file.read()

        tree = ast.parse(code_content)
        
        functions = {}
        detected = False

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Detect Long Function
                if len(node.body) > LONG_METHOD_TRESHOLD:
                    detected = True
                    self.code_smell_results.insert(tk.END, f"\nLong Method/Function Detected\nFunction: {node.name}, {len(node.body)} lines\n")
                
                # Detect Long Parameter List
                if len(node.args.args) > LONG_PARAMETER_TRESHOLD:
                    detected = True
                    self.code_smell_results.insert(tk.END, f"\nLong Parameter List Detected\nFunction: {node.name}, {len(node.args.args)} parameters\n")
                    
                function_code = ast.get_source_segment(code_content, node)
                functions[node.name] = function_code
                
        duplicates = self.detect_duplicate_functions(functions)

        # Print out detected duplicated functions
        if duplicates:
            detected = True
            self.refactor_button.pack()
            self.code_smell_results.insert(tk.END, "\nDuplicated Functions Detected:\n")
            for function1, function2, similarity in duplicates:
                self.code_smell_results.insert(tk.END, f"Functions: {function1} and {function2}, Similarity: {similarity}\n")
                
        if not detected:
            self.code_smell_results.insert(tk.END, f"No Code Smells Detected!\n")


root = tk.Tk()
root.geometry("%dx%d" % (root.winfo_screenwidth(), root.winfo_screenheight()))
app = CodeSmellDetectorGUI(root)
root.mainloop()