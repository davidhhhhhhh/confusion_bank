# Confusion Bank - Flask Implementation Plan

## Project Overview
A web-based chatbot that helps students review questions based on syllabus-mapped conversations with LLMs. Students upload course syllabi, chat with AI about coursework, and get targeted review questions based on detected confusion points.

## Tech Stack
- **Backend**: Flask (Python)
- **Database**: SQLite
- **LLM**: Anthropic Claude API (increased token limits for full responses)
- **PDF Processing**: PyPDF2
- **Frontend**: HTML/CSS/JavaScript + Marked.js for markdown rendering
- **UI Enhancement**: Rich markdown formatting in chat and reviews
- **AI Grading**: Intelligent answer evaluation with structured feedback
- **Session Management**: Browser-based session tracking with new session controls

## System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   HTML/CSS/JS   │    │   Flask Server   │    │  Anthropic API  │
│   Templates     │◄──►│   Python Routes  │◄──►│   Claude LLM    │
│   File Upload   │    │   Business Logic │    │   Chat & Review │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │     SQLite       │
                       │   Local Database │
                       │   Conversations  │
                       └──────────────────┘
```

## Database Schema

```sql
-- Courses table - stores syllabus structure
CREATE TABLE courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    units TEXT NOT NULL,    -- JSON: [{"name": "Unit 1", "topics": ["topic1", "topic2"]}]
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Conversations table - individual user-AI message pairs
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,  -- Groups related conversations
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Confusion points table - analysis results per session
CREATE TABLE confusion_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    course_id INTEGER REFERENCES courses(id),
    unit TEXT,
    topics TEXT,  -- JSON array of identified topics
    confused_conversation_ids TEXT,  -- JSON array of conversation IDs showing confusion
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Project Structure

```
confusion_bank/
├── app.py              # Main Flask application
├── database.py         # Database setup and queries
├── llm_service.py      # Anthropic API integration + grading system
├── pdf_processor.py    # PDF parsing and topic extraction
├── classifier.py       # Conversation topic classification
├── review_generator.py # Review questions generation
├── prompts/            # LLM prompt templates
│   ├── __init__.py     # Prompt loading utilities
│   └── answer_grading.txt # AI grading evaluation template
├── templates/
│   ├── base.html       # Base template
│   ├── upload.html     # Syllabus upload page
│   ├── chat.html       # Chat interface with session controls
│   └── review.html     # Review mode with analysis status
├── static/
│   ├── style.css       # Enhanced styling with grading UI
│   └── script.js       # Frontend JavaScript with grading integration
├── requirements.txt    # Python dependencies
└── README.md          # Project documentation
```

## Core Modules

### 1. PDF Processor Module (`pdf_processor.py`)
```python
def extract_text_from_pdf(pdf_file) -> str:
    """Extract raw text from uploaded PDF"""

def extract_course_structure(syllabus_text: str) -> Dict:
    """Use LLM to extract course units and topics structure"""

def save_course_to_db(course_name: str, units_structure: Dict):
    """Save parsed course structure to database"""
```

### 2. LLM Service Module (`llm_service.py`)
```python
def chat_with_claude(user_message: str) -> str:
    """Handle normal chat conversations with Claude (4096 max tokens)"""

def analyze_session_confusion(session_conversations: List[Dict], courses: List[Dict]) -> Dict:
    """Analyze entire session for course/unit/topic classification and confusion detection
    Returns: {course_id, unit, topics, confused_conversation_ids} (2048 max tokens)"""

def parse_review_request(natural_language: str, courses: List[Dict]) -> Dict:
    """Parse natural language review request to course/unit/topics (1024 max tokens)"""

def generate_review_content(confusion_sessions: List[Dict]) -> Dict:
    """Generate review questions based on confusion session contexts (4096 max tokens)"""

def improve_course_structure_extraction(syllabus_text: str) -> List[Dict]:
    """Extract course units and topics from syllabus (2048 max tokens)"""

def grade_student_answer(question: str, question_type: str, student_answer: str, hint: str = None) -> Dict:
    """Evaluate student answers using AI with structured feedback (2048 max tokens)"""
```

### 3. Database Module (`database.py`)
```python
def init_database():
    """Initialize SQLite database with tables"""

def save_conversation(session_id: str, user_msg: str, ai_response: str) -> int:
    """Save conversation pair to database"""

def get_session_conversations(session_id: str) -> List[Dict]:
    """Get all conversations for a session"""

def get_unanalyzed_sessions() -> List[str]:
    """Get session IDs that have conversations but no confusion analysis"""

def save_confusion_analysis(session_id: str, course_id: int, unit: str, topics: List[str], confused_ids: List[int]):
    """Save confusion analysis results"""

def get_confusion_sessions(course_id: int = None, unit: str = None, topics: List[str] = None) -> List[str]:
    """Get session IDs matching review criteria"""
```

