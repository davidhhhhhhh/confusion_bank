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
            event.target.reset(); // Use event.target to reference the form
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
    const newSessionBtn = document.getElementById('new-session-btn');

    if (chatForm) {
        chatForm.addEventListener('submit', handleChatMessage);
    }

    if (newSessionBtn) {
        newSessionBtn.addEventListener('click', startNewSession);
    }

    // Generate or retrieve session ID
    if (!sessionStorage.getItem('chatSessionId')) {
        sessionStorage.setItem('chatSessionId', generateSessionId());
    }

    // Update session display
    updateSessionDisplay();

    // Add welcome message
    addMessage('Hello! I\'m here to help you with your coursework. Ask me anything!', 'ai');
}

function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substring(2);
}

function updateSessionDisplay() {
    const sessionDisplay = document.getElementById('current-session-display');
    const sessionId = sessionStorage.getItem('chatSessionId');

    if (sessionDisplay && sessionId) {
        // Show a shortened version of the session ID
        const shortId = sessionId.substring(8, 16); // Take part of timestamp
        sessionDisplay.textContent = `Session: ${shortId}`;
    }
}

function startNewSession() {
    if (confirm('Start a new conversation session? This will clear your current chat and create a fresh session for analysis.')) {
        // Generate new session ID
        const newSessionId = generateSessionId();
        sessionStorage.setItem('chatSessionId', newSessionId);

        // Clear chat messages
        const chatMessages = document.getElementById('chat-messages');
        if (chatMessages) {
            chatMessages.innerHTML = '';
        }

        // Update session display
        updateSessionDisplay();

        // Add welcome message for new session
        addMessage('🔄 New session started! Ask me anything about your coursework.', 'ai');

        // Show confirmation
        const shortId = newSessionId.substring(8, 16);
        showStatus(`New session created: ${shortId}`, 'success');
        setTimeout(hideStatus, 3000);
    }
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

    // Render markdown for AI messages, plain text for user messages
    if (sender === 'ai' && typeof marked !== 'undefined') {
        messageDiv.innerHTML = marked.parse(content);
    } else {
        messageDiv.textContent = content;
    }

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

    // Check analysis status first
    checkAnalysisStatus();

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

    // Initialize analysis functionality
    const analyzeBtn = document.getElementById('analyze-confusion');
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', handleAnalysisRequest);
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

    // Set title and summary with markdown rendering
    document.getElementById('review-title').textContent = title;
    const reviewSummaryEl = document.getElementById('review-summary');
    if (typeof marked !== 'undefined' && content.summary) {
        reviewSummaryEl.innerHTML = marked.parse(content.summary);
    } else {
        reviewSummaryEl.textContent = content.summary;
    }

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

    // Create question HTML with markdown rendering
    const questionHTML = typeof marked !== 'undefined' ? marked.parse(question.question) : question.question;
    const hintHTML = question.hint && typeof marked !== 'undefined' ? marked.parse(question.hint) : question.hint;

    reviewQuestions.innerHTML = `
        <div class="question active">
            <div class="question-header">
                <h4>Question ${index + 1}</h4>
                <span class="question-type">${question.type}</span>
            </div>
            <div class="question-content">
                <div class="question-text">${questionHTML}</div>
                ${question.hint ? `<div class="hint" style="display: none;">💡 ${hintHTML}</div>` : ''}
                <div class="answer-section">
                    <textarea id="current-answer" placeholder="Type your answer here..." rows="4"></textarea>
                    <div class="answer-actions">
                        ${question.hint ? `<button class="btn-secondary" onclick="showHint()">Show Hint</button>` : ''}
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
        const hintButton = document.querySelector('.answer-actions .btn-secondary');

        if (hintDiv && hintButton) {
            const isHidden = hintDiv.style.display === 'none';

            if (isHidden) {
                // Show hint
                hintDiv.style.display = 'block';
                hintButton.textContent = 'Hide Hint';
            } else {
                // Hide hint
                hintDiv.style.display = 'none';
                hintButton.textContent = 'Show Hint';
            }
        }
    }
}

function checkAnswer() {
    const answer = document.getElementById('current-answer').value.trim();
    if (!answer) {
        showStatus('Please provide an answer first.', 'error');
        return;
    }

    const currentQuestion = currentReview.questions[currentReview.currentIndex];

    // Show loading state
    const checkBtn = document.querySelector('.answer-actions .btn-primary');
    const originalText = checkBtn.textContent;
    checkBtn.textContent = 'Grading...';
    checkBtn.disabled = true;

    showStatus('Evaluating your answer...', 'info');

    // Submit answer for grading
    fetch('/api/grade-answer', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            question: currentQuestion.question,
            question_type: currentQuestion.type,
            student_answer: answer,
            hint: currentQuestion.hint || ''
        })
    })
    .then(response => response.json())
    .then(data => {
        // Reset button state
        checkBtn.textContent = originalText;
        checkBtn.disabled = false;

        if (data.status === 'success') {
            displayGradingResults(data.grading);
            hideStatus();
        } else {
            showStatus('Error grading answer: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);

        // Reset button state
        checkBtn.textContent = originalText;
        checkBtn.disabled = false;

        showStatus('Error submitting answer for grading.', 'error');
    });
}

function displayGradingResults(grading) {
    // Create grading results display
    const gradingHTML = `
        <div class="grading-results">
            <div class="score-display">
                <div class="score-circle">
                    <span class="score-percentage">${grading.score_percentage}%</span>
                    <span class="score-category">${grading.score_category}</span>
                </div>
            </div>

            <div class="feedback-sections">
                <div class="feedback-section strengths">
                    <h4>✅ What you did well:</h4>
                    <p>${grading.feedback.strengths}</p>
                </div>

                ${grading.feedback.areas_for_improvement ? `
                <div class="feedback-section improvements">
                    <h4>💡 Areas to improve:</h4>
                    <p>${grading.feedback.areas_for_improvement}</p>
                </div>
                ` : ''}

                ${grading.feedback.suggestions ? `
                <div class="feedback-section suggestions">
                    <h4>📚 Study suggestions:</h4>
                    <p>${grading.feedback.suggestions}</p>
                </div>
                ` : ''}

                <div class="feedback-section encouragement">
                    <h4>🌟 Encouragement:</h4>
                    <p>${grading.feedback.encouragement}</p>
                </div>
            </div>

            <div class="overall-assessment">
                <strong>Overall: ${grading.overall_assessment}</strong>
            </div>

            <div class="grading-actions">
                <button class="btn-secondary" onclick="hideGradingResults()">Continue</button>
                <button class="btn-primary" onclick="nextQuestion()">Next Question</button>
            </div>
        </div>
    `;

    // Insert grading results after the answer section
    const answerSection = document.querySelector('.answer-section');

    // Remove any existing grading results
    const existingResults = document.querySelector('.grading-results');
    if (existingResults) {
        existingResults.remove();
    }

    answerSection.insertAdjacentHTML('afterend', gradingHTML);

    // Scroll to results
    document.querySelector('.grading-results').scrollIntoView({
        behavior: 'smooth',
        block: 'nearest'
    });
}

function hideGradingResults() {
    const gradingResults = document.querySelector('.grading-results');
    if (gradingResults) {
        gradingResults.remove();
    }
}

function nextQuestion() {
    hideGradingResults();

    // Move to next question if available
    if (currentReview.currentIndex < currentReview.questions.length - 1) {
        currentReview.currentIndex++;
        displayCurrentQuestion();
    } else {
        // End of questions
        if (confirm('You\'ve completed all questions! Would you like to end the review session?')) {
            endReviewSession();
        }
    }
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

// Analysis status checking
function checkAnalysisStatus() {
    fetch('/api/analysis-status')
    .then(response => response.json())
    .then(data => {
        const analysisMessage = document.getElementById('analysis-message');
        const analysisStatus = document.getElementById('analysis-status');
        const analyzeBtn = document.getElementById('analyze-confusion');

        if (data.success) {
            if (data.needs_analysis) {
                // Has unanalyzed sessions
                analysisMessage.innerHTML = `
                    📊 Found ${data.unanalyzed_count} unanalyzed conversation sessions out of ${data.total_sessions} total.<br>
                    Click below to analyze them for review questions.
                `;
                analysisStatus.className = 'analysis-status warning';
                analyzeBtn.disabled = false;
                analyzeBtn.style.display = 'block';
            } else if (data.total_conversations > 0) {
                // All analyzed
                analysisMessage.innerHTML = `
                    ✅ All ${data.analyzed_sessions} conversation sessions are analyzed and ready for review!
                `;
                analysisStatus.className = 'analysis-status success';
                analyzeBtn.disabled = true;
                analyzeBtn.style.display = 'none';
            } else {
                // No conversations yet
                analysisMessage.innerHTML = `
                    💬 No conversations found yet. Start chatting to generate review content!
                `;
                analysisStatus.className = 'analysis-status';
                analyzeBtn.disabled = true;
                analyzeBtn.style.display = 'none';
            }
        } else {
            analysisMessage.textContent = 'Error checking analysis status.';
            analysisStatus.className = 'analysis-status warning';
        }
    })
    .catch(error => {
        console.error('Error checking analysis status:', error);
        const analysisMessage = document.getElementById('analysis-message');
        analysisMessage.textContent = 'Error checking analysis status.';
    });
}

// Analysis functionality
function handleAnalysisRequest() {
    const analyzeBtn = document.getElementById('analyze-confusion');
    const analyzeText = document.getElementById('analyze-text');
    const analyzeLoading = document.getElementById('analyze-loading');
    const analysisResults = document.getElementById('analysis-results');

    // Show loading state
    analyzeText.style.display = 'none';
    analyzeLoading.style.display = 'inline';
    analyzeBtn.disabled = true;
    analysisResults.style.display = 'none';

    showStatus('Analyzing your past conversations for confusion points...', 'info');

    fetch('/admin/run-analysis')
    .then(response => response.json())
    .then(data => {
        // Reset button state
        analyzeText.style.display = 'inline';
        analyzeLoading.style.display = 'none';

        if (data.success) {
            showStatus('Analysis complete! New confusion points have been processed.', 'success');

            // Show results
            analysisResults.innerHTML = `
                <div class="success-message">
                    ✅ Successfully analyzed your past conversations!<br>
                    🔄 Refreshing analysis status and course options...
                </div>
            `;
            analysisResults.style.display = 'block';

            // Refresh analysis status and course list
            setTimeout(() => {
                checkAnalysisStatus();
                loadCourses();
                hideStatus();
                analysisResults.style.display = 'none';
            }, 2000);
        } else {
            analyzeBtn.disabled = false;
            showStatus('Analysis failed: ' + data.message, 'error');
            analysisResults.innerHTML = `
                <div class="error-message">
                    ❌ Analysis failed: ${data.message}
                </div>
            `;
            analysisResults.style.display = 'block';
        }
    })
    .catch(error => {
        console.error('Error:', error);

        // Reset button state
        analyzeText.style.display = 'inline';
        analyzeLoading.style.display = 'none';
        analyzeBtn.disabled = false;

        showStatus('Error running analysis.', 'error');
        analysisResults.innerHTML = `
            <div class="error-message">
                ❌ Error running analysis. Please try again.
            </div>
        `;
        analysisResults.style.display = 'block';
    });
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