import tkinter as tk
from tkinter import filedialog, ttk
import ast
import os
import autopep8

LONG_METHOD_THRESHOLD = 15
LONG_PARAMETER_THRESHOLD = 3
DUPLICATED_CODE_THRESHOLD = 0.75
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
        self.refactor_button = tk.Button(root, text="Refactor Duplicated Code", command=self.refactor_button, font=FONT_TUPLE)

        self.progress_bar = ttk.Progressbar(root, orient='horizontal', length=160)
        self.progress_bar.place(x=30, y=30)

        self.uploaded_file = tk.Text(root, height=1, width=100, bg="light yellow", font=FONT_TUPLE)
        self.code_smell_results = tk.Text(root, height=18, width=100, bg="light cyan", font=FONT_TUPLE)
        self.refactor_results = tk.Text(root, height=1, width=100, bg="light cyan", font=FONT_TUPLE)

        self.upload_button.pack(pady=20)
        self.uploaded_file.pack()
        self.detect_button.pack(pady=20)
        self.progress_bar.pack()
        self.code_smell_results.pack(pady=20)
        self.clear_button.pack()
        self.refactor_button.pack_forget()
        self.refactor_results.pack_forget()

    def upload_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if self.file_path != "":
            self.uploaded_file.config(state="normal")
            self.uploaded_file.delete('1.0', tk.END)
            self.uploaded_file.insert(tk.END, "File Uploaded: " + self.file_path)

    def detect_smells(self):
        if not hasattr(self, 'file_path') or not self.file_path:
            self.uploaded_file.insert(tk.END, f"No file selected!")
        else:
            self.progress_bar.start()
            self.progress_bar.after(PROGRESS_BAR_TIME, self.display_results)

    def display_results(self):
        self.progress_bar.stop()
        self.analyze_code(self.file_path)
        
    def display_duplicates(self, duplicated_functions):
        self.refactor_button.pack(pady=20)
        self.refactor_results.pack()
        self.code_smell_results.insert(tk.END, "\nDuplicated Functions Detected:\n")
        for function1, function2, similarity in duplicated_functions:
            self.code_smell_results.insert(tk.END, f"Functions: {function1} and {function2}, Similarity: {similarity}\n")

    def clear_text_fields(self):
        self.uploaded_file.config(state="normal")
        self.uploaded_file.delete('1.0', tk.END)
        self.code_smell_results.delete('1.0', tk.END)
        self.refactor_button.pack_forget()
        self.refactor_results.pack_forget()
        self.file_path = ""
        
    def refactor_button(self):
        self.progress_bar.start()
        self.progress_bar.after(PROGRESS_BAR_TIME, self.refactor_duplicated_code)

    def refactor_duplicated_code(self):
        self.progress_bar.stop()
        code_content = self.read_file_content(self.file_path)

        functions = self.extract_functions(code_content)

        duplicates = self.detect_duplicate_functions(functions)

        code_content = self.remove_duplicates_and_refactor(code_content, duplicates)

        refactored_file_path = self.write_refactored_code_to_file(code_content)

        self.refactor_results.insert(tk.END, f"Refactoring Complete. Refactored code written to {refactored_file_path}")

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
        code_content = self.read_file_content(file_path)
        tree = ast.parse(code_content)
        
        functions = {}
        detected = False

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if len(node.body) > LONG_METHOD_THRESHOLD:
                    detected = True
                    self.code_smell_results.insert(tk.END, f"\nLong Method/Function Detected\nFunction: {node.name}, {len(node.body)} lines\n")
                
                if len(node.args.args) > LONG_PARAMETER_THRESHOLD:
                    detected = True
                    self.code_smell_results.insert(tk.END, f"\nLong Parameter List Detected\nFunction: {node.name}, {len(node.args.args)} parameters\n")
                    
                function_code = ast.get_source_segment(code_content, node)
                functions[node.name] = function_code
                
        duplicates = self.detect_duplicate_functions(functions)

        if duplicates:
            detected = True
            self.display_duplicates(duplicates)
                
        if not detected:
            self.code_smell_results.insert(tk.END, f"No Code Smells Detected!\n")

    def read_file_content(self, file_path):
        with open(file_path, 'r') as file:
            return file.read()

    def extract_functions(self, code_content):
        functions = {}
        tree = ast.parse(code_content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_code = ast.get_source_segment(code_content, node)
                functions[node.name] = function_code
        return functions

    def remove_duplicates_and_refactor(self, code_content, duplicates):
        for name in [dup[1] for dup in duplicates]:
            function_def_start = code_content.find(f"def {name}")
            if function_def_start != -1:
                function_def_end = code_content.find('\n\n', function_def_start)
                if function_def_end == -1:
                    function_def_end = len(code_content)
                function_code = code_content[function_def_start:function_def_end]
                code_content = code_content.replace(function_code, '', 1)

        for name in [dup[1] for dup in duplicates]:
            code_content = code_content.replace(name + '(', duplicates[0][0] + '(', 1)

        return autopep8.fix_code(code_content)

    def write_refactored_code_to_file(self, code_content):
        file_name, _ = os.path.splitext(os.path.basename(self.file_path))
        refactored_file_path = f"refactored_{file_name}.py"
        with open(refactored_file_path, 'w') as refactored_file:
            refactored_file.write(code_content)
        return refactored_file_path


root = tk.Tk()
root.geometry("%dx%d" % (root.winfo_screenwidth(), root.winfo_screenheight()))
app = CodeSmellDetectorGUI(root)
root.mainloop()
