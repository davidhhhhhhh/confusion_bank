# Confusion Bank 🎯

A smart web-based chatbot that helps students review questions based on syllabus-mapped conversations with AI. Students upload course syllabi, chat with AI about coursework, and get targeted review questions based on detected confusion points.

## 🚀 Features

### 📚 Intelligent Course Management
- **PDF Syllabus Upload**: Extract course structure from uploaded syllabi
- **Smart Topic Extraction**: AI-powered parsing of course units and topics
- **Multi-Course Support**: Handle multiple courses simultaneously

### 💬 Enhanced Chat Experience
- **Contextual Conversations**: AI maintains session history for better continuity
- **Markdown Support**: Rich formatting for code, equations, and structured content
- **Session Management**: Organize conversations with new session controls
- **Real-time Interface**: Smooth AJAX-powered chat experience

### 🎯 Intelligent Review System
- **Confusion Analysis**: AI analyzes conversations to identify knowledge gaps
- **Personalized Questions**: Generate targeted review questions based on actual confusion
- **Dual Review Modes**:
  - Natural language requests ("I want to review neural networks")
  - Traditional course/topic selection
- **AI-Powered Grading**: Intelligent answer evaluation with structured feedback
- **Color-Coded Scoring**: Visual feedback with percentage-based color mapping

### 🔍 Smart Analysis Features
- **Session-Based Grouping**: Organize conversations for better analysis
- **Background Processing**: Analyze conversation patterns for confusion detection
- **Progress Tracking**: Visual status updates and analysis readiness indicators

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with structured schema
- **AI/LLM**: Anthropic Claude API with increased token limits
- **PDF Processing**: PyPDF2 for syllabus parsing
- **Frontend**: HTML5, CSS3, JavaScript + Marked.js for markdown
- **UI/UX**: Responsive design with rich formatting support

## 📋 Prerequisites

- Python 3.8+
- Anthropic API key
- Modern web browser

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone <repository-url>
cd confusion_bank_hackmit25
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file:
```bash
ANTHROPIC_API_KEY=your_api_key_here
FLASK_ENV=development
FLASK_DEBUG=True
```

### 3. Initialize Database
```bash
python -c "from database import init_database; init_database()"
```

### 4. Run the Application
```bash
python app.py
```

Visit `http://localhost:5000` to start using Confusion Bank!

## 📖 How to Use

### Step 1: Start Chatting
- The app opens directly to the **Chat** interface (new default)
- Ask questions about any subject - AI maintains conversation context
- Use "New Session" to organize different topics

### Step 2: Upload Course Materials (Optional)
- Navigate to **Upload** tab
- Upload PDF syllabi to help AI understand your course structure
- AI extracts units and topics automatically

### Step 3: Get Personalized Review
- Go to **Review** tab
- Click "Analyze Past Content" to process your conversations
- Choose your review method:
  - **Quick Request**: "I want to review data structures"
  - **Browse Topics**: Select specific courses and topics
- Answer questions and get AI-powered feedback with color-coded scoring

## 🎨 AI Grading System

### Score Categories & Colors
- **🟢 Excellent (90-100%)**: Complete understanding with accurate details
- **🔵 Good (75-89%)**: Solid understanding with minor gaps
- **🟡 Fair (60-74%)**: Partial understanding, some correct concepts
- **🟠 Needs Improvement (40-59%)**: Limited understanding with significant gaps
- **🔴 Insufficient (0-39%)**: Minimal or incorrect understanding

### Feedback Structure
- ✅ **Strengths**: What you did well
- 💡 **Areas to Improve**: Specific improvement suggestions
- 📚 **Study Suggestions**: Targeted learning recommendations

## 🏗️ Architecture

### Database Schema
```sql
-- Courses: Store syllabus structure
courses (id, name, units, created_at)

-- Conversations: Individual chat messages
conversations (id, session_id, user_message, ai_response, created_at)

-- Confusion Points: Analysis results
confusion_points (id, session_id, course_id, unit, topics, confused_conversation_ids, created_at)
```

### Key Components
- **PDF Processor**: Syllabus parsing and topic extraction
- **LLM Service**: Claude API integration with context management
- **Classifier**: Conversation analysis and confusion detection
- **Review Generator**: Question generation based on confusion patterns
- **Grading System**: AI-powered answer evaluation

## 🔧 API Endpoints

### Chat System
- `GET /` → Redirects to chat interface
- `GET /chat` → Chat interface page
- `POST /api/chat` → Send chat message with session context

### Course Management
- `GET /upload` → Upload page
- `POST /upload` → Handle PDF syllabus upload
- `GET /api/courses` → Get all courses
- `GET /api/courses/{id}/review-topics` → Get reviewable topics

### Review System
- `GET /review` → Review selection page
- `POST /api/review-request` → Natural language review generation
- `GET /api/review/{course_id}/{topic}` → Traditional topic review
- `POST /api/grade-answer` → AI answer grading
- `GET /api/analysis-status` → Check analysis readiness

### Admin Functions
- `GET /admin/run-analysis` → Process conversation analysis
- `GET /admin/analyze-session/{id}` → Force analyze specific session

## 🎯 Demo Flow

1. **Chat Interaction**: Ask questions about various topics across multiple sessions
2. **Session Organization**: Use "New Session" to separate different subjects
3. **Analysis Processing**: Click "Analyze Past Content" in Review tab
4. **Review Generation**: Request reviews using natural language or topic selection
5. **Interactive Learning**: Answer questions and receive detailed AI feedback
6. **Continuous Improvement**: Use feedback to guide further study

## 🚀 Advanced Features

### Session Context Management
- AI maintains conversation history for continuity
- Limited to last 10 exchanges to manage token usage
- Automatic session grouping for analysis

### Intelligent Topic Classification
- AI maps conversations to course topics automatically
- Confusion detection based on question patterns and responses
- Background processing for scalable analysis

### Rich Content Support
- Markdown rendering in chat and reviews
- Code syntax highlighting
- Mathematical notation support
- Structured content display

## 🔒 Security & Privacy

- Local SQLite database - no cloud data storage
- API keys stored in environment variables
- Session-based conversation grouping
- No personal data collection beyond usage patterns

## 🤝 Contributing

This project was developed for HackMIT 2025. For improvements or bug reports:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request with detailed description

## 📝 License

MIT License - see LICENSE file for details

## 🏆 Acknowledgments

- Built for HackMIT 2025
- Powered by Anthropic Claude API
- Inspired by the need for personalized learning tools

---

**Happy Learning! 🎓** Use Confusion Bank to turn your conversations into targeted review sessions and improve your understanding through AI-powered feedback.