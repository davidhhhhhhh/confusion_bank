import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

DATABASE_PATH = 'confusion_bank.db'

def init_database():
    """Initialize SQLite database with tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Create courses table - stores syllabus structure
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        units TEXT NOT NULL,    -- JSON: [{"name": "Unit 1", "topics": ["topic1", "topic2"]}]
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create conversations table - individual user-AI message pairs
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,  -- Groups related conversations
        user_message TEXT NOT NULL,
        ai_response TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create confusion points table - analysis results per session
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS confusion_points (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        course_id INTEGER REFERENCES courses(id),
        unit TEXT,
        topics TEXT,  -- JSON array of identified topics
        confused_conversation_ids TEXT,  -- JSON array of conversation IDs showing confusion
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully")

# Course functions
def save_course(course_name: str, units_structure: List[Dict]) -> int:
    """Save course structure to database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO courses (name, units)
    VALUES (?, ?)
    ''', (course_name, json.dumps(units_structure)))

    course_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return course_id

def get_courses() -> List[Dict]:
    """Get all courses"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT id, name, units, created_at FROM courses')
    rows = cursor.fetchall()

    courses = []
    for row in rows:
        courses.append({
            'id': row[0],
            'name': row[1],
            'units': json.loads(row[2]),
            'created_at': row[3]
        })

    conn.close()
    return courses

def get_course_by_id(course_id: int) -> Optional[Dict]:
    """Get course by ID"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT id, name, units, created_at FROM courses WHERE id = ?', (course_id,))
    row = cursor.fetchone()

    if row:
        course = {
            'id': row[0],
            'name': row[1],
            'units': json.loads(row[2]),
            'created_at': row[3]
        }
    else:
        course = None

    conn.close()
    return course

# Conversation functions
def save_conversation(session_id: str, user_message: str, ai_response: str) -> int:
    """Save conversation pair to database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO conversations (session_id, user_message, ai_response)
    VALUES (?, ?, ?)
    ''', (session_id, user_message, ai_response))

    conversation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return conversation_id

def get_session_conversations(session_id: str) -> List[Dict]:
    """Get all conversations for a session"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, user_message, ai_response, created_at
    FROM conversations
    WHERE session_id = ?
    ORDER BY created_at ASC
    ''', (session_id,))

    rows = cursor.fetchall()
    conversations = []
    for row in rows:
        conversations.append({
            'id': row[0],
            'user_message': row[1],
            'ai_response': row[2],
            'created_at': row[3]
        })

    conn.close()
    return conversations

def get_recent_sessions(limit: int = 10) -> List[str]:
    """Get recent unique session IDs"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT session_id
    FROM conversations
    GROUP BY session_id
    ORDER BY MAX(created_at) DESC
    LIMIT ?
    ''', (limit,))

    rows = cursor.fetchall()
    sessions = [row[0] for row in rows]

    conn.close()
    return sessions

def check_session_needs_analysis(session_id: str) -> bool:
    """Check if session needs confusion analysis"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Check if this session already has confusion analysis
    cursor.execute('SELECT id FROM confusion_points WHERE session_id = ?', (session_id,))
    existing = cursor.fetchone()

    conn.close()
    return existing is None

def get_unanalyzed_sessions() -> List[str]:
    """Get all session IDs that have conversations but no confusion analysis"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT DISTINCT c.session_id
    FROM conversations c
    LEFT JOIN confusion_points cp ON c.session_id = cp.session_id
    WHERE cp.session_id IS NULL
    GROUP BY c.session_id
    ORDER BY MAX(c.created_at) DESC
    ''')

    rows = cursor.fetchall()
    sessions = [row[0] for row in rows]

    conn.close()
    return sessions

# Confusion analysis functions
def save_confusion_analysis(session_id: str, course_id: int, unit: str, topics: List[str], confused_conversation_ids: List[int]):
    """Save confusion analysis results"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO confusion_points (session_id, course_id, unit, topics, confused_conversation_ids)
    VALUES (?, ?, ?, ?, ?)
    ''', (session_id, course_id, unit, json.dumps(topics), json.dumps(confused_conversation_ids)))

    conn.commit()
    conn.close()

def get_confusion_sessions(course_id: int = None, unit: str = None, topics: List[str] = None) -> List[str]:
    """Get session IDs matching review criteria"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    query = 'SELECT DISTINCT session_id FROM confusion_points WHERE 1=1'
    params = []

    if course_id:
        query += ' AND course_id = ?'
        params.append(course_id)

    if unit:
        query += ' AND unit = ?'
        params.append(unit)

    if topics:
        # For topics, we need to check JSON contains any of the specified topics
        topic_conditions = []
        for topic in topics:
            topic_conditions.append('topics LIKE ?')
            params.append(f'%"{topic}"%')

        if topic_conditions:
            query += ' AND (' + ' OR '.join(topic_conditions) + ')'

    query += ' ORDER BY created_at DESC'

    cursor.execute(query, params)
    rows = cursor.fetchall()
    sessions = [row[0] for row in rows]

    conn.close()
    return sessions

def get_confusion_points_for_session(session_id: str) -> Optional[Dict]:
    """Get confusion analysis for a specific session"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT course_id, unit, topics, confused_conversation_ids, created_at
    FROM confusion_points
    WHERE session_id = ?
    ''', (session_id,))

    row = cursor.fetchone()
    if row:
        result = {
            'course_id': row[0],
            'unit': row[1],
            'topics': json.loads(row[2]),
            'confused_conversation_ids': json.loads(row[3]),
            'created_at': row[4]
        }
    else:
        result = None

    conn.close()
    return result

# Utility functions
def get_all_session_data(session_ids: List[str]) -> List[Dict]:
    """Get complete session data (conversations + confusion analysis) for multiple sessions"""
    session_data = []

    for session_id in session_ids:
        conversations = get_session_conversations(session_id)
        confusion_analysis = get_confusion_points_for_session(session_id)

        session_data.append({
            'session_id': session_id,
            'conversations': conversations,
            'confusion_analysis': confusion_analysis
        })

    return session_data

def cleanup_old_data(days_old: int = 30):
    """Clean up old conversations and confusion points (optional utility)"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    DELETE FROM conversations
    WHERE created_at < datetime('now', '-{} days')
    '''.format(days_old))

    cursor.execute('''
    DELETE FROM confusion_points
    WHERE created_at < datetime('now', '-{} days')
    '''.format(days_old))

    conn.commit()
    conn.close()

def reset_database():
    """Reset database to clean state - remove all data but keep structure"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Clear all data from tables in reverse dependency order
    cursor.execute('DELETE FROM confusion_points')
    cursor.execute('DELETE FROM conversations')
    cursor.execute('DELETE FROM courses')

    # Reset auto-increment counters
    cursor.execute('DELETE FROM sqlite_sequence WHERE name="confusion_points"')
    cursor.execute('DELETE FROM sqlite_sequence WHERE name="conversations"')
    cursor.execute('DELETE FROM sqlite_sequence WHERE name="courses"')

    conn.commit()
    conn.close()
    print("Database reset complete - all data cleared")

def get_database_stats():
    """Get current database statistics"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    stats = {}

    cursor.execute('SELECT COUNT(*) FROM courses')
    stats['courses'] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM conversations')
    stats['conversations'] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(DISTINCT session_id) FROM conversations')
    stats['sessions'] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM confusion_points')
    stats['analyzed_sessions'] = cursor.fetchone()[0]

    conn.close()
    return stats

if __name__ == '__main__':
    # Reset database to clean state
    print("Resetting database...")
    # reset_database()

    # # Initialize fresh database
    # init_database()

    # # Show stats
    # stats = get_database_stats()
    # print(f"Database reset complete. Current stats: {stats}")