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
-- Courses table
CREATE TABLE courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    syllabus_content TEXT NOT NULL,
    topics TEXT NOT NULL,  -- JSON array of topics
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Conversations table
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    course_topic TEXT,  -- Which syllabus topic this relates to
    confusion_detected BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Confusion points table
CREATE TABLE confusion_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER REFERENCES conversations(id),
    course_id INTEGER REFERENCES courses(id),
    topic TEXT NOT NULL,
    confusion_summary TEXT NOT NULL,
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

def extract_topics_from_syllabus(syllabus_text: str) -> List[str]:
    """Use LLM to extract course topics from syllabus"""

def save_course_to_db(course_name: str, syllabus_content: str, topics: List[str]):
    """Save parsed course data to database"""
```

### 2. LLM Service Module (`llm_service.py`)
```python
def chat_with_claude(user_message: str, conversation_history: List) -> str:
    """Handle normal chat conversations"""

def classify_conversation_topic(message: str, course_topics: List[str]) -> str:
    """Classify which syllabus topic the conversation relates to"""

def detect_confusion(conversation: str) -> bool:
    """Detect if student seems confused in conversation"""

def generate_review_summary(confusion_points: List) -> str:
    """Summarize confusion points for review"""

def generate_review_questions(confusion_summary: str, topic: str) -> List[str]:
    """Generate targeted review questions"""
```

### 3. Database Module (`database.py`)
```python
def init_database():
    """Initialize SQLite database with tables"""

def save_conversation(user_msg: str, ai_response: str, topic: str = None):
    """Save conversation to database"""

def get_conversations_by_topic(course_id: int, topic: str) -> List:
    """Retrieve conversations for specific topic"""

def save_confusion_point(conversation_id: int, course_id: int, topic: str, summary: str):
    """Save detected confusion point"""

def get_confusion_points(course_id: int, topic: str = None) -> List:
    """Get confusion points for review generation"""
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

### 3. Targeted Review Generation
- Select course/topic for review
- LLM summarizes past confusion points
- Generate personalized review questions
- Interactive Q&A session

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