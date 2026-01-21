from database import get_db
import logging

logger = logging.getLogger(__name__)

class Subject:
    """Subject model"""
    
    @staticmethod
    def get_all():
        """Get all subjects"""
        db = get_db()
        query = "SELECT * FROM subjects ORDER BY semester, subject_name"
        return db.execute_query(query)
    
    @staticmethod
    def get_by_id(subject_id):
        """Get subject by ID"""
        db = get_db()
        query = "SELECT * FROM subjects WHERE id = %s"
        results = db.execute_query(query, (subject_id,))
        return results[0] if results else None
    
    @staticmethod
    def get_by_semester(semester):
        """Get subjects by semester"""
        db = get_db()
        query = "SELECT * FROM subjects WHERE semester = %s ORDER BY subject_name"
        return db.execute_query(query, (semester,))
    
    @staticmethod
    def create(subject_code, subject_name, semester, department):
        """Create new subject"""
        db = get_db()
        query = """
            INSERT INTO subjects (subject_code, subject_name, semester, department)
            VALUES (%s, %s, %s, %s)
        """
        return db.execute_query(query, (subject_code, subject_name, semester, department), fetch=False)


class Material:
    """Study material model"""
    
    @staticmethod
    def create(subject_id, title, description, file_path, file_type, file_size):
        """Create new material"""
        db = get_db()
        query = """
            INSERT INTO materials (subject_id, title, description, file_path, file_type, file_size)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        return db.execute_query(query, (subject_id, title, description, file_path, file_type, file_size), fetch=False)
    
    @staticmethod
    def get_by_subject(subject_id):
        """Get materials by subject"""
        db = get_db()
        query = """
            SELECT m.*, s.subject_name, s.subject_code
            FROM materials m
            JOIN subjects s ON m.subject_id = s.id
            WHERE m.subject_id = %s
            ORDER BY m.upload_date DESC
        """
        return db.execute_query(query, (subject_id,))
    
    @staticmethod
    def get_all():
        """Get all materials"""
        db = get_db()
        query = """
            SELECT m.*, s.subject_name, s.subject_code
            FROM materials m
            JOIN subjects s ON m.subject_id = s.id
            ORDER BY m.upload_date DESC
        """
        return db.execute_query(query)
    
    @staticmethod
    def mark_processed(material_id):
        """Mark material as processed"""
        db = get_db()
        query = "UPDATE materials SET is_processed = TRUE WHERE id = %s"
        db.execute_query(query, (material_id,), fetch=False)
    
    @staticmethod
    def get_by_id(material_id):
        """Get material by ID"""
        db = get_db()
        query = "SELECT * FROM materials WHERE id = %s"
        results = db.execute_query(query, (material_id,))
        return results[0] if results else None


class Syllabus:
    """Syllabus model"""
    
    @staticmethod
    def create(subject_id, unit_number, unit_name, topics, learning_outcomes):
        """Create syllabus entry"""
        db = get_db()
        query = """
            INSERT INTO syllabus (subject_id, unit_number, unit_name, topics, learning_outcomes)
            VALUES (%s, %s, %s, %s, %s)
        """
        return db.execute_query(query, (subject_id, unit_number, unit_name, topics, learning_outcomes), fetch=False)
    
    @staticmethod
    def get_by_subject(subject_id):
        """Get syllabus by subject"""
        db = get_db()
        query = """
            SELECT sy.*, s.subject_name, s.subject_code
            FROM syllabus sy
            JOIN subjects s ON sy.subject_id = s.id
            WHERE sy.subject_id = %s
            ORDER BY sy.unit_number
        """
        return db.execute_query(query, (subject_id,))
    
    @staticmethod
    def update(syllabus_id, unit_name, topics, learning_outcomes):
        """Update syllabus entry"""
        db = get_db()
        query = """
            UPDATE syllabus 
            SET unit_name = %s, topics = %s, learning_outcomes = %s
            WHERE id = %s
        """
        db.execute_query(query, (unit_name, topics, learning_outcomes, syllabus_id), fetch=False)


class ImportantQuestion:
    """Important questions model"""
    
    @staticmethod
    def create(subject_id, question, answer, question_type, difficulty, unit_number):
        """Create important question"""
        db = get_db()
        query = """
            INSERT INTO important_questions 
            (subject_id, question, answer, question_type, difficulty, unit_number)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        return db.execute_query(query, (subject_id, question, answer, question_type, difficulty, unit_number), fetch=False)
    
    @staticmethod
    def get_by_subject(subject_id, question_type=None):
        """Get important questions by subject"""
        db = get_db()
        if question_type:
            query = """
                SELECT iq.*, s.subject_name, s.subject_code
                FROM important_questions iq
                JOIN subjects s ON iq.subject_id = s.id
                WHERE iq.subject_id = %s AND iq.question_type = %s
                ORDER BY iq.unit_number, iq.difficulty
            """
            return db.execute_query(query, (subject_id, question_type))
        else:
            query = """
                SELECT iq.*, s.subject_name, s.subject_code
                FROM important_questions iq
                JOIN subjects s ON iq.subject_id = s.id
                WHERE iq.subject_id = %s
                ORDER BY iq.unit_number, iq.difficulty
            """
            return db.execute_query(query, (subject_id,))
    
    @staticmethod
    def get_all():
        """Get all important questions"""
        db = get_db()
        query = """
            SELECT iq.*, s.subject_name, s.subject_code
            FROM important_questions iq
            JOIN subjects s ON iq.subject_id = s.id
            ORDER BY s.subject_name, iq.unit_number
        """
        return db.execute_query(query)


class ChatHistory:
    """Chat history model"""
    
    @staticmethod
    def create(session_id, user_message, bot_response, context_used):
        """Save chat message"""
        db = get_db()
        query = """
            INSERT INTO chat_history (session_id, user_message, bot_response, context_used)
            VALUES (%s, %s, %s, %s)
        """
        return db.execute_query(query, (session_id, user_message, bot_response, context_used), fetch=False)
    
    @staticmethod
    def get_by_session(session_id, limit=50):
        """Get chat history by session"""
        db = get_db()
        query = """
            SELECT * FROM chat_history
            WHERE session_id = %s
            ORDER BY timestamp DESC
            LIMIT %s
        """
        return db.execute_query(query, (session_id, limit))


class ExtractedImage:
    """Extracted images model"""
    
    @staticmethod
    def create(material_id, image_path, page_number, image_type, caption):
        """Save extracted image"""
        db = get_db()
        query = """
            INSERT INTO extracted_images (material_id, image_path, page_number, image_type, caption)
            VALUES (%s, %s, %s, %s, %s)
        """
        return db.execute_query(query, (material_id, image_path, page_number, image_type, caption), fetch=False)
    
    @staticmethod
    def get_by_material(material_id):
        """Get images by material"""
        db = get_db()
        query = """
            SELECT * FROM extracted_images
            WHERE material_id = %s
            ORDER BY page_number
        """
        return db.execute_query(query, (material_id,))
