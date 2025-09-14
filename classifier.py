from typing import List, Dict, Optional
from database import (
    get_session_conversations,
    get_courses,
    save_confusion_analysis,
    get_unanalyzed_sessions
)
from llm_service import analyze_session_confusion

class SessionClassifier:
    """Handles session analysis and confusion detection"""

    def __init__(self):
        pass

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
            from database import check_session_needs_analysis
            needs_analysis = check_session_needs_analysis(session_id) if conversations else False

            return {
                'session_id': session_id,
                'conversation_count': len(conversations) if conversations else 0,
                'needs_analysis': needs_analysis
            }

        except Exception as e:
            return {
                'session_id': session_id,
                'error': str(e)
            }

# Global classifier instance
classifier = SessionClassifier()


def run_periodic_analysis():
    """Run analysis of all unanalyzed sessions (user-triggered)"""
    print("Running analysis of unanalyzed sessions...")

    # Get all sessions that need analysis
    unanalyzed_sessions = get_unanalyzed_sessions()
    print(f"Found {len(unanalyzed_sessions)} sessions that need analysis")

    analyzed_count = 0
    failed_count = 0

    for session_id in unanalyzed_sessions:
        try:
            print(f"Analyzing session: {session_id}")
            result = classifier.analyze_single_session(session_id)

            if result:
                analyzed_count += 1
                print(f"Session {session_id} analyzed successfully")
            else:
                failed_count += 1
                print(f"Session {session_id} analysis failed or returned no results")

        except Exception as e:
            failed_count += 1
            print(f"Error analyzing session {session_id}: {str(e)}")

    print(f"Analysis complete - {analyzed_count} successful, {failed_count} failed")
    return analyzed_count, failed_count

def force_analyze_session(session_id: str) -> Dict:
    """Force analyze a specific session"""
    return classifier.force_analyze_session(session_id)

def get_session_status(session_id: str) -> Dict:
    """Get session status"""
    return classifier.get_session_status(session_id)

if __name__ == '__main__':
    # Test the classifier
    print("Testing Session Classifier...")

    # Test the new unanalyzed sessions approach
    from database import get_recent_sessions

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