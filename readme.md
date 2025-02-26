# Literature Review Manager

A comprehensive tool for managing academic literature reviews with metadata extraction and organization capabilities.

## Overview

The Literature Review Manager helps researchers organize and analyze academic papers by extracting structured metadata from files with YAML frontmatter. It creates searchable tables of literature reviews and supports exporting to CSV format.

This repository contains multiple implementations of the Literature Review Manager:

1. **Web-based HTML/JavaScript versions**:
   - `collectreviewsall.html`: Full-featured web version with support for TXT, MD, and DOCX files
   - `CollectReviewsmd.html`: Simplified version supporting only TXT/MD files

2. **Python implementations**:
   - `LRSheets.py`: Flask-based web application with Excel export capability
   - `LRSheets2.py`: Desktop GUI application using Tkinter for a standalone experience

## Features

- Extract metadata from literature review files with YAML frontmatter
- Support for multiple file formats (TXT, MD, DOCX, PDF*)
- Search functionality for both metadata and full-text content
- Interactive table view of review metadata
- Export capabilities to CSV/Excel formats
- Responsive interfaces in both web and desktop versions

*PDF support varies by implementation

## Getting Started

### Prerequisites

- Python 3.6 or higher (for Python implementations)
- Modern web browser (for HTML versions)
- Dependencies as listed in the setup script

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/literature-review-manager.git
   cd literature-review-manager
   ```

2. Run the setup script:
   ```
   # For Linux/Mac
   chmod +x setup.sh
   ./setup.sh
   
   # For Windows
   setup.bat
   ```

### Running the Application

#### Web Versions (HTML/JavaScript)

Simply open any of the HTML files in a web browser:

```
# Open directly from file explorer or:
open collectreviewsall.html
# OR
open CollectReviewsmd.html
```

#### Python Flask Web App

```
# Activate the virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the Flask application
python LRSheets.py
```

Then navigate to `http://127.0.0.1:5000` in your web browser.

#### Python Tkinter Desktop App

```
# Activate the virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the Tkinter application
python LRSheets2.py
```

## Usage Guide

### Creating Literature Review Files

1. Use the provided template (`lit-review-template.md`) as a starting point
2. Fill in the YAML frontmatter between the `---` markers
3. Save your file with a `.md`, `.txt`, or `.docx` extension

Example YAML frontmatter:

```yaml
---
year: 2024
author_country: "Smith et al. / United States"
title: "Advances in Machine Learning Applications for Literature Review Automation"
journal: "Journal of Information Science"
abstract: "This paper explores recent developments in using machine learning to automate aspects of the literature review process..."
methodology: "Systematic review of 45 papers published between 2018-2024"
strengths_limitations: "Strong coverage of ML techniques; Limited discussion of implementation challenges"
sample_size: "45 papers"
key_findings: "Key finding 1... Key finding 2..."
notes: "Important to follow up on references 23 and 24"
remarks: "Consider extending this analysis to include NLP approaches"
citation: "Smith, J., Jones, A., & Brown, T. (2024). Advances in Machine Learning Applications for Literature Review Automation. Journal of Information Science, 50(2), 123-145."
---
```

### Using the Web Interface

1. Open one of the HTML files in your web browser
2. Click "Choose Files" to select your literature review files
3. The metadata will be extracted and displayed in a searchable table
4. Use the search box to filter the table
5. Click "Export CSV" to download your data

### Using the Python Applications

The Python implementations offer additional features:

- `LRSheets.py` (Flask web app):
  - Upload multiple files through the web interface
  - Export to Excel format

- `LRSheets2.py` (Tkinter desktop app):
  - More sophisticated searching (metadata and full-text)
  - Enhanced visual display with color coding
  - Direct file system access

## Implementation Details

### File Structure

```
literature-review-manager/
├── collectreviewsall.html     # Full-featured web version
├── CollectReviewsmd.html      # Simplified web version
├── lit-review-template.md     # Template for creating new reviews
├── LRSheets.py                # Flask web application
├── LRSheets2.py               # Tkinter desktop application
├── setup.sh                   # Linux/Mac setup script
├── setup.bat                  # Windows setup script
└── README.md                  # This documentation
```

### Metadata Fields

The following metadata fields are extracted and displayed:

| Field                | Description                                    |
|----------------------|------------------------------------------------|
| Year                 | Publication year                               |
| Author/Country       | Author names and country of origin             |
| Title                | Full publication title                         |
| Journal              | Journal or publication name                    |
| Abstract             | Summary of the paper                           |
| Methodology          | Research approach and methods                  |
| Strengths/Limitations| Notable strengths and weaknesses               |
| Sample Size          | Number of participants or data points          |
| Key Findings         | Main results and conclusions                   |
| Notes                | Additional observations                        |
| Remarks              | Critical evaluation and implications           |
| Citation             | Formatted citation                             |

## Technical Details

### Web Versions

- Pure HTML, CSS, and JavaScript
- Uses JSZip and DocXTemplater libraries for DOCX processing
- Mammoth.js for DOCX-to-text conversion

### Python Implementations

- Flask for web framework (LRSheets.py)
- Tkinter for desktop GUI (LRSheets2.py)
- Libraries: pdfplumber, pandas, PyYAML, python-docx

## Troubleshooting

### Common Issues

1. **PDF extraction issues**:
   - Ensure Poppler is installed for PDF support:
     ```
     # Ubuntu/Debian
     sudo apt-get install poppler-utils
     
     # macOS
     brew install poppler
     
     # Windows
     # See pdfplumber documentation
     ```

2. **DOCX parsing problems**:
   - Ensure python-docx or docx2txt is installed
   - YAML must be properly formatted within the DOCX file

3. **Python dependency issues**:
   - Run the setup script again or manually install missing packages:
     ```
     pip install pandas pdfplumber PyYAML markdown python-docx flask openpyxl
     ```

## Contributing

Contributions to improve the Literature Review Manager are welcome. Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Contributors and maintainers of the libraries used in this project
- Academic researchers who provided feedback during development
