from typing import List, Dict, Optional
from database import (
    get_confusion_sessions,
    get_all_session_data,
    get_course_by_id,
    get_courses
)
from llm_service import generate_review_content, parse_review_request

class ReviewGenerator:
    """Handles review content generation based on confusion analysis"""

    def generate_review_from_request(self, natural_language_request: str) -> Dict:
        """Generate review content from natural language request

        Args:
            natural_language_request: User request like "I want to review CS101 loops"

        Returns:
            Dict with review content or error message
        """
        try:
            # Step 1: Parse the natural language request
            courses = get_courses()
            parsed_request = parse_review_request(natural_language_request, courses)

            if not parsed_request['course_id']:
                return {
                    'success': False,
                    'message': 'Could not understand which course you want to review. Please specify a course name or topic.'
                }

            print(f"Parsed request: {parsed_request}")

            # Step 2: Get confusion sessions matching the criteria
            confusion_session_ids = get_confusion_sessions(
                course_id=parsed_request['course_id'],
                unit=parsed_request['unit'],
                topics=parsed_request['topics']
            )

            if not confusion_session_ids:
                return {
                    'success': False,
                    'message': 'No confusion points found for the requested topic. Try having some conversations first!'
                }

            print(f"Found {len(confusion_session_ids)} relevant confusion sessions")

            # Step 3: Get complete session data for review generation
            session_data = get_all_session_data(confusion_session_ids)

            # Step 4: Generate review content using LLM
            review_content = generate_review_content(session_data)

            return {
                'success': True,
                'content': review_content,
                'metadata': {
                    'course_id': parsed_request['course_id'],
                    'unit': parsed_request['unit'],
                    'topics': parsed_request['topics'],
                    'session_count': len(confusion_session_ids)
                }
            }

        except Exception as e:
            print(f"Error in generate_review_from_request: {str(e)}")
            return {
                'success': False,
                'message': f'Error generating review: {str(e)}'
            }

    def generate_review_by_criteria(self, course_id: int, unit: str = None, topics: List[str] = None) -> Dict:
        """Generate review content by specific criteria

        Args:
            course_id: ID of the course
            unit: Specific unit name (optional)
            topics: List of specific topics (optional)

        Returns:
            Dict with review content or error message
        """
        try:
            # Validate course exists
            course = get_course_by_id(course_id)
            if not course:
                return {
                    'success': False,
                    'message': f'Course with ID {course_id} not found'
                }

            print(f"Generating review for course: {course['name']}")

            # Get confusion sessions matching the criteria
            confusion_session_ids = get_confusion_sessions(
                course_id=course_id,
                unit=unit,
                topics=topics
            )

            if not confusion_session_ids:
                course_name = course['name']
                topic_info = f" on {', '.join(topics)}" if topics else ""
                unit_info = f" in {unit}" if unit else ""

                return {
                    'success': False,
                    'message': f'No confusion points found for {course_name}{unit_info}{topic_info}. Try having some conversations about this topic first!'
                }

            print(f"Found {len(confusion_session_ids)} relevant confusion sessions")

            # Get complete session data for review generation
            session_data = get_all_session_data(confusion_session_ids)

            # Generate review content using LLM
            review_content = generate_review_content(session_data)

            return {
                'success': True,
                'content': review_content,
                'metadata': {
                    'course_id': course_id,
                    'course_name': course['name'],
                    'unit': unit,
                    'topics': topics,
                    'session_count': len(confusion_session_ids)
                }
            }

        except Exception as e:
            print(f"Error in generate_review_by_criteria: {str(e)}")
            return {
                'success': False,
                'message': f'Error generating review: {str(e)}'
            }

    def get_available_review_topics(self, course_id: int) -> Dict:
        """Get available topics for review based on confusion analysis

        Args:
            course_id: ID of the course

        Returns:
            Dict with available units and topics that have confusion points
        """
        try:
            # Validate course exists
            course = get_course_by_id(course_id)
            if not course:
                return {
                    'success': False,
                    'message': f'Course with ID {course_id} not found'
                }

            # Get all confusion sessions for this course
            confusion_session_ids = get_confusion_sessions(course_id=course_id)

            if not confusion_session_ids:
                return {
                    'success': True,
                    'course_name': course['name'],
                    'available_units': [],
                    'available_topics': [],
                    'message': 'No confusion points found for this course yet.'
                }

            # Get session data to analyze available topics
            session_data = get_all_session_data(confusion_session_ids)

            # Extract unique units and topics from confusion analysis
            available_units = set()
            available_topics = set()

            for session in session_data:
                if session['confusion_analysis']:
                    analysis = session['confusion_analysis']
                    if analysis['unit']:
                        available_units.add(analysis['unit'])
                    if analysis['topics']:
                        available_topics.update(analysis['topics'])

            return {
                'success': True,
                'course_name': course['name'],
                'available_units': sorted(list(available_units)),
                'available_topics': sorted(list(available_topics)),
                'session_count': len(confusion_session_ids)
            }

        except Exception as e:
            print(f"Error in get_available_review_topics: {str(e)}")
            return {
                'success': False,
                'message': f'Error getting available topics: {str(e)}'
            }

    def generate_review_summary(self, course_id: int, unit: str = None, topics: List[str] = None) -> Dict:
        """Generate a summary of confusion points for review planning

        Args:
            course_id: ID of the course
            unit: Specific unit name (optional)
            topics: List of specific topics (optional)

        Returns:
            Dict with confusion summary
        """
        try:
            # Get confusion sessions matching the criteria
            confusion_session_ids = get_confusion_sessions(
                course_id=course_id,
                unit=unit,
                topics=topics
            )

            if not confusion_session_ids:
                return {
                    'success': True,
                    'summary': 'No confusion points found for the specified criteria.',
                    'session_count': 0,
                    'confusion_count': 0
                }

            # Get complete session data
            session_data = get_all_session_data(confusion_session_ids)

            # Count total confusion points
            total_confused_conversations = 0
            confusion_topics = set()
            confusion_units = set()

            for session in session_data:
                if session['confusion_analysis']:
                    analysis = session['confusion_analysis']
                    confused_ids = analysis['confused_conversation_ids']
                    total_confused_conversations += len(confused_ids)

                    if analysis['topics']:
                        confusion_topics.update(analysis['topics'])
                    if analysis['unit']:
                        confusion_units.add(analysis['unit'])

            return {
                'success': True,
                'summary': f'Found {total_confused_conversations} confusion points across {len(confusion_session_ids)} sessions.',
                'session_count': len(confusion_session_ids),
                'confusion_count': total_confused_conversations,
                'topics_with_confusion': sorted(list(confusion_topics)),
                'units_with_confusion': sorted(list(confusion_units))
            }

        except Exception as e:
            print(f"Error in generate_review_summary: {str(e)}")
            return {
                'success': False,
                'message': f'Error generating summary: {str(e)}'
            }

# Global review generator instance
review_generator = ReviewGenerator()

# Convenience functions
def generate_review_from_request(natural_language_request: str) -> Dict:
    """Generate review from natural language request"""
    return review_generator.generate_review_from_request(natural_language_request)

def generate_review_by_criteria(course_id: int, unit: str = None, topics: List[str] = None) -> Dict:
    """Generate review by specific criteria"""
    return review_generator.generate_review_by_criteria(course_id, unit, topics)

def get_available_review_topics(course_id: int) -> Dict:
    """Get available review topics for a course"""
    return review_generator.get_available_review_topics(course_id)

def generate_review_summary(course_id: int, unit: str = None, topics: List[str] = None) -> Dict:
    """Generate confusion summary"""
    return review_generator.generate_review_summary(course_id, unit, topics)

if __name__ == '__main__':
    # Test the review generator
    print("Testing Review Generator...")

    # Test 1: Get available review topics for course 4 (Data Mining)
    print("\n1. Testing available review topics...")
    available = get_available_review_topics(4)
    print(f"Available topics result: {available}")

    # Test 2: Generate review summary
    print("\n2. Testing review summary...")
    summary = generate_review_summary(4)
    print(f"Summary result: {summary}")

    # Test 3: Generate review by criteria
    if available['success'] and available['available_topics']:
        print("\n3. Testing review generation by criteria...")
        first_topic = available['available_topics'][0]
        review = generate_review_by_criteria(4, topics=[first_topic])
        print(f"Review generation result: {review['success']}")
        if review['success']:
            print(f"Generated {len(review['content']['questions'])} questions")

    # Test 4: Natural language review request
    print("\n4. Testing natural language review request...")
    nl_review = generate_review_from_request("I want to review neural networks")
    print(f"Natural language review result: {nl_review['success']}")
    if nl_review['success']:
        print(f"Generated review with {len(nl_review['content']['questions'])} questions")

    print("\nTesting complete!")