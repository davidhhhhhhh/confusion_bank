# Confusion Bank - Implementation TODO

## Module 1: Project Foundation & Setup
- [x] Create project directory structure
- [x] Set up virtual environment
- [x] Install required packages (Flask, anthropic, PyPDF2, etc.)
- [x] Create `.env` file with Anthropic API key
- [ ] Initialize Git repository
- [x] Create basic `app.py` with Flask setup
- [x] Test Flask server runs successfully

## Module 2: Database Setup
- [ ] Create `database.py` file
- [ ] Design SQLite database schema
- [ ] Implement `init_database()` function
- [ ] Create tables: courses, conversations, confusion_points
- [ ] Test database creation and connection
- [ ] Implement basic CRUD functions
- [ ] Test database operations with sample data

## Module 3: PDF Processing & Syllabus Upload
- [ ] Create `pdf_processor.py` file
- [ ] Implement `extract_text_from_pdf()` function using PyPDF2
- [ ] Test PDF text extraction with sample files
- [ ] Implement `extract_topics_from_syllabus()` using LLM
- [x] Create `/upload` route in Flask
- [x] Create `templates/upload.html` for file upload form
- [ ] Test end-to-end PDF upload and topic extraction
- [ ] Implement `save_course_to_db()` function

## Module 4: LLM Service Integration
- [ ] Create `llm_service.py` file
- [ ] Set up Anthropic client configuration
- [ ] Implement `chat_with_claude()` function
- [ ] Test basic chat functionality
- [ ] Implement `classify_conversation_topic()` function
- [ ] Implement `detect_confusion()` function
- [ ] Test topic classification with sample conversations
- [ ] Test confusion detection accuracy

## Module 5: Chat Interface
- [ ] Create `templates/chat.html` with chat interface
- [ ] Create `static/script.js` for AJAX chat functionality
- [ ] Implement `/chat` route for chat page
- [ ] Implement `/api/chat` API endpoint
- [ ] Test real-time chat experience
- [ ] Implement conversation history display
- [ ] Add course selection for chat context
- [ ] Test conversation storage to database

## Module 6: Conversation Classification
- [ ] Create `classifier.py` file
- [ ] Integrate topic classification into chat flow
- [ ] Implement background classification of conversations
- [ ] Test classification accuracy with various topics
- [ ] Implement confusion point detection and storage
- [ ] Add visual indicators for classified topics
- [ ] Test classification persistence in database

## Module 7: Review System - Backend
- [ ] Create `review_generator.py` file
- [ ] Implement `generate_review_summary()` function
- [ ] Implement `generate_review_questions()` function
- [ ] Test review content generation
- [ ] Implement course and topic selection logic
- [ ] Create database queries for confusion points retrieval
- [ ] Test review data aggregation

## Module 8: Review Interface
- [ ] Create `templates/review.html` for review mode
- [ ] Implement `/review` route for course/topic selection
- [ ] Implement `/api/review/<course_id>/<topic>` API endpoint
- [ ] Create interactive Q&A interface
- [ ] Add review session management
- [ ] Test complete review flow
- [ ] Add navigation between review questions

## Module 9: Frontend Styling & UX
- [ ] Create `static/style.css` for basic styling
- [ ] Style upload page with clean design
- [ ] Style chat interface for good UX
- [ ] Style review interface for readability
- [ ] Add responsive design for mobile
- [ ] Add loading states and user feedback
- [ ] Test cross-browser compatibility

## Module 10: Error Handling & Polish
- [ ] Add error handling for PDF upload failures
- [ ] Add error handling for API failures
- [ ] Add input validation for all forms
- [ ] Add user feedback messages (success/error)
- [ ] Test edge cases (empty PDFs, API timeouts)
- [ ] Add graceful fallbacks for LLM failures
- [ ] Implement proper logging

## Module 11: Demo Preparation
- [ ] Create sample syllabus PDFs for demo
- [ ] Prepare sample conversation scenarios
- [ ] Test complete user flow end-to-end
- [ ] Create demo script and talking points
- [ ] Test app performance under demo conditions
- [ ] Prepare backup plans for common demo issues
- [ ] Document known limitations

## Module 12: Final Testing & Deployment
- [ ] Run comprehensive testing of all features
- [ ] Fix any critical bugs discovered
- [ ] Optimize database queries for demo
- [ ] Test app on different devices/browsers
- [ ] Prepare deployment environment
- [ ] Create final demo data set
- [ ] Run final rehearsal of demo flow

---

## Completion Tracking

### Phase 1 (Hours 1-3): Foundation ✅/❌
- Module 1: Project Setup
- Module 2: Database Setup
- Module 3: PDF Processing

### Phase 2 (Hours 4-6): Core Chat ✅/❌
- Module 4: LLM Integration
- Module 5: Chat Interface
- Module 6: Classification

### Phase 3 (Hours 7-9): Review System ✅/❌
- Module 7: Review Backend
- Module 8: Review Interface

### Phase 4 (Hours 10-12): Polish & Demo ✅/❌
- Module 9: Styling & UX
- Module 10: Error Handling
- Module 11: Demo Prep
- Module 12: Final Testing

---

## Notes & Reminders
- **Priority**: Focus on core functionality first, polish last
- **Testing**: Test each module thoroughly before moving to next
- **Demo**: Keep demo scenario simple but impressive
- **Backup**: Have fallback plans for each major component
- **Time Management**: Stick to timeline, cut features if needed

## Quick Commands
```bash
# Start development
source venv/bin/activate
export FLASK_ENV=development
python app.py

# Reset database
python -c "from database import init_database; init_database()"

# Test API endpoints
curl -X POST http://localhost:5000/api/chat -d '{"message": "test"}'
```