import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re
import csv
import os

# Attempt to import PDF and DOCX extraction modules
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import docx2txt
except ImportError:
    docx2txt = None

##############################################################################
# Configuration
##############################################################################

# Soft color scheme
COLORS = {
    "primary": "#6d9eeb",      # Soft blue
    "secondary": "#e8f0fe",    # Very light blue
    "accent": "#a4c2f4",       # Medium-light blue
    "background": "#f5f7fa",   # Pale blue background
    "text": "#333333",         # Dark gray text
    "header_bg": "#a4c2f4",    # Header background
    "button_bg": "#6d9eeb",    # Button background
    "button_fg": "white",      # Button text
    "highlight": "#ffdf9e"     # Highlight color (soft yellow)
}

# Columns for our "table." Each tuple is (key_in_metadata, display_header).
COLUMNS = [
    ("year", "Year"),
    ("author_country", "Author/Country"),
    ("title", "Title"),
    ("journal", "Journal"),
    ("abstract", "Abstract"),
    ("methodology", "Methodology"),
    ("strengths_limitations", "Strengths/Limitations"),
    ("sample_size", "Sample Size"),
    ("key_findings", "Key Findings"),
    ("notes", "Notes"),
    ("remarks", "Remarks"),
    ("citation", "Citation"),
]

# How many pixels wide before text wraps in each column
# Adjust these as you like. If a column is still too wide, you can scroll horizontally.
COLUMN_WRAP_LENGTHS = {
    "year":                  60,
    "author_country":        120,
    "title":                 200,
    "journal":               200,
    "abstract":              300,
    "methodology":           300,
    "strengths_limitations": 300,
    "sample_size":           150,
    "key_findings":          300,
    "notes":                 300,
    "remarks":               300,
    "citation":              300
}

# Global list of metadata rows. Each row is a dict with keys matching COLUMNS.
data_rows = []

# Store the full text of each document alongside its metadata
document_texts = {}

##############################################################################
# File Extraction Logic
##############################################################################

def extract_text_from_file(filepath):
    """
    Extract all text from a file (PDF, DOCX, TXT, MD).
    Returns the raw text (string) or "" on error/unsupported.
    """
    ext = os.path.splitext(filepath)[1].lower()
    text = ""
    try:
        if ext in [".txt", ".md"]:
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
        elif ext == ".docx":
            if docx2txt is not None:
                text = docx2txt.process(filepath)
            else:
                messagebox.showerror("Dependency Error",
                    "docx2txt not installed.\nInstall via: pip install docx2txt")
        elif ext == ".pdf":
            if PyPDF2 is not None:
                with open(filepath, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            else:
                messagebox.showerror("Dependency Error",
                    "PyPDF2 not installed.\nInstall via: pip install PyPDF2")
        else:
            messagebox.showwarning("Unsupported File", f"Unsupported file type: {ext}")
    except Exception as e:
        messagebox.showerror("Error",
            f"Error processing {os.path.basename(filepath)}:\n{str(e)}")
    return text

def extract_yaml_metadata(text):
    """
    Look for a YAML block between --- and --- in the text.
    Parse lines of the form key: value.
    Returns a dict or None if no YAML was found.
    """
    pattern = re.compile(r'---(.*?)---', re.DOTALL)
    match = pattern.search(text)
    if not match:
        return None
    yaml_text = match.group(1).strip()
    metadata = {}
    for line in yaml_text.splitlines():
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower().replace(" ", "_")
            value = value.strip().strip('"\'')
            metadata[key] = value
    return metadata

##############################################################################
# GUI Logic
##############################################################################

def load_files():
    """Open file dialog, process each file, and update the table."""
    file_paths = filedialog.askopenfilenames(
        title="Select Files",
        filetypes=[
            ("Supported", "*.pdf *.docx *.txt *.md"),
            ("PDF Files", "*.pdf"),
            ("Word Documents", "*.docx"),
            ("Text/Markdown", "*.txt *.md")
        ]
    )
    if not file_paths:
        return

    global data_rows, document_texts
    data_rows = []
    document_texts = {}
    
    status_label.config(text="Loading files...")
    root.update()
    
    for path in file_paths:
        filename = os.path.basename(path)
        text = extract_text_from_file(path)
        if not text:
            continue
            
        # Store the full text for full-text searching later
        document_texts[filename] = text
        
        # Extract metadata
        meta = extract_yaml_metadata(text)
        if meta:
            # Add filename to metadata for reference
            meta['_filename'] = filename
            data_rows.append(meta)
        else:
            print(f"No YAML found in {filename}")
    
    status_label.config(text=f"Loaded {len(data_rows)} files with metadata")
    update_table(data_rows)

def on_metadata_search(*args):
    """When the metadata search box changes, re-filter and update the table."""
    filter_text = metadata_search_var.get().lower()
    
    if not filter_text:
        update_table(data_rows)
        return
        
    filtered = []
    for row in data_rows:
        combined = " ".join(str(row.get(k, "")) for k, _ in COLUMNS).lower()
        if filter_text in combined:
            filtered.append(row)
    
    status_label.config(text=f"Found {len(filtered)} matches in metadata")
    update_table(filtered)

def on_fulltext_search():
    """Search the full text of all loaded documents."""
    search_term = fulltext_search_var.get().lower()
    
    if not search_term:
        messagebox.showinfo("Search", "Please enter a search term")
        return
        
    status_label.config(text="Searching full text...")
    root.update()
    
    # Collect rows where the full text contains the search term
    filtered = []
    for row in data_rows:
        filename = row.get('_filename', '')
        if filename in document_texts:
            if search_term in document_texts[filename].lower():
                filtered.append(row)
    
    status_label.config(text=f"Found {len(filtered)} documents containing '{search_term}'")
    update_table(filtered)

def update_table(rows):
    """
    Clear existing table content in 'table_frame' and rebuild them for the given rows.
    We'll put headers in row=0, and each data row in row i+1, columns matching COLUMNS.
    """
    # Clear the table_frame first
    for widget in table_frame.winfo_children():
        widget.destroy()

    # Create header labels in row=0
    for col_idx, (key, header) in enumerate(COLUMNS):
        header_label = tk.Label(table_frame, text=header,
                                font=("Arial", 10, "bold"),
                                bg=COLORS["header_bg"],
                                fg=COLORS["text"],
                                borderwidth=1,
                                relief="solid")
        header_label.grid(row=0, column=col_idx, sticky="nsew", padx=1, pady=1)

    # Alternate row colors for better readability
    row_colors = [COLORS["secondary"], COLORS["background"]]
    
    # Create data rows
    for row_idx, row_data in enumerate(rows, start=1):
        row_bg = row_colors[row_idx % 2]
        
        for col_idx, (key, header) in enumerate(COLUMNS):
            cell_text = row_data.get(key, "")
            wrap_len = COLUMN_WRAP_LENGTHS.get(key, 200)

            cell_label = tk.Label(table_frame,
                                  text=cell_text,
                                  wraplength=wrap_len,
                                  justify="left",
                                  anchor="nw",
                                  bg=row_bg,
                                  fg=COLORS["text"],
                                  borderwidth=1,
                                  relief="solid")
            cell_label.grid(row=row_idx, column=col_idx,
                            sticky="nw", padx=1, pady=1)

    # Let each column expand to fit content
    for col_idx in range(len(COLUMNS)):
        table_frame.grid_columnconfigure(col_idx, weight=1)

    # Force the table_frame to update geometry, then reset scroll region
    table_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

def export_csv():
    """Export currently visible rows to CSV."""
    # Gather rows based on the current search filter
    visible_rows = []
    for widget in table_frame.winfo_children():
        if isinstance(widget, tk.Label) and widget.grid_info()["row"] > 0:
            row_idx = widget.grid_info()["row"]
            if row_idx <= len(data_rows) and col_idx == 0 and row_idx not in [r["row"] for r in visible_rows]:
                visible_rows.append({"row": row_idx, "data": data_rows[row_idx-1]})
    
    if not visible_rows:
        messagebox.showinfo("Export CSV", "No data to export")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv")]
    )
    if not file_path:
        return

    try:
        with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            # Write header
            writer.writerow([header for _, header in COLUMNS])
            # Write rows
            for row_info in visible_rows:
                writer.writerow([row_info["data"].get(k, "") for k, _ in COLUMNS])
        messagebox.showinfo("Export CSV", "CSV exported successfully")
    except Exception as e:
        messagebox.showerror("Export Error", str(e))

##############################################################################
# Main GUI
##############################################################################

root = tk.Tk()
root.title("Literature Review Manager")
root.configure(bg=COLORS["background"])

# Configure a custom style
style = ttk.Style()
style.configure("TButton", 
                font=("Arial", 10),
                padding=5)
style.map("TButton",
          background=[("active", COLORS["accent"])])
          
style.configure("TEntry", 
                fieldbackground="white",
                font=("Arial", 10))

# Title frame with application name
title_frame = tk.Frame(root, bg=COLORS["primary"], padx=10, pady=5)
title_frame.pack(fill="x")

title_label = tk.Label(title_frame, 
                      text="Literature Review Manager",
                      font=("Arial", 16, "bold"),
                      bg=COLORS["primary"],
                      fg="white")
title_label.pack(pady=5)

# Top controls (Load, Search, Export)
control_frame = tk.Frame(root, bg=COLORS["background"], padx=10, pady=10)
control_frame.pack(fill="x")

# File controls
file_frame = tk.Frame(control_frame, bg=COLORS["background"], pady=5)
file_frame.pack(fill="x")

load_btn = tk.Button(file_frame, text="Choose Files", command=load_files, 
                    bg=COLORS["button_bg"], fg=COLORS["button_fg"],
                    font=("Arial", 10), padx=10, pady=5, relief="raised")
load_btn.pack(side="left", padx=5)

export_btn = tk.Button(file_frame, text="Export CSV", command=export_csv,
                      bg=COLORS["button_bg"], fg=COLORS["button_fg"],
                      font=("Arial", 10), padx=10, pady=5, relief="raised")
export_btn.pack(side="left", padx=5)

# Status label
status_label = tk.Label(file_frame, text="Ready", bg=COLORS["background"], fg=COLORS["text"])
status_label.pack(side="right", padx=10)

# Search frames
search_frame = tk.Frame(control_frame, bg=COLORS["background"], pady=10)
search_frame.pack(fill="x")

# Metadata search
metadata_search_frame = tk.Frame(search_frame, bg=COLORS["background"])
metadata_search_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))

tk.Label(metadata_search_frame, text="Filter Metadata:", bg=COLORS["background"], fg=COLORS["text"],
         font=("Arial", 10)).pack(side="left")
metadata_search_var = tk.StringVar()
metadata_search_var.trace_add("write", on_metadata_search)
metadata_search_entry = tk.Entry(metadata_search_frame, textvariable=metadata_search_var, 
                               width=30, font=("Arial", 10))
metadata_search_entry.pack(side="left", padx=5, fill="x", expand=True)

# Full-text search
fulltext_search_frame = tk.Frame(search_frame, bg=COLORS["background"])
fulltext_search_frame.pack(side="left", fill="x", expand=True, padx=(5, 0))

tk.Label(fulltext_search_frame, text="Full-Text Search:", bg=COLORS["background"], fg=COLORS["text"],
         font=("Arial", 10)).pack(side="left")
fulltext_search_var = tk.StringVar()
fulltext_search_entry = tk.Entry(fulltext_search_frame, textvariable=fulltext_search_var, 
                               width=30, font=("Arial", 10))
fulltext_search_entry.pack(side="left", padx=5, fill="x", expand=True)

fulltext_search_btn = tk.Button(fulltext_search_frame, text="Search Content", 
                              command=on_fulltext_search,
                              bg=COLORS["button_bg"], fg=COLORS["button_fg"],
                              font=("Arial", 10), padx=10, pady=5, relief="raised")
fulltext_search_btn.pack(side="left")

##############################################################################
# Scrollable "Table" region
##############################################################################

main_frame = tk.Frame(root, bg=COLORS["background"], padx=10, pady=10)
main_frame.pack(fill="both", expand=True)

# Canvas for the table
canvas = tk.Canvas(main_frame, bg=COLORS["background"], highlightthickness=0)
canvas.grid(row=0, column=0, sticky="nsew")

# Scrollbars
x_scrollbar = tk.Scrollbar(main_frame, orient="horizontal", command=canvas.xview)
y_scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)

x_scrollbar.grid(row=1, column=0, sticky="ew")
y_scrollbar.grid(row=0, column=1, sticky="ns")

canvas.configure(xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)

# A frame inside the canvas, which will contain the entire "table"
table_frame = tk.Frame(canvas, bg=COLORS["background"])
canvas.create_window((0, 0), window=table_frame, anchor="nw")

# Make the main_frame expandable
main_frame.rowconfigure(0, weight=1)
main_frame.columnconfigure(0, weight=1)

# Add some padding around the main window
root.geometry("1200x800")  # Set a reasonable starting size

# Add some responsive behavior
def on_resize(event):
    canvas.config(width=event.width-20, height=event.height-20)
    
main_frame.bind("<Configure>", on_resize)

root.mainloop()
