import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
import os
import pyarrow.parquet as pq
import json


class ParquetEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Parquet Metadata Editor")
        self.root.geometry("700x500")
        self.root.configure(bg="#f5f5f5")

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook.Tab", font=("Segoe UI", 11, "bold"), padding=[10, 5])
        style.configure("TButton", font=("Segoe UI", 10), padding=6)

        self.main_container = tk.Frame(self.root, bg="white")
        self.main_container.pack(fill="both", expand=True)

        self.current_metadata = {}
        self.notebook = None
        self.tab_widgets = {}

        self.show_home_screen()

    def show_home_screen(self):
        self.clear_main_container()
        home_frame = tk.Frame(self.main_container, bg="white")
        home_frame.pack(fill="both", expand=True)

        title = tk.Label(home_frame, text="Welcome to Parquet Metadata Editor", font=("Segoe UI", 16, "bold"), bg="white", fg="#333")
        title.pack(pady=(30, 40))

        select_button = ttk.Button(home_frame, text="Select Parquet", command=self.select_parquet_file)
        select_button.pack(pady=10, ipadx=10, ipady=4)

        help_button = ttk.Button(home_frame, text="Help & Support", command=self.show_help_screen)
        help_button.pack(pady=10)

    def show_help_screen(self):
        self.clear_main_container()
        help_frame = tk.Frame(self.main_container, bg="white")
        help_frame.pack(fill="both", expand=True)

        help_title = tk.Label(help_frame, text="Help & Support", font=("Segoe UI", 14, "bold"), bg="white")
        help_title.pack(anchor="w", pady=(20, 10), padx=30)

        help_text = (
            "\n- Edit or add metadata keys and values directly.\n"
            "- Metadata is stored in the Parquet file footer.\n"
            "- Use the '+' tab to add new metadata keys.\n"
        )

        help_label = tk.Label(help_frame, text=help_text, font=("Segoe UI", 10), justify="left", wraplength=540, bg="white", fg="#444")
        help_label.pack(anchor="w", padx=30)

        back_button = ttk.Button(help_frame, text="Back", command=self.show_home_screen)
        back_button.pack(pady=20)

    def select_parquet_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Parquet Files", "*.parquet")])
        if file_path:
            self.load_metadata_editor(file_path)

    def load_metadata_editor(self, file_path):
        self.clear_main_container()
        self.tab_widgets = {}

        try:
            table = pq.read_table(file_path)
            metadata = table.schema.metadata or {}
            self.current_metadata = {k.decode(): v.decode() for k, v in metadata.items()}
        except Exception as e:
            self.current_metadata = {}
            print("Error loading metadata:", e)

        editor_frame = tk.Frame(self.main_container, bg="white")
        editor_frame.pack(fill="both", expand=True)

        save_btn = ttk.Button(editor_frame, text="Save Metadata", command=lambda: self.save_metadata(file_path))
        save_btn.pack(pady=10, padx=10, anchor="ne")

        self.notebook = ttk.Notebook(editor_frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        for key, value in self.current_metadata.items():
            self.add_metadata_tab(key, value)

        self.add_plus_tab()

    def add_metadata_tab(self, key, value):
        frame = tk.Frame(self.notebook, bg="white")
        text = tk.Text(frame, wrap="word")
        text.insert("1.0", value)
        text.pack(expand=True, fill="both", padx=10, pady=10)
        self.notebook.add(frame, text=key)
        self.tab_widgets[key] = text

    def add_plus_tab(self):
        frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(frame, text="+")
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def on_tab_changed(self, event):
        current = self.notebook.index("current")
        if self.notebook.tab(current, "text") == "+":
            key = simpledialog.askstring("New Metadata Key", "Enter metadata key:")
            if key and key not in self.tab_widgets:
                self.notebook.forget(current)
                self.add_metadata_tab(key, "")
                self.add_plus_tab()
                self.notebook.select(len(self.notebook.tabs()) - 2)

    def save_metadata(self, file_path):
        new_metadata = {}
        for key, text_widget in self.tab_widgets.items():
            value = text_widget.get("1.0", "end").strip()
            new_metadata[key] = value

        try:
            table = pq.read_table(file_path)
            metadata_bytes = {k.encode(): v.encode() for k, v in new_metadata.items()}
            new_schema = table.schema.with_metadata(metadata_bytes)
            table = table.cast(new_schema)  # update the table's schema

            pq.write_table(table, file_path)  # no need to pass `schema=...` again
            print("Metadata saved successfully!")
        except Exception as e:
            print("Error saving metadata:", e)


    def clear_main_container(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ParquetEditorApp(root)
    root.mainloop()