### 4. Main Flask App (`app.py`)
```python
@app.route('/')
def home():
    """Landing page with course upload"""

@app.route('/upload', methods=['POST'])
def upload_syllabus():
    """Handle PDF syllabus upload and processing"""

@app.route('/chat')
def chat_interface():
    """Chat interface page"""

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """API endpoint for chat messages"""

@app.route('/review')
def review_mode():
    """Review mode selection page"""

@app.route('/api/review/<course_id>/<topic>')
def api_review(course_id, topic):
    """Generate and return review content"""

@app.route('/admin/run-analysis')
def admin_run_analysis():
    """Trigger analysis of all unprocessed sessions"""

@app.route('/api/grade-answer', methods=['POST'])
def api_grade_answer():
    """Grade student's answer to review question with AI feedback"""

@app.route('/api/analysis-status')
def api_analysis_status():
    """Check if all conversations have been analyzed for review readiness"""
```

## Implementation Timeline (12 hours)

### Phase 1: Foundation (Hours 1-3)
- Set up Flask project structure
- Create database schema and initialization
- Basic HTML templates and routing
- PDF upload functionality with text extraction

### Phase 2: Enhanced Chat (Hours 4-6)
- Anthropic API integration for chat (increased token limits)
- Markdown rendering integration (Marked.js)
- Conversation storage and retrieval
- Basic topic classification
- Real-time chat interface with AJAX and rich formatting

### Phase 3: Enhanced Review System (Hours 7-9)
- User-triggered confusion analysis button
- Confusion point detection and storage (2048 tokens)
- Rich review summary generation with markdown
- Comprehensive review question generation (4096 tokens)
- Review interface with formatted content display

### Phase 4: Polish & UX (Hours 10-12)
- Enhanced UI styling with markdown support
- CSS styling for code blocks, headers, and formatting
- Error handling and validation
- Testing with sample data including formatted responses
- Demo preparation with rich content examples

## Key Features

### 1. Syllabus Upload & Processing
- Upload PDF syllabus files
- Extract text using PyPDF2
- Use LLM to identify course topics/modules
- Store course structure in database

### 2. Enhanced Chat System with Session Management
- Normal conversation flow with Claude (up to 4096 tokens)
- Rich markdown rendering (headers, code blocks, lists, formatting)
- Browser-based session tracking using sessionStorage
- "New Session" button to start fresh conversations
- Conversation history storage with session grouping
- Manual analysis trigger for confusion detection
- No automatic background processing
- Smooth, formatted responses for better readability

### 3. User-Triggered Confusion Analysis
- Store conversations with session IDs for grouping
- User triggers analysis via "Analyze My Confusion Points" button
- Analyze all unprocessed sessions for course/unit/topic classification
- Identify specific conversations showing confusion
- Store analysis results for review generation

### 4. Enhanced Review System with AI Grading
- **UI Improvements**: Analysis section prominently at top, side-by-side review options
- **Smart Status Checking**: Analysis button shows when sessions need processing
- **Dual Review Modes**: Natural language requests OR topic-based selection
- Student requests review in natural language (e.g., "I want to review CS101 loops")
- LLM maps request to course/unit/topics structure (1024 tokens)
- Query confusion points to find relevant sessions
- Generate comprehensive review questions using full session context (4096 tokens)
- Rich markdown formatting in review summaries and questions
- Support for code examples, math formulas, and structured content

### 5. AI-Powered Answer Grading
- **Intelligent Evaluation**: AI grades student answers with 5-tier scoring system
- **Structured Feedback**: Strengths, improvement areas, specific suggestions, encouragement
- **Educational Focus**: Constructive, supportive feedback designed for learning
- **Professional UI**: Circular score display, detailed feedback sections
- **Hint System**: Optional hints that remain hidden until requested
- **Question Types**: Support for conceptual, coding, and calculation questions

## Environment Setup

### Required Python Packages
```txt
Flask==2.3.3
anthropic==0.7.8
PyPDF2==3.0.1
sqlite3 (built-in)
python-dotenv==1.0.0
```

### Environment Variables
```bash
ANTHROPIC_API_KEY=your_api_key_here
FLASK_ENV=development
FLASK_DEBUG=True
```

## Demo Flow
1. **Upload**: Upload 2 sample course syllabi (CS101, MATH201)
2. **Chat**: Have conversations about various course topics across multiple sessions
3. **Session Management**: Use "New Session" button to organize different conversation topics
4. **Analysis**: Click "Analyze Past Content" to process all conversations (top of review page)
5. **Review Selection**: Choose between natural language requests or topic-based selection
6. **Interactive Learning**: Answer review questions and receive detailed AI-powered feedback
7. **Iterative Improvement**: Use feedback suggestions to deepen understanding

## Success Metrics
- ✅ Successfully parse PDF syllabi with improved extraction (2048 tokens)
- ✅ Classify 80%+ of conversations to correct topics
- ✅ Generate comprehensive, well-formatted review questions (4096 tokens)
- ✅ AI grading system with structured educational feedback
- ✅ Complete end-to-end user flow in demo with rich content
- ✅ Responsive interface with markdown rendering on mobile/desktop
- ✅ Enhanced UX with smooth formatted responses
- ✅ Session management with new session functionality
- ✅ Professional grading UI with detailed feedback display
- ✅ Smart analysis status checking and user guidance

## Deployment
For hackathon demo:
- Local Flask development server
- SQLite database file
- Static file serving through Flask
- No complex deployment needed