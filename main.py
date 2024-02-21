import tkinter as tk
from tkinter import filedialog, ttk, messagebox, Toplevel, Label
import ast

LONG_METHOD_TRESHOLD = 15
LONG_PARAMETER_TRESHOLD = 3
DUPLICATED_CODE_THRESHOLD = 0.15
PROGRESS_BAR_TIME = 5000
POPUP_WINDOW_WIDTH = 650
POPUP_WINDOW_HEIGHT = 250

class CodeSmellDetectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Code Smell Detector")

        self.upload_button = tk.Button(root, text="Upload File", command=self.upload_file)
        self.detect_button = tk.Button(root, text="Detect Code Smells", command=self.detect_smells)
        self.clear_button = tk.Button(root, text="Clear", command=self.clear_text_fields)
        self.refactor_button = tk.Button(root, text= "Refactor Duplicated Code", command= self.refactor_popup)

        self.progress_bar = ttk.Progressbar(root, orient='horizontal', length=160)
        self.progress_bar.place(x=30, y=30)

        self.uploaded_file = tk.Text(root, height=2, width=100, bg="light yellow")
        self.code_smell_results = tk.Text(root, height=30, width=100, bg="light cyan")

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
            self.uploaded_file.insert(tk.END, "File Uploaded: " + self.file_path + "\n")

    def detect_smells(self):
        if not hasattr(self, 'file_path') or not self.file_path:
            messagebox.showerror("Error", "No file selected!")
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

    def refactor_popup(self):
        top = Toplevel(root)
        
        x_coordinate = int((top.winfo_screenwidth() - POPUP_WINDOW_WIDTH) / 2)
        y_coordinate = int((top.winfo_screenheight() - POPUP_WINDOW_HEIGHT) / 2)
        top.geometry(f"{POPUP_WINDOW_WIDTH}x{POPUP_WINDOW_HEIGHT}+{x_coordinate}+{y_coordinate}")
        
        top.title("Refacor Window")
        Label(top, text= "Do you want to refactor the Duplicated Code?", font=('Mistral 18 bold')).place(x=120,y=80)
        
        yes_button = tk.Button(top, text="Yes", command=self.refactor_duplicated_code)
        yes_button.place(x=POPUP_WINDOW_WIDTH / 2 - 100, y=150)

        # No Button
        no_button = tk.Button(top, text="No", command=top.destroy)
        no_button.place(x=POPUP_WINDOW_WIDTH / 2 + 20, y=150)

    def refactor_duplicated_code(self):
        # Your refactoring logic here
        pass
    
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

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Detect Long Function
                if len(node.body) > LONG_METHOD_TRESHOLD:
                    self.code_smell_results.insert(tk.END, f"\nLong Method/Function Detected\n Function: {node.name}, {len(node.body)} lines\n")
                
                # Detect Long Parameter List
                if len(node.args.args) > LONG_PARAMETER_TRESHOLD:
                    self.code_smell_results.insert(tk.END, f"\nLong Parameter List Detected\n Function: {node.name}, {len(node.args.args)} parameters\n")
                    
                function_code = ast.get_source_segment(code_content, node)
                functions[node.name] = function_code
                
        duplicates = self.detect_duplicate_functions(functions)

        # Print out detected duplicated functions
        if duplicates:
            self.refactor_button.pack()
            self.code_smell_results.insert(tk.END, "\nDuplicated Functions Detected:\n")
            for function1, function2, similarity in duplicates:
                self.code_smell_results.insert(tk.END, f"Functions: {function1} and {function2}, Similarity: {similarity}\n")


root = tk.Tk()
root.geometry("%dx%d" % (root.winfo_screenwidth(), root.winfo_screenheight()))
app = CodeSmellDetectorGUI(root)
root.mainloop()