from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
from pdf_processor import process_syllabus_upload
from llm_service import chat_with_claude
from database import save_conversation, get_courses
from classifier import update_session_activity, force_analyze_session, run_periodic_analysis
from review_generator import generate_review_by_criteria, generate_review_from_request, get_available_review_topics

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
    try:
        # Check if the request has the file part
        if 'syllabus-file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file uploaded'})

        file = request.files['syllabus-file']
        course_name = request.form.get('course-name', '').strip()

        # Validate inputs
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No file selected'})

        if not course_name:
            return jsonify({'status': 'error', 'message': 'Course name is required'})

        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'status': 'error', 'message': 'Only PDF files are allowed'})

        # Process the PDF
        result = process_syllabus_upload(course_name, file)

        if result['success']:
            return jsonify({
                'status': 'success',
                'message': result['message'],
                'course_id': result['course_id']
            })
        else:
            return jsonify({
                'status': 'error',
                'message': result['message']
            })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        })

@app.route('/chat')
def chat_interface():
    """Chat interface page"""
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """API endpoint for chat messages"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', '')

        if not user_message:
            return jsonify({
                'status': 'error',
                'message': 'Message is required'
            })

        if not session_id:
            return jsonify({
                'status': 'error',
                'message': 'Session ID is required'
            })

        # Get AI response
        ai_response = chat_with_claude(user_message)

        # Save conversation to database
        conversation_id = save_conversation(session_id, user_message, ai_response)

        # Update session activity for classification tracking
        update_session_activity(session_id)

        return jsonify({
            'status': 'success',
            'response': ai_response,
            'conversation_id': conversation_id
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        })

@app.route('/review')
def review_mode():
    """Review mode selection page"""
    return render_template('review.html')

@app.route('/api/courses')
def api_courses():
    """Get all available courses"""
    try:
        courses = get_courses()
        return jsonify({
            'status': 'success',
            'courses': courses
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error loading courses: {str(e)}'
        })

@app.route('/api/courses/<int:course_id>/topics')
def api_course_topics(course_id):
    """Get topics for a specific course"""
    try:
        courses = get_courses()
        course = next((c for c in courses if c['id'] == course_id), None)

        if not course:
            return jsonify({
                'status': 'error',
                'message': 'Course not found'
            })

        # Extract all topics from all units
        topics = []
        for unit in course['units']:
            topics.extend(unit['topics'])

        # Remove duplicates and sort
        unique_topics = sorted(list(set(topics)))

        return jsonify({
            'status': 'success',
            'topics': unique_topics
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error loading topics: {str(e)}'
        })

@app.route('/api/courses/<int:course_id>/review-topics')
def api_course_review_topics(course_id):
    """Get topics available for review based on confusion analysis"""
    try:
        result = get_available_review_topics(course_id)
        if result['success']:
            return jsonify({
                'status': 'success',
                'course_name': result['course_name'],
                'available_units': result['available_units'],
                'available_topics': result['available_topics'],
                'session_count': result.get('session_count', 0)
            })
        else:
            return jsonify({
                'status': 'error',
                'message': result['message']
            })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error loading review topics: {str(e)}'
        })

@app.route('/api/review/<int:course_id>/<topic>')
def api_review(course_id, topic):
    """Generate and return review content based on confusion analysis"""
    try:
        # Generate review using our intelligent system
        result = generate_review_by_criteria(course_id, topics=[topic])

        if result['success']:
            return jsonify({
                'status': 'success',
                'content': result['content'],
                'metadata': result['metadata']
            })
        else:
            return jsonify({
                'status': 'error',
                'message': result['message']
            })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error generating review: {str(e)}'
        })

@app.route('/api/review-request', methods=['POST'])
def api_review_request():
    """Generate review from natural language request"""
    try:
        data = request.get_json()
        natural_request = data.get('request', '').strip()

        if not natural_request:
            return jsonify({
                'status': 'error',
                'message': 'Review request is required'
            })

        # Generate review using natural language processing
        result = generate_review_from_request(natural_request)

        if result['success']:
            return jsonify({
                'status': 'success',
                'content': result['content'],
                'metadata': result['metadata']
            })
        else:
            return jsonify({
                'status': 'error',
                'message': result['message']
            })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error processing review request: {str(e)}'
        })

# Admin endpoints for session analysis
@app.route('/admin/analyze-session/<session_id>')
def admin_analyze_session(session_id):
    """Force analyze a specific session"""
    try:
        result = force_analyze_session(session_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@app.route('/admin/run-analysis')
def admin_run_analysis():
    """Run periodic analysis of all expired sessions"""
    try:
        run_periodic_analysis()
        return jsonify({
            'success': True,
            'message': 'Periodic analysis completed'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000)