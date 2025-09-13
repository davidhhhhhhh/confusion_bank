// Frontend JavaScript for Confusion Bank

document.addEventListener('DOMContentLoaded', function() {
    // Initialize page-specific functionality
    const currentPath = window.location.pathname;

    if (currentPath === '/' || currentPath.includes('upload')) {
        initUploadPage();
    } else if (currentPath.includes('chat')) {
        initChatPage();
    } else if (currentPath.includes('review')) {
        initReviewPage();
    }
});

// Upload page functionality
function initUploadPage() {
    const uploadForm = document.getElementById('upload-form');

    if (uploadForm) {
        uploadForm.addEventListener('submit', handleFileUpload);
    }
}

function handleFileUpload(event) {
    event.preventDefault();

    const formData = new FormData();
    const courseNameInput = document.getElementById('course-name');
    const syllabusFileInput = document.getElementById('syllabus-file');

    formData.append('course-name', courseNameInput.value);
    formData.append('syllabus-file', syllabusFileInput.files[0]);

    // Show loading state
    showStatus('Uploading and processing syllabus...', 'info');

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showStatus('Syllabus uploaded and processed successfully!', 'success');
            uploadForm.reset();
            // Redirect to chat after successful upload
            setTimeout(() => {
                window.location.href = '/chat';
            }, 2000);
        } else {
            showStatus('Error: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showStatus('An error occurred during upload.', 'error');
    });
}

// Chat page functionality
function initChatPage() {
    const chatForm = document.getElementById('chat-form');
    const chatMessages = document.getElementById('chat-messages');

    if (chatForm) {
        chatForm.addEventListener('submit', handleChatMessage);
    }

    // Generate or retrieve session ID
    if (!sessionStorage.getItem('chatSessionId')) {
        sessionStorage.setItem('chatSessionId', generateSessionId());
    }

    // Add welcome message
    addMessage('Hello! I\'m here to help you with your coursework. Ask me anything!', 'ai');
}

function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substring(2);
}

function handleChatMessage(event) {
    event.preventDefault();

    const chatInput = document.getElementById('chat-input');
    const message = chatInput.value.trim();

    if (!message) return;

    // Add user message to chat
    addMessage(message, 'user');
    chatInput.value = '';

    // Show typing indicator
    const typingId = addMessage('Thinking...', 'ai', 'typing');

    // Send message to backend
    fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: message,
            session_id: sessionStorage.getItem('chatSessionId')
        })
    })
    .then(response => response.json())
    .then(data => {
        // Remove typing indicator
        removeMessage(typingId);

        if (data.status === 'success') {
            // Add AI response
            addMessage(data.response, 'ai');
        } else {
            addMessage('Sorry, there was an error: ' + data.message, 'ai', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        removeMessage(typingId);
        addMessage('Sorry, there was an error processing your message.', 'ai', 'error');
    });
}

function addMessage(content, sender, messageType = '') {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    const messageId = Date.now() + Math.random();

    messageDiv.className = `message ${sender} ${messageType}`;
    messageDiv.id = `message-${messageId}`;
    messageDiv.textContent = content;

    // Add timestamp for messages
    if (sender === 'user' || sender === 'ai') {
        const timestamp = document.createElement('div');
        timestamp.className = 'timestamp';
        timestamp.textContent = new Date().toLocaleTimeString();
        messageDiv.appendChild(timestamp);
    }

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return messageId;
}

function removeMessage(messageId) {
    const message = document.getElementById(`message-${messageId}`);
    if (message) {
        message.remove();
    }
}

// Review page functionality
function initReviewPage() {
    const courseSelect = document.getElementById('course-select');
    const topicSelect = document.getElementById('topic-select');
    const startReviewBtn = document.getElementById('start-review');
    const naturalRequestInput = document.getElementById('natural-request');
    const generateNaturalReviewBtn = document.getElementById('generate-natural-review');

    // Initialize traditional course/topic selection
    if (courseSelect) {
        loadCourses();
        courseSelect.addEventListener('change', handleCourseChange);
    }

    if (topicSelect) {
        topicSelect.addEventListener('change', handleTopicChange);
    }

    if (startReviewBtn) {
        startReviewBtn.addEventListener('click', startTraditionalReview);
    }

    // Initialize natural language review
    if (naturalRequestInput) {
        naturalRequestInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                handleNaturalLanguageReview();
            }
        });
    }

    if (generateNaturalReviewBtn) {
        generateNaturalReviewBtn.addEventListener('click', handleNaturalLanguageReview);
    }

    // Initialize review navigation
    initReviewNavigation();
}

function loadCourses() {
    const courseSelect = document.getElementById('course-select');

    fetch('/api/courses')
    .then(response => response.json())
    .then(data => {
        courseSelect.innerHTML = '<option value="">Select a course</option>';

        if (data.status === 'success') {
            data.courses.forEach(course => {
                const option = document.createElement('option');
                option.value = course.id;
                option.textContent = course.name;
                courseSelect.appendChild(option);
            });
        } else {
            courseSelect.innerHTML = '<option value="">No courses available</option>';
        }
    })
    .catch(error => {
        console.error('Error loading courses:', error);
        courseSelect.innerHTML = '<option value="">Error loading courses</option>';
    });
}

function handleCourseChange(event) {
    const courseId = event.target.value;
    const topicSelect = document.getElementById('topic-select');
    const startReviewBtn = document.getElementById('start-review');

    topicSelect.innerHTML = '<option value="">Loading review topics...</option>';
    topicSelect.disabled = true;
    startReviewBtn.disabled = true;

    if (courseId) {
        // Load topics that have actual confusion points for review
        fetch(`/api/courses/${courseId}/review-topics`)
        .then(response => response.json())
        .then(data => {
            topicSelect.innerHTML = '<option value="">Select a topic</option>';

            if (data.status === 'success' && data.available_topics.length > 0) {
                data.available_topics.forEach(topic => {
                    const option = document.createElement('option');
                    option.value = topic;
                    option.textContent = topic;
                    topicSelect.appendChild(option);
                });
                topicSelect.disabled = false;

                // Show course info
                const courseInfo = `Found ${data.session_count} sessions with confusion points`;
                console.log(courseInfo);
            } else {
                topicSelect.innerHTML = '<option value="">No confusion points found - chat first!</option>';
            }
        })
        .catch(error => {
            console.error('Error loading review topics:', error);
            topicSelect.innerHTML = '<option value="">Error loading topics</option>';
        });
    } else {
        topicSelect.innerHTML = '<option value="">Select a course first</option>';
    }
}

function handleTopicChange(event) {
    const startReviewBtn = document.getElementById('start-review');
    const courseSelect = document.getElementById('course-select');

    if (event.target.value && courseSelect.value) {
        startReviewBtn.disabled = false;
    } else {
        startReviewBtn.disabled = true;
    }
}

// Global review state
let currentReview = {
    questions: [],
    currentIndex: 0,
    metadata: null
};

function handleNaturalLanguageReview() {
    const naturalRequest = document.getElementById('natural-request').value.trim();

    if (!naturalRequest) {
        showStatus('Please enter a review request.', 'error');
        return;
    }

    showStatus('Processing your request and generating personalized review...', 'info');

    fetch('/api/review-request', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({request: naturalRequest})
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            displayReviewContent(data.content, data.metadata, `Review: "${naturalRequest}"`);
            hideStatus();
        } else {
            showStatus('Error: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showStatus('Error processing your request.', 'error');
    });
}

function startTraditionalReview() {
    const courseId = document.getElementById('course-select').value;
    const topic = document.getElementById('topic-select').value;

    if (!courseId || !topic) {
        showStatus('Please select both a course and topic.', 'error');
        return;
    }

    showStatus('Generating personalized review questions...', 'info');

    fetch(`/api/review/${courseId}/${encodeURIComponent(topic)}`)
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            displayReviewContent(data.content, data.metadata, `Review: ${topic}`);
            hideStatus();
        } else {
            showStatus('Error: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showStatus('Error loading review questions.', 'error');
    });
}

function displayReviewContent(content, metadata, title) {
    // Store review data globally
    currentReview.questions = content.questions;
    currentReview.currentIndex = 0;
    currentReview.metadata = metadata;

    // Show review content section
    const reviewContent = document.getElementById('review-content');
    reviewContent.style.display = 'block';

    // Set title and summary
    document.getElementById('review-title').textContent = title;
    document.getElementById('review-summary').textContent = content.summary;

    // Set metadata stats
    const stats = document.getElementById('review-stats');
    if (metadata) {
        stats.innerHTML = `
            <small>
                📊 Based on ${metadata.session_count} session(s) •
                🎯 ${content.questions.length} questions •
                📚 ${metadata.course_name || 'Multiple courses'}
            </small>
        `;
    }

    // Display first question
    displayCurrentQuestion();

    // Scroll to review content
    reviewContent.scrollIntoView({ behavior: 'smooth' });
}

function displayCurrentQuestion() {
    const questions = currentReview.questions;
    const index = currentReview.currentIndex;

    if (questions.length === 0) return;

    const question = questions[index];
    const reviewQuestions = document.getElementById('review-questions');

    reviewQuestions.innerHTML = `
        <div class="question active">
            <div class="question-header">
                <h4>Question ${index + 1}</h4>
                <span class="question-type">${question.type}</span>
            </div>
            <div class="question-content">
                <p class="question-text">${question.question}</p>
                ${question.hint ? `<div class="hint">💡 <em>${question.hint}</em></div>` : ''}
                <div class="answer-section">
                    <textarea id="current-answer" placeholder="Type your answer here..." rows="4"></textarea>
                    <div class="answer-actions">
                        <button class="btn-secondary" onclick="showHint()">Show Hint</button>
                        <button class="btn-primary" onclick="checkAnswer()">Check Answer</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Update question counter
    document.getElementById('question-counter').textContent =
        `Question ${index + 1} of ${questions.length}`;

    // Update navigation buttons
    document.getElementById('prev-question').disabled = (index === 0);
    document.getElementById('next-question').disabled = (index === questions.length - 1);
}

function initReviewNavigation() {
    const prevBtn = document.getElementById('prev-question');
    const nextBtn = document.getElementById('next-question');
    const endBtn = document.getElementById('end-review');

    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            if (currentReview.currentIndex > 0) {
                currentReview.currentIndex--;
                displayCurrentQuestion();
            }
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            if (currentReview.currentIndex < currentReview.questions.length - 1) {
                currentReview.currentIndex++;
                displayCurrentQuestion();
            }
        });
    }

    if (endBtn) {
        endBtn.addEventListener('click', endReviewSession);
    }
}

function showHint() {
    const question = currentReview.questions[currentReview.currentIndex];
    if (question.hint) {
        const hintDiv = document.querySelector('.hint');
        if (hintDiv) {
            hintDiv.style.display = hintDiv.style.display === 'none' ? 'block' : 'none';
        }
    }
}

function checkAnswer() {
    const answer = document.getElementById('current-answer').value.trim();
    if (!answer) {
        showStatus('Please provide an answer first.', 'error');
        return;
    }

    // For now, just show encouragement - could add LLM answer evaluation later
    showStatus('Great job! Keep practicing with the next question.', 'success');
}

function endReviewSession() {
    if (confirm('Are you sure you want to end this review session?')) {
        // Hide review content
        document.getElementById('review-content').style.display = 'none';

        // Reset form
        document.getElementById('natural-request').value = '';
        document.getElementById('course-select').value = '';
        document.getElementById('topic-select').innerHTML = '<option value="">Select a course first</option>';
        document.getElementById('topic-select').disabled = true;
        document.getElementById('start-review').disabled = true;

        // Reset review state
        currentReview = {
            questions: [],
            currentIndex: 0,
            metadata: null
        };

        showStatus('Review session completed! Great job practicing.', 'success');
        setTimeout(hideStatus, 3000);
    }
}

// Utility functions
function showStatus(message, type) {
    const statusElements = document.querySelectorAll('.status-message');
    statusElements.forEach(element => {
        element.textContent = message;
        element.className = `status-message ${type}`;
        element.style.display = 'block';
    });
}

function hideStatus() {
    const statusElements = document.querySelectorAll('.status-message');
    statusElements.forEach(element => {
        element.style.display = 'none';
    });
}