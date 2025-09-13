import os
from typing import Dict

PROMPTS_DIR = os.path.dirname(__file__)

def load_prompt(prompt_name: str) -> str:
    """Load a prompt template from file"""
    prompt_file = os.path.join(PROMPTS_DIR, f"{prompt_name}.txt")

    if not os.path.exists(prompt_file):
        raise FileNotFoundError(f"Prompt template not found: {prompt_name}.txt")

    with open(prompt_file, 'r', encoding='utf-8') as f:
        return f.read().strip()

def format_prompt(prompt_name: str, **kwargs) -> str:
    """Load and format a prompt template with provided variables"""
    template = load_prompt(prompt_name)
    return template.format(**kwargs)

# Available prompt templates
AVAILABLE_PROMPTS = [
    "session_analysis",
    "review_request_parsing",
    "course_structure_extraction",
    "review_generation"
]