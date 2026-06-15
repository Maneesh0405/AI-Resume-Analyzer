# AI Resume Analyzer

An intelligent, NLP-powered Resume Analyzer built with Python and Flask. This application helps job seekers and recruiters evaluate resumes against specific job descriptions to generate an ATS (Applicant Tracking System) score. It highlights matching keywords and identifies missing ones to help optimize the resume for better selection chances.

## Features

- **PDF Text Extraction:** Extracts text seamlessly from uploaded PDF resumes.
- **Natural Language Processing (NLP):** Uses `spaCy` for advanced text preprocessing, lemmatization, and keyword extraction.
- **Machine Learning Analysis:** Utilizes `scikit-learn` (TF-IDF and Cosine Similarity) to calculate the relevance of the resume to the selected job role.
- **Detailed Scoring System:** Calculates a composite score based on:
  - 60% Cosine Similarity (Contextual match)
  - 40% Keyword Match (Exact skill match)
- **Actionable Feedback:** Provides a list of found keywords and top missing keywords for resume improvement.
- **Predefined Job Roles:** Supports various job roles including Software Engineer, Data Scientist, Frontend Developer, Backend Developer, DevOps Engineer, Machine Learning Engineer, and more.

## Tech Stack

- **Backend:** Python, Flask, Flask-CORS
- **Machine Learning & NLP:** spaCy, scikit-learn (TfidfVectorizer, cosine_similarity)
- **PDF Processing:** PyPDF2
- **Frontend:** HTML, CSS, JavaScript (via Flask templates)

## Installation and Setup

Follow these steps to run the project locally.

### 1. Clone the repository

```bash
git clone <repository-url>
cd AI-Resume-Analyzer
```

### 2. Set up a Virtual Environment (Optional but recommended)

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

*Note: The `requirements.txt` file also includes the necessary `spaCy` English language model (`en_core_web_sm`).*

### 4. Run the Application

```bash
python app.py
```

The application will start running on `http://127.0.0.1:5000/`.

## How to Use

1. Open your web browser and go to `http://127.0.0.1:5000/`.
2. Upload your resume in **PDF format**.
3. Enter or select the **Job Role** you are applying for (e.g., `software_engineer`, `data_scientist`, `frontend_developer`).
4. Click on **Analyze**.
5. The system will process your resume and display:
   - Your ATS Score
   - Status (Selected/Not Selected based on a 60% threshold)
   - Cosine Similarity & Keyword Match Percentages
   - Keywords found in your resume
   - Keywords missing from your resume

## Project Structure

```text
AI-Resume-Analyzer/
│
├── analyzer.py          # Core ML/NLP logic for extracting text, preprocessing, and calculating ATS score
├── app.py               # Flask application and API routing
├── requirements.txt     # Python dependencies
├── static/              # Static files (CSS, JS, Images)
├── templates/           # HTML templates (index.html)
└── uploads/             # Temporary folder for PDF uploads (handled dynamically)
```

## Future Enhancements

- Allow custom Job Description input instead of only predefined roles.
- Enhance the UI/UX with modern web frameworks.
- Add support for `.docx` files.
- Provide detailed paragraph-level feedback on the resume.

## License

This project is open-source and available under the [MIT License](LICENSE).
