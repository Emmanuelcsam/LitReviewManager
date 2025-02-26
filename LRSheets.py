import os
import pandas as pd
import pdfplumber
import yaml
import markdown
from docx import Document
from flask import Flask, request, render_template, send_file

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Allowed extensions
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "md"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip()

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

def extract_text_from_md(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return markdown.markdown(file.read())

def parse_yaml_metadata(text):
    yaml_data = {}
    if "---" in text:
        try:
            yaml_content = text.split("---")[1]
            yaml_data = yaml.safe_load(yaml_content)
        except yaml.YAMLError:
            pass
    return yaml_data

def process_file(file_path, file_ext):
    if file_ext == "pdf":
        text = extract_text_from_pdf(file_path)
    elif file_ext == "docx":
        text = extract_text_from_docx(file_path)
    elif file_ext == "txt":
        text = extract_text_from_txt(file_path)
    elif file_ext == "md":
        text = extract_text_from_md(file_path)
    else:
        return None
    
    metadata = parse_yaml_metadata(text)
    return metadata

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        files = request.files.getlist("file")
        data = []

        for file in files:
            if file and allowed_file(file.filename):
                file_ext = file.filename.rsplit(".", 1)[1].lower()
                file_path = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(file_path)
                
                metadata = process_file(file_path, file_ext)
                if metadata:
                    data.append(metadata)

        if data:
            df = pd.DataFrame(data)
            excel_path = os.path.join(UPLOAD_FOLDER, "literature_reviews.xlsx")
            df.to_excel(excel_path, index=False)
            return send_file(excel_path, as_attachment=True)
    
    return render_template("upload.html")

if __name__ == "__main__":
    app.run(debug=True)

# HTML Template (upload.html)
UPLOAD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upload Literature Reviews</title>
</head>
<body>
    <h2>Upload Literature Review Files</h2>
    <form action="/" method="post" enctype="multipart/form-data">
        <input type="file" name="file" multiple>
        <button type="submit">Upload</button>
    </form>
</body>
</html>
"""

@app.route("/upload.html")
def upload_page():
    return UPLOAD_HTML
