import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from database import (
    get_session_conversations,
    get_courses,
    save_confusion_analysis,
    check_session_needs_analysis
)
from llm_service import analyze_session_confusion

# Session timeout in seconds (30 minutes)
SESSION_TIMEOUT = 30 * 60

class SessionClassifier:
    """Handles session analysis and confusion detection"""

    def __init__(self):
        self.active_sessions = {}  # Track session activity

    def update_session_activity(self, session_id: str):
        """Update the last activity time for a session"""
        self.active_sessions[session_id] = time.time()

    def get_expired_sessions(self) -> List[str]:
        """Get sessions that have expired (no activity for 30+ minutes)"""
        current_time = time.time()
        expired_sessions = []

        for session_id, last_activity in self.active_sessions.items():
            if current_time - last_activity >= SESSION_TIMEOUT:
                expired_sessions.append(session_id)

        return expired_sessions

    def mark_session_analyzed(self, session_id: str):
        """Remove session from active tracking after analysis"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]

    def analyze_expired_sessions(self):
        """Analyze all expired sessions for confusion points"""
        expired_sessions = self.get_expired_sessions()

        for session_id in expired_sessions:
            try:
                # Check if this session needs analysis
                if check_session_needs_analysis(session_id):
                    print(f"Analyzing expired session: {session_id}")
                    result = self.analyze_single_session(session_id)

                    if result:
                        print(f"Session {session_id} analyzed successfully")
                    else:
                        print(f"Session {session_id} analysis failed or returned no results")

                # Mark as analyzed (remove from active tracking)
                self.mark_session_analyzed(session_id)

            except Exception as e:
                print(f"Error analyzing session {session_id}: {str(e)}")

    def analyze_single_session(self, session_id: str) -> bool:
        """Analyze a single session for course classification and confusion detection"""
        try:
            # Get session conversations
            conversations = get_session_conversations(session_id)

            if not conversations or len(conversations) == 0:
                print(f"No conversations found for session {session_id}")
                return False

            print(f"Analyzing session {session_id} with {len(conversations)} conversations")

            # Get available courses for classification
            courses = get_courses()

            if not courses:
                print("No courses available for classification")
                return False

            # Analyze session using LLM
            analysis_result = analyze_session_confusion(conversations, courses)

            # Save results if we found a course match
            if analysis_result['course_id']:
                save_confusion_analysis(
                    session_id=session_id,
                    course_id=analysis_result['course_id'],
                    unit=analysis_result['unit'],
                    topics=analysis_result['topics'],
                    confused_conversation_ids=analysis_result['confused_conversation_ids']
                )

                print(f"Saved analysis for session {session_id}:")
                print(f"  Course: {analysis_result['course_id']}")
                print(f"  Unit: {analysis_result['unit']}")
                print(f"  Topics: {analysis_result['topics']}")
                print(f"  Confused conversations: {analysis_result['confused_conversation_ids']}")

                return True
            else:
                print(f"No course classification found for session {session_id}")
                # Still save the analysis with null course_id
                save_confusion_analysis(
                    session_id=session_id,
                    course_id=None,
                    unit=None,
                    topics=[],
                    confused_conversation_ids=[]
                )
                return True

        except Exception as e:
            print(f"Error in analyze_single_session: {str(e)}")
            return False

    def force_analyze_session(self, session_id: str) -> Dict:
        """Force analysis of a specific session (for testing/debugging)"""
        try:
            success = self.analyze_single_session(session_id)
            return {
                'success': success,
                'session_id': session_id,
                'message': 'Session analyzed successfully' if success else 'Session analysis failed'
            }
        except Exception as e:
            return {
                'success': False,
                'session_id': session_id,
                'message': f'Error: {str(e)}'
            }

    def get_session_status(self, session_id: str) -> Dict:
        """Get status information about a session"""
        try:
            conversations = get_session_conversations(session_id)
            is_active = session_id in self.active_sessions
            needs_analysis = check_session_needs_analysis(session_id) if conversations else False

            last_activity = None
            if is_active:
                last_activity = datetime.fromtimestamp(self.active_sessions[session_id]).isoformat()

            return {
                'session_id': session_id,
                'is_active': is_active,
                'conversation_count': len(conversations) if conversations else 0,
                'needs_analysis': needs_analysis,
                'last_activity': last_activity
            }

        except Exception as e:
            return {
                'session_id': session_id,
                'error': str(e)
            }

# Global classifier instance
classifier = SessionClassifier()

def update_session_activity(session_id: str):
    """Update session activity (called after each conversation)"""
    classifier.update_session_activity(session_id)

def run_periodic_analysis():
    """Run periodic analysis of expired sessions"""
    print("Running periodic session analysis...")
    classifier.analyze_expired_sessions()
    print("Periodic analysis complete")

def force_analyze_session(session_id: str) -> Dict:
    """Force analyze a specific session"""
    return classifier.force_analyze_session(session_id)

def get_session_status(session_id: str) -> Dict:
    """Get session status"""
    return classifier.get_session_status(session_id)

if __name__ == '__main__':
    # Test the classifier
    print("Testing Session Classifier...")

    # Create a test session for analysis
    from database import save_conversation, get_recent_sessions

    # Get a recent session to test with
    recent_sessions = get_recent_sessions(5)

    if recent_sessions:
        print(f"Found {len(recent_sessions)} recent sessions")

        # Test analyzing the most recent session
        test_session = recent_sessions[0]
        print(f"Testing analysis of session: {test_session}")

        result = force_analyze_session(test_session)
        print(f"Analysis result: {result}")

        # Get session status
        status = get_session_status(test_session)
        print(f"Session status: {status}")
    else:
        print("No recent sessions found to test with")

    print("Testing complete!")