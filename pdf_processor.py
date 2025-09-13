import PyPDF2
import json
import io
from typing import Dict, List
from database import save_course
from llm_service import improve_course_structure_extraction

def extract_text_from_pdf(pdf_file) -> str:
    """Extract raw text from uploaded PDF file"""
    try:
        # Reset file pointer to beginning
        pdf_file.seek(0)

        # Create PDF reader object
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        # Extract text from all pages
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() + "\n"

        return text.strip()

    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        return ""

def extract_course_structure(syllabus_text: str) -> List[Dict]:
    """Use LLM to extract course units and topics structure from syllabus text"""
    return improve_course_structure_extraction(syllabus_text)

def save_course_to_db(course_name: str, syllabus_text: str) -> int:
    """Extract course structure and save to database"""
    try:
        # Extract course structure from syllabus
        units_structure = extract_course_structure(syllabus_text)

        # Save to database
        course_id = save_course(course_name, units_structure)

        print(f"Course '{course_name}' saved with ID {course_id}")
        print(f"Extracted {len(units_structure)} units")

        return course_id

    except Exception as e:
        print(f"Error saving course to database: {str(e)}")
        return -1

def process_syllabus_upload(course_name: str, pdf_file) -> Dict:
    """Complete end-to-end syllabus processing"""
    try:
        # Step 1: Extract text from PDF
        print("Extracting text from PDF...")
        syllabus_text = extract_text_from_pdf(pdf_file)

        if not syllabus_text:
            return {
                'success': False,
                'message': 'Failed to extract text from PDF. Please ensure the file is a valid PDF with readable text.'
            }

        print(f"Extracted {len(syllabus_text)} characters from PDF")

        # Step 2: Extract course structure and save to database
        print("Processing course structure...")
        course_id = save_course_to_db(course_name, syllabus_text)

        if course_id < 0:
            return {
                'success': False,
                'message': 'Failed to save course to database.'
            }

        return {
            'success': True,
            'message': f'Successfully processed syllabus for {course_name}',
            'course_id': course_id,
            'text_length': len(syllabus_text)
        }

    except Exception as e:
        return {
            'success': False,
            'message': f'Error processing syllabus: {str(e)}'
        }

if __name__ == '__main__':
    # Test the module
    print("Testing PDF processor module...")

    # Test with sample text
    sample_text = """
    Course: Introduction to Computer Science

    Unit 1: Programming Basics
    - Variables and data types
    - Control structures
    - Functions

    Unit 2: Data Structures
    - Arrays and lists
    - Dictionaries
    - Sets

    Unit 3: Algorithms
    - Sorting algorithms
    - Search algorithms
    - Recursion
    """

    print("Testing course structure extraction...")
    structure = extract_course_structure(sample_text)
    print("Extracted structure:")
    for unit in structure:
        print(f"  {unit['name']}: {unit['topics']}")

    print("\nTesting database save...")
    course_id = save_course_to_db("Test Course", sample_text)
    print(f"Saved course with ID: {course_id}")