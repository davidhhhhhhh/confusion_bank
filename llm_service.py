import anthropic
import json
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
from prompts import format_prompt

load_dotenv()

# Initialize Anthropic client
client = anthropic.Anthropic()

def chat_with_claude(user_message: str, session_id: str = None) -> str:
    """Handle normal chat conversations with Claude, including session history for context"""
    try:
        # Build conversation history for context
        messages = []

        if session_id:
            from database import get_session_conversations
            # Get recent conversation history (limit to last 10 exchanges to manage token usage)
            session_history = get_session_conversations(session_id)[-10:]

            if session_history:
                # Add system message with context instruction
                system_context = "You are a helpful AI tutor. Below is our recent conversation history for context:"

                # Add conversation history
                history_text = ""
                for conv in session_history:
                    history_text += f"Student: {conv['user_message']}\nAI: {conv['ai_response']}\n\n"

                # Add context as initial message
                messages.append({
                    "role": "user",
                    "content": f"{system_context}\n\n--- Previous Conversation ---\n{history_text}--- Current Question ---\n{user_message}"
                })
            else:
                # No history, just add the current message
                messages.append({
                    "role": "user",
                    "content": user_message
                })
        else:
            # No session ID provided, just respond to current message
            messages.append({
                "role": "user",
                "content": user_message
            })

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=messages
        )

        return response.content[0].text

    except Exception as e:
        print(f"Error in chat_with_claude: {str(e)}")
        return "I'm sorry, I'm having trouble responding right now. Please try again."

def analyze_session_confusion(session_conversations: List[Dict], courses: List[Dict]) -> Dict:
    """Analyze entire session for course/unit/topic classification and confusion detection

    Args:
        session_conversations: List of conversation dicts with 'user_message' and 'ai_response'
        courses: List of available courses with their units/topics structure

    Returns:
        Dict with: {course_id, unit, topics, confused_conversation_ids}
    """
    try:
        # Prepare the conversation text for analysis
        conversation_text = ""
        for i, conv in enumerate(session_conversations):
            conversation_text += f"Conversation {conv['id']}:\n"
            conversation_text += f"Student: {conv['user_message']}\n"
            conversation_text += f"AI: {conv['ai_response']}\n\n"

        # Prepare course structure for the prompt
        course_info = ""
        for course in courses:
            course_info += f"Course {course['id']}: {course['name']}\n"
            for unit in course['units']:
                course_info += f"  Unit: {unit['name']}\n"
                course_info += f"    Topics: {', '.join(unit['topics'])}\n"
            course_info += "\n"

        prompt = format_prompt(
            "session_analysis",
            course_info=course_info,
            conversation_text=conversation_text
        )

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # Parse the JSON response
        response_text = response.content[0].text.strip()

        # Clean up the response to extract just the JSON
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        elif "{" in response_text:
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            response_text = response_text[json_start:json_end]

        analysis_result = json.loads(response_text)

        # Ensure all required fields exist
        result = {
            'course_id': analysis_result.get('course_id'),
            'unit': analysis_result.get('unit'),
            'topics': analysis_result.get('topics', []),
            'confused_conversation_ids': analysis_result.get('confused_conversation_ids', [])
        }

        return result

    except Exception as e:
        print(f"Error in analyze_session_confusion: {str(e)}")
        # Return empty analysis on error
        return {
            'course_id': None,
            'unit': None,
            'topics': [],
            'confused_conversation_ids': []
        }

def parse_review_request(natural_language: str, courses: List[Dict]) -> Dict:
    """Parse natural language review request to course/unit/topics

    Args:
        natural_language: User's request like "I want to review CS101 loops"
        courses: List of available courses

    Returns:
        Dict with: {course_id, unit, topics}
    """
    try:
        # Prepare course structure for the prompt
        course_info = ""
        for course in courses:
            course_info += f"Course {course['id']}: {course['name']}\n"
            for unit in course['units']:
                course_info += f"  Unit: {unit['name']}\n"
                course_info += f"    Topics: {', '.join(unit['topics'])}\n"
            course_info += "\n"

        prompt = format_prompt(
            "review_request_parsing",
            course_info=course_info,
            natural_language=natural_language
        )

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # Parse the JSON response
        response_text = response.content[0].text.strip()

        # Clean up the response to extract just the JSON
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        elif "{" in response_text:
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            response_text = response_text[json_start:json_end]

        parsed_request = json.loads(response_text)

        result = {
            'course_id': parsed_request.get('course_id'),
            'unit': parsed_request.get('unit'),
            'topics': parsed_request.get('topics', [])
        }

        return result

    except Exception as e:
        print(f"Error in parse_review_request: {str(e)}")
        return {
            'course_id': None,
            'unit': None,
            'topics': []
        }

def improve_course_structure_extraction(syllabus_text: str) -> List[Dict]:
    """Use LLM to extract proper course units and topics structure from syllabus text

    This replaces the placeholder function in pdf_processor.py
    """
    try:
        prompt = format_prompt(
            "course_structure_extraction",
            syllabus_text=syllabus_text
        )

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        response_text = response.content[0].text.strip()

        # Clean up the response to extract just the JSON
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        elif "[" in response_text:
            json_start = response_text.find("[")
            json_end = response_text.rfind("]") + 1
            response_text = response_text[json_start:json_end]

        units_structure = json.loads(response_text)

        # Validate structure
        if not isinstance(units_structure, list):
            raise ValueError("Response is not a list")

        for unit in units_structure:
            if not isinstance(unit, dict) or 'name' not in unit or 'topics' not in unit:
                raise ValueError("Invalid unit structure")

        return units_structure

    except Exception as e:
        print(f"Error in improve_course_structure_extraction: {str(e)}")
        # Fallback to basic structure
        return [{"name": "General Course Content", "topics": ["course overview", "key concepts", "assignments"]}]

def generate_review_content(confusion_sessions: List[Dict]) -> Dict:
    """Generate review questions based on confusion session contexts

    Args:
        confusion_sessions: List of session data with conversations and confusion analysis

    Returns:
        Dict with review questions and explanations
    """
    try:
        # Prepare session contexts for analysis
        context_text = ""
        for session in confusion_sessions:
            context_text += f"Session {session['session_id']}:\n"

            if session['confusion_analysis']:
                context_text += f"Topics: {', '.join(session['confusion_analysis']['topics'])}\n"
                context_text += f"Unit: {session['confusion_analysis']['unit']}\n"

            # Include the confused conversations
            for conv in session['conversations']:
                if (session['confusion_analysis'] and
                    conv['id'] in session['confusion_analysis']['confused_conversation_ids']):
                    context_text += f"  Confused about: {conv['user_message']}\n"
                    context_text += f"  Response: {conv['ai_response'][:200]}...\n"

            context_text += "\n"

        prompt = format_prompt(
            "review_generation",
            context_text=context_text
        )

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        response_text = response.content[0].text.strip()

        # Clean up the response to extract just the JSON
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        elif "{" in response_text:
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            response_text = response_text[json_start:json_end]

        review_content = json.loads(response_text)

        return review_content

    except Exception as e:
        print(f"Error in generate_review_content: {str(e)}")
        return {
            "summary": "Unable to generate review content at this time.",
            "questions": [
                {
                    "question": "Please review your course materials and try again later.",
                    "type": "general",
                    "hint": "Check back when the system is available."
                }
            ]
        }

def grade_student_answer(question: str, question_type: str, student_answer: str, hint: str = None) -> Dict:
    """Grade a student's answer to a review question using AI evaluation

    Args:
        question: The review question that was asked
        question_type: Type of question (e.g., "conceptual", "coding", etc.)
        student_answer: The student's response
        hint: Optional hint that was provided with the question

    Returns:
        Dict with grading results including score, feedback, and suggestions
    """
    try:
        prompt = format_prompt(
            "answer_grading",
            question=question,
            question_type=question_type,
            student_answer=student_answer,
            hint=hint if hint else "No hint provided"
        )

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        response_text = response.content[0].text.strip()

        # Clean up the response to extract just the JSON
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        elif "{" in response_text:
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            response_text = response_text[json_start:json_end]

        grading_result = json.loads(response_text)

        # Validate required fields
        required_fields = ['score_percentage', 'score_category', 'feedback', 'overall_assessment']
        for field in required_fields:
            if field not in grading_result:
                raise ValueError(f"Missing required field: {field}")

        # Validate feedback structure
        if not isinstance(grading_result['feedback'], dict):
            raise ValueError("Feedback must be an object")

        feedback_fields = ['strengths', 'areas_for_improvement', 'suggestions', 'encouragement']
        for field in feedback_fields:
            if field not in grading_result['feedback']:
                grading_result['feedback'][field] = ""

        return grading_result

    except Exception as e:
        print(f"Error in grade_student_answer: {str(e)}")
        # Return a fallback grading response
        return {
            "score_percentage": 75,
            "score_category": "Good",
            "feedback": {
                "strengths": "Thank you for providing an answer.",
                "areas_for_improvement": "We encountered an issue evaluating your response.",
                "suggestions": "Please try submitting your answer again.",
                "encouragement": "Keep up the good work! Practice makes perfect."
            },
            "overall_assessment": "Answer submitted successfully"
        }

if __name__ == '__main__':
    # Test the LLM service functions
    print("Testing LLM service functions...")

    # Test basic chat
    print("\n1. Testing basic chat...")
    response = chat_with_claude("Hello, can you explain what a variable is in programming?")
    print(f"Chat response: {response[:100]}...")

    # Test course structure extraction
    print("\n2. Testing course structure extraction...")
    sample_syllabus = """
    CS 101 - Introduction to Programming

    Unit 1: Programming Basics
    This unit covers variables, data types, and basic syntax.

    Unit 2: Control Flow
    Students will learn about if statements, loops, and functions.

    Unit 3: Data Structures
    Introduction to arrays, lists, and dictionaries.
    """

    structure = improve_course_structure_extraction(sample_syllabus)
    print(f"Extracted structure: {json.dumps(structure, indent=2)}")

    print("\nLLM service testing complete!")