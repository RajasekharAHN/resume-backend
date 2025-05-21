"""
Flask backend for Resume Analyzer API with file extension preservation
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
from os import environ
from werkzeug.utils import secure_filename

from resume_parser import parse_document
from skill_matcher import SkillMatcher

app = Flask(__name__)
CORS(app)

skill_matcher = SkillMatcher()

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'resume' not in request.files or 'job_description' not in request.files:
        return jsonify({'error': 'Both resume and job description files are required'}), 400

    resume_file = request.files['resume']
    job_desc_file = request.files['job_description']

    if resume_file.filename == '' or job_desc_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Preserve file extensions
    resume_ext = os.path.splitext(resume_file.filename)[1]
    job_desc_ext = os.path.splitext(job_desc_file.filename)[1]

    with tempfile.NamedTemporaryFile(delete=False, suffix=resume_ext) as temp_resume:
        resume_path = temp_resume.name
        resume_file.save(resume_path)

    with tempfile.NamedTemporaryFile(delete=False, suffix=job_desc_ext) as temp_job:
        job_desc_path = temp_job.name
        job_desc_file.save(job_desc_path)

    try:
        print("Parsing resume from:", resume_path)
        resume_text = parse_document(resume_path)
        print("Resume text preview:", resume_text[:500])

        print("Parsing job description from:", job_desc_path)
        job_desc_text = parse_document(job_desc_path)
        print("Job description text preview:", job_desc_text[:500])

        if not resume_text or not job_desc_text:
            return jsonify({'error': 'Failed to parse one or both documents'}), 400

        results = skill_matcher.analyze(resume_text, job_desc_text)

        os.unlink(resume_path)
        os.unlink(job_desc_path)

        return jsonify(results)

    except Exception as e:
        if os.path.exists(resume_path):
            os.unlink(resume_path)
        if os.path.exists(job_desc_path):
            os.unlink(job_desc_path)
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(environ.get("PORT", 5000)))