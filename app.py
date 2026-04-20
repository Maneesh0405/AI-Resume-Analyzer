import os
import tempfile
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from analyzer import extract_text_from_pdf, calculate_ats_score
import uuid

# Lock the base directory strictly to where this script lives
basedir = os.path.abspath(os.path.dirname(__file__))

# Initialize Flask with explicit static and template paths
app = Flask(__name__, 
            static_folder=os.path.join(basedir, 'static'),
            template_folder=os.path.join(basedir, 'templates'))

CORS(app)

# Ensure uploads folder exists in a writable /tmp directory
UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB max size

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_resume():
    if 'resume' not in request.files:
        return jsonify({"error": "No resume file provided"}), 400
        
    file = request.files['resume']
    job_role = request.form.get('job_role')
    
    if file.filename == '':
        return jsonify({"error": "No file selected for uploading"}), 400
        
    if not file.filename.endswith('.pdf'):
        return jsonify({"error": "Only PDF files are supported"}), 400
        
    if not job_role:
        return jsonify({"error": "Job role not provided"}), 400

    try:
        # Save file to process
        filename = f"{uuid.uuid4().hex}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract text
        resume_text = extract_text_from_pdf(filepath)
        
        # Cleanup file after extracting text
        if os.path.exists(filepath):
            os.remove(filepath)
            
        if not resume_text:
            return jsonify({"error": "Failed to extract text from PDF or PDF is empty."}), 400

        # Run AI analyzer
        analysis_result = calculate_ats_score(resume_text, job_role)
        
        if "error" in analysis_result:
            return jsonify({"error": analysis_result["error"]}), 400
            
        return jsonify(analysis_result)

    except Exception as e:
         return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
