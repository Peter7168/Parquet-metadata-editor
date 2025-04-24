import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from parquet_metadata_editor import (
    load_parquet_metadata,
    save_parquet_with_metadata,
    update_metadata_value,
    add_new_metadata_key,
)

class MetadataEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Parquet Metadata Editor")
        self.root.geometry("800x600")
        self.metadata = {}
        self.metadata_widgets = {}
        self.current_tab = None
        self.table = None
        self.file_path = ""

        self.build_ui()

    def build_ui(self):
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill="both", expand=True)

        self.tab_bar_canvas = tk.Canvas(self.frame, height=40)
        self.tab_frame = tk.Frame(self.tab_bar_canvas)
        self.tab_scroll = ttk.Scrollbar(self.frame, orient="horizontal", command=self.tab_bar_canvas.xview)
        self.tab_bar_canvas.configure(xscrollcommand=self.tab_scroll.set)

        self.tab_bar_window = self.tab_bar_canvas.create_window((0, 0), window=self.tab_frame, anchor="nw")
        self.tab_frame.bind("<Configure>", lambda e: self.tab_bar_canvas.configure(scrollregion=self.tab_bar_canvas.bbox("all")))

        self.tab_bar_canvas.pack(fill="x", side="top")
        self.tab_scroll.pack(fill="x", side="top")

        self.text_editor = tk.Text(self.frame, font=("Courier", 12))
        self.text_editor.pack(fill="both", expand=True, padx=10, pady=10)

        self.bottom_bar = tk.Frame(self.frame)
        self.bottom_bar.pack(fill="x")

        tk.Button(self.bottom_bar, text="Open Parquet", command=self.open_file).pack(side="left", padx=5)
        tk.Button(self.bottom_bar, text="Save", command=self.save_file).pack(side="left", padx=5)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Parquet Files", "*.parquet")])
        if file_path:
            self.file_path = file_path
            self.metadata, self.table = load_parquet_metadata(file_path)
            self.render_tabs()

    def render_tabs(self):
        for widget in self.tab_frame.winfo_children():
            widget.destroy()

        self.metadata_widgets.clear()

        for key in self.metadata:
            self.create_tab(key)

        self.create_add_tab()
        self.switch_tab(next(iter(self.metadata), None))  #select the first tab

    def create_tab(self, key):
        btn = ttk.Button(self.tab_frame, text=key, command=lambda k=key: self.switch_tab(k))
        btn.pack(side="left", padx=2, pady=5)
        self.metadata_widgets[key] = btn

    def create_add_tab(self):
        btn = ttk.Button(self.tab_frame, text="+", width=3, command=self.add_tab)
        btn.pack(side="left", padx=2, pady=5)

    def switch_tab(self, key):
        if self.current_tab:
            # Save content of current tab before switching
            current_value = self.text_editor.get("1.0", tk.END).strip()
            update_metadata_value(self.metadata, self.current_tab, current_value)

        self.current_tab = key
        self.text_editor.delete("1.0", tk.END)
        if key:
            self.text_editor.insert("1.0", self.metadata.get(key, ""))

    def add_tab(self):
        new_key = self.prompt_for_key()
        if new_key:
            if new_key in self.metadata:
                messagebox.showerror("Error", "This key already exists.")
                return
            add_new_metadata_key(self.metadata, new_key)
            self.create_tab(new_key)
            self.create_add_tab()  # refresh the "+" at the end
            self.switch_tab(new_key)

    def prompt_for_key(self):
        popup = tk.Toplevel(self.root)
        popup.title("New Metadata Key")
        popup.grab_set()
        tk.Label(popup, text="Enter metadata key:").pack(padx=10, pady=10)
        entry = tk.Entry(popup)
        entry.pack(padx=10)
        entry.focus()

        def submit():
            popup.key = entry.get().strip()
            popup.destroy()

        tk.Button(popup, text="Add", command=submit).pack(pady=10)
        self.root.wait_window(popup)
        return getattr(popup, "key", None)

    def save_file(self):
        if self.current_tab:
            current_value = self.text_editor.get("1.0", tk.END).strip()
            update_metadata_value(self.metadata, self.current_tab, current_value)
        try:
            save_parquet_with_metadata(self.file_path, self.metadata, self.table)
            messagebox.showinfo("Saved", "Metadata saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = MetadataEditorApp(root)
    root.mainloop()
