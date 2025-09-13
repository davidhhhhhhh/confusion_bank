from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'confusion-bank-secret-key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def home():
    """Landing page with course upload"""
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_syllabus():
    """Handle PDF syllabus upload and processing"""
    # TODO: Implement PDF upload and processing
    return jsonify({'status': 'success', 'message': 'Upload functionality coming soon'})

@app.route('/chat')
def chat_interface():
    """Chat interface page"""
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """API endpoint for chat messages"""
    # TODO: Implement chat API
    return jsonify({'response': 'Chat functionality coming soon'})

@app.route('/review')
def review_mode():
    """Review mode selection page"""
    return render_template('review.html')

@app.route('/api/review/<int:course_id>/<topic>')
def api_review(course_id, topic):
    """Generate and return review content"""
    # TODO: Implement review generation
    return jsonify({'questions': ['Review functionality coming soon']})

if __name__ == '__main__':
    app.run(debug=True, port=5000)