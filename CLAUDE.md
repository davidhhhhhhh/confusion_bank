# Confusion Bank - Flask Implementation Plan

## Project Overview
A web-based chatbot that helps students review questions based on syllabus-mapped conversations with LLMs. Students upload course syllabi, chat with AI about coursework, and get targeted review questions based on detected confusion points.

## Tech Stack
- **Backend**: Flask (Python)
- **Database**: SQLite
- **LLM**: Anthropic Claude API
- **PDF Processing**: PyPDF2
- **Frontend**: HTML/CSS/JavaScript (no frameworks)

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
├── llm_service.py      # Anthropic API integration
├── pdf_processor.py    # PDF parsing and topic extraction
├── classifier.py       # Conversation topic classification
├── review_generator.py # Review questions generation
├── templates/
│   ├── base.html       # Base template
│   ├── upload.html     # Syllabus upload page
│   ├── chat.html       # Chat interface
│   └── review.html     # Review mode interface
├── static/
│   ├── style.css       # Basic styling
│   └── script.js       # Frontend JavaScript
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
    """Handle normal chat conversations"""

def analyze_session_confusion(session_conversations: List[Dict], courses: List[Dict]) -> Dict:
    """Analyze entire session for course/unit/topic classification and confusion detection
    Returns: {course_id, unit, topics, confused_conversation_ids}"""

def parse_review_request(natural_language: str, courses: List[Dict]) -> Dict:
    """Parse natural language review request to course/unit/topics"""

def generate_review_content(confusion_sessions: List[Dict]) -> Dict:
    """Generate review questions based on confusion session contexts"""
```

### 3. Database Module (`database.py`)
```python
def init_database():
    """Initialize SQLite database with tables"""

def save_conversation(session_id: str, user_msg: str, ai_response: str) -> int:
    """Save conversation pair to database"""

def get_session_conversations(session_id: str) -> List[Dict]:
    """Get all conversations for a session"""

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
```

## Implementation Timeline (12 hours)

### Phase 1: Foundation (Hours 1-3)
- Set up Flask project structure
- Create database schema and initialization
- Basic HTML templates and routing
- PDF upload functionality with text extraction

### Phase 2: Core Chat (Hours 4-6)
- Anthropic API integration for chat
- Conversation storage and retrieval
- Basic topic classification
- Real-time chat interface with AJAX

### Phase 3: Review System (Hours 7-9)
- Confusion point detection and storage
- Review summary generation
- Review question generation
- Review interface implementation

### Phase 4: Polish (Hours 10-12)
- UI improvements and styling
- Error handling and validation
- Testing with sample data
- Demo preparation

## Key Features

### 1. Syllabus Upload & Processing
- Upload PDF syllabus files
- Extract text using PyPDF2
- Use LLM to identify course topics/modules
- Store course structure in database

### 2. Intelligent Chat Classification
- Normal conversation flow with Claude
- Background topic classification
- Automatic confusion detection
- Conversation history storage

### 3. Session-Based Confusion Analysis
- Group conversations into sessions (user-initiated + 30min timeout)
- Analyze complete sessions for course/unit/topic classification
- Identify specific conversations showing confusion
- Store analysis results for review generation

### 4. Natural Language Review System
- Student requests review in natural language (e.g., "I want to review CS101 loops")
- LLM maps request to course/unit/topics structure
- Query confusion points to find relevant sessions
- Generate review questions using full session context

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
2. **Chat**: Have conversations about various course topics
3. **Classification**: Show how conversations map to syllabus topics
4. **Review**: Select a course/topic, see confusion summary, answer review questions

## Success Metrics
- ✅ Successfully parse PDF syllabi
- ✅ Classify 80%+ of conversations to correct topics
- ✅ Generate relevant review questions
- ✅ Complete end-to-end user flow in demo
- ✅ Responsive interface on mobile/desktop

## Deployment
For hackathon demo:
- Local Flask development server
- SQLite database file
- Static file serving through Flask
- No complex deployment needed