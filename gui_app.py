import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os

try:
    import docx
except ImportError:
    docx = None

# Try to import windnd for drag-and-drop
try:
    import windnd
    HAS_DND = True
except ImportError:
    HAS_DND = False

from genius_humanizer import GeniusHumanizer


class HumanizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Genius Text Humanizer v3.0")
        self.root.geometry("1000x680")
        self.root.configure(bg="#1a1a2e")
        self.root.minsize(800, 500)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#1a1a2e")
        style.configure("TLabelframe", background="#16213e", foreground="#e94560")
        style.configure("TLabelframe.Label", background="#16213e", foreground="#e94560",
                         font=('Segoe UI', 10, 'bold'))
        style.configure("TButton", background="#e94560", foreground="white",
                         font=('Segoe UI', 9, 'bold'), padding=6)
        style.map("TButton", background=[('active', '#c73e54')])
        style.configure("TLabel", background="#1a1a2e", foreground="#eee", font=('Segoe UI', 10))
        style.configure("Horizontal.TProgressbar", troughcolor="#16213e", background="#0f3460")

        self.humanizer = None
        self.is_processing = False

        self.create_widgets()
        self.setup_drag_and_drop()

        self.status_var.set("Loading AI Model...")
        threading.Thread(target=self.init_model, daemon=True).start()

    def create_widgets(self):
        main = ttk.Frame(self.root, padding="10")
        main.pack(fill=tk.BOTH, expand=True)

        # Top bar
        top = ttk.Frame(main)
        top.pack(fill=tk.X, pady=(0, 8))

        ttk.Button(top, text="Open File (.txt .docx .md)", command=self.load_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="Clear", command=self.clear_text).pack(side=tk.LEFT, padx=5)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(top, textvariable=self.status_var, font=('Segoe UI', 10, 'bold')).pack(side=tk.RIGHT, padx=5)

        # Progress bar
        self.progress = ttk.Progressbar(main, orient=tk.HORIZONTAL, mode='determinate')
        self.progress.pack(fill=tk.X, pady=(0, 8))

        # Paned window
        paned = ttk.PanedWindow(main, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Input frame
        input_frame = ttk.LabelFrame(paned, text="Input - Paste or Drag File Here")
        paned.add(input_frame, weight=1)

        self.input_text = tk.Text(input_frame, wrap=tk.WORD, font=('Consolas', 11),
                                   bg="#0f3460", fg="#e0e0e0", insertbackground="white",
                                   selectbackground="#e94560", relief=tk.FLAT, padx=8, pady=8)
        self.input_text.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)

        # Output frame - READ ONLY
        output_frame = ttk.LabelFrame(paned, text="Humanized Result (Read-Only)")
        paned.add(output_frame, weight=1)

        self.output_text = tk.Text(output_frame, wrap=tk.WORD, font=('Consolas', 11),
                                    bg="#0f3460", fg="#a8e6cf", insertbackground="white",
                                    selectbackground="#e94560", relief=tk.FLAT, padx=8, pady=8,
                                    state=tk.DISABLED)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)

        # Bottom bar
        bottom = ttk.Frame(main)
        bottom.pack(fill=tk.X, pady=(8, 0))

        self.process_btn = ttk.Button(bottom, text="Humanize Text", command=self.start_processing)
        self.process_btn.pack(side=tk.RIGHT, padx=5)

        ttk.Button(bottom, text="Copy Result", command=self.copy_result).pack(side=tk.RIGHT, padx=5)
        ttk.Button(bottom, text="Save Result", command=self.save_result).pack(side=tk.RIGHT, padx=5)

    def setup_drag_and_drop(self):
        """Setup drag-and-drop file support."""
        if HAS_DND:
            windnd.hook_dropfiles(self.root, func=self.on_file_drop)
            self.input_text.insert(tk.END, "\n\n     Drag & drop a file here, or paste text, or click 'Open File'\n")
        else:
            self.input_text.insert(tk.END,
                "\n\n     Paste text here or click 'Open File'\n"
                "     (Install 'windnd' for drag-and-drop: pip install windnd)\n")

    def on_file_drop(self, files):
        """Handle file drop."""
        if self.is_processing:
            return
        if files:
            filepath = files[0]
            if isinstance(filepath, bytes):
                filepath = filepath.decode('utf-8')
            self._load_file_content(filepath)

    def init_model(self):
        try:
            self.humanizer = GeniusHumanizer()
            self.status_var.set("AI Model Ready")
        except Exception as e:
            self.status_var.set("Error Loading Model")
            messagebox.showerror("Error", f"Failed to load AI Model:\n{e}")

    def load_file(self):
        if self.is_processing:
            return
        filetypes = [("All Supported", "*.txt *.docx *.md"), ("Text Files", "*.txt"),
                     ("Markdown", "*.md"), ("Word", "*.docx")]
        filepath = filedialog.askopenfilename(filetypes=filetypes)
        if filepath:
            self._load_file_content(filepath)

    def _load_file_content(self, filepath):
        try:
            if filepath.lower().endswith('.docx'):
                if docx is None:
                    messagebox.showerror("Error", "Install python-docx: pip install python-docx")
                    return
                doc = docx.Document(filepath)
                content = "\n".join([p.text for p in doc.paragraphs])
            else:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

            self.input_text.delete(1.0, tk.END)
            self.input_text.insert(tk.END, content)
            self.status_var.set(f"Loaded: {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file:\n{e}")

    def clear_text(self):
        self.input_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.progress['value'] = 0
        self.status_var.set("Ready")

    def copy_result(self):
        result = self.output_text.get(1.0, tk.END).strip()
        if result:
            self.root.clipboard_clear()
            self.root.clipboard_append(result)
            self.status_var.set("Copied to Clipboard!")

    def save_result(self):
        result = self.output_text.get(1.0, tk.END).strip()
        if not result:
            messagebox.showwarning("Warning", "No result to save.")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".txt",
                                                  filetypes=[("Text Files", "*.txt")])
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(result)
            self.status_var.set(f"Saved: {os.path.basename(filepath)}")

    def start_processing(self):
        if self.humanizer is None:
            messagebox.showwarning("Warning", "AI Model is still loading.")
            return
        if self.is_processing:
            return
        text = self.input_text.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter text or open a file first.")
            return

        self.is_processing = True
        self.process_btn.config(state=tk.DISABLED)
        self.status_var.set("Processing... Please wait")
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.progress['value'] = 0

        threading.Thread(target=self.process_text, args=(text,), daemon=True).start()

    def update_progress(self, value):
        self.root.after(0, lambda: self.progress.configure(value=value))

    def process_text(self, text):
        try:
            result = self.humanizer.humanize(text, progress_callback=self.update_progress)
            self.root.after(0, self.show_result, result)
        except Exception as e:
            self.root.after(0, self.show_error, str(e))

    def show_result(self, result):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, result)
        self.output_text.config(state=tk.DISABLED)
        self.progress['value'] = 100
        self.status_var.set("Done! Text humanized.")
        self.is_processing = False
        self.process_btn.config(state=tk.NORMAL)

    def show_error(self, msg):
        self.status_var.set("Error")
        messagebox.showerror("Error", msg)
        self.is_processing = False
        self.process_btn.config(state=tk.NORMAL)


if __name__ == "__main__":
    root = tk.Tk()
    app = HumanizerApp(root)
    root.mainloop()
