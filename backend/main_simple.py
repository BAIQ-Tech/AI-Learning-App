from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import sqlite3
from datetime import datetime
import json

app = FastAPI(title="AI-Learning API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Language configurations
SUPPORTED_LANGUAGES = {
    "en": {"name": "English", "native": "English"},
    "ja": {"name": "Japanese", "native": "日本語"},
    "zh": {"name": "Chinese", "native": "中文"},
    "es": {"name": "Spanish", "native": "Español"},
    "el": {"name": "Greek", "native": "Ελληνικά"},
    "he": {"name": "Hebrew", "native": "עברית"}
}

# Database initialization
def init_db():
    conn = sqlite3.connect('ai_learning.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # User progress table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            language_code TEXT,
            lesson_id TEXT,
            score INTEGER,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Conversations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            language_code TEXT,
            messages TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Pydantic models
class TranslationRequest(BaseModel):
    text: str
    source_language: str
    target_language: str

class ConversationRequest(BaseModel):
    message: str
    language_code: str
    user_id: Optional[int] = None

class LessonRequest(BaseModel):
    language_code: str
    level: str
    topic: Optional[str] = None

class User(BaseModel):
    username: str
    email: str

# Mock responses for demo purposes
MOCK_TRANSLATIONS = {
    ("Hello", "en", "ja"): "こんにちは",
    ("Hello", "en", "zh"): "你好",
    ("Hello", "en", "es"): "Hola",
    ("Hello", "en", "el"): "Γεια σας",
    ("Hello", "en", "he"): "שלום",
}

MOCK_LESSONS = {
    "en": {
        "title": "English Basics",
        "level": "beginner",
        "vocabulary": [
            {"word": "Hello", "translation": "Greeting", "pronunciation": "/həˈloʊ/"},
            {"word": "Thank you", "translation": "Expression of gratitude", "pronunciation": "/θæŋk juː/"},
            {"word": "Please", "translation": "Polite request", "pronunciation": "/pliːz/"},
        ],
        "examples": ["Hello, how are you?", "Thank you very much!"],
        "grammar": {"point": "Present Simple", "explanation": "Used for general facts and habits"},
        "exercises": [
            {"type": "translate", "question": "Translate: Hello", "answer": "Hello"},
            {"type": "multiple-choice", "question": "What is a greeting?", "options": ["Hello", "Goodbye", "Maybe"], "answer": "Hello"}
        ]
    },
    "ja": {
        "title": "Japanese Basics - 日本語の基礎",
        "level": "beginner",
        "vocabulary": [
            {"word": "こんにちは", "translation": "Hello", "pronunciation": "konnichiwa"},
            {"word": "ありがとう", "translation": "Thank you", "pronunciation": "arigatou"},
            {"word": "すみません", "translation": "Excuse me", "pronunciation": "sumimasen"},
        ],
        "examples": ["こんにちは、元気ですか？", "ありがとうございます！"],
        "grammar": {"point": "Politeness Levels", "explanation": "Japanese has different levels of politeness"},
        "exercises": [
            {"type": "translate", "question": "Translate: Hello", "answer": "こんにちは"},
            {"type": "multiple-choice", "question": "How do you say thank you?", "options": ["こんにちは", "ありがとう", "すみません"], "answer": "ありがとう"}
        ]
    }
}

# Routes
@app.get("/")
async def root():
    return {"message": "AI-Learning API is running"}

@app.get("/languages")
async def get_supported_languages():
    return {"languages": SUPPORTED_LANGUAGES}

@app.post("/translate")
async def translate_text(request: TranslationRequest):
    # Mock translation for demo
    key = (request.text, request.source_language, request.target_language)
    translation = MOCK_TRANSLATIONS.get(key, f"[Mock translation of '{request.text}' to {request.target_language}]")
    
    return {
        "original_text": request.text,
        "translated_text": translation,
        "source_language": request.source_language,
        "target_language": request.target_language
    }

@app.post("/conversation")
async def ai_conversation(request: ConversationRequest):
    # Mock AI response for demo
    language_info = SUPPORTED_LANGUAGES.get(request.language_code, {})
    language_name = language_info.get('name', request.language_code)
    
    mock_responses = {
        "en": f"Hello! I'm your AI tutor for {language_name}. How can I help you today?",
        "ja": "こんにちは！日本語の勉強を手伝います。何か質問はありますか？",
        "zh": "你好！我是你的中文老师。有什么可以帮助你的吗？",
        "es": "¡Hola! Soy tu tutor de español. ¿En qué puedo ayudarte?",
        "el": "Γεια σας! Είμαι ο δάσκαλός σας για τα ελληνικά. Πώς μπορώ να βοηθήσω;",
        "he": "שלום! אני המורה שלך לעברית. איך אני יכול לעזור?"
    }
    
    ai_response = mock_responses.get(request.language_code, "Hello! I'm your AI language tutor.")
    
    return {
        "user_message": request.message,
        "ai_response": ai_response,
        "language_code": request.language_code
    }

@app.post("/lesson")
async def generate_lesson(request: LessonRequest):
    # Return mock lesson for demo
    lesson = MOCK_LESSONS.get(request.language_code, MOCK_LESSONS["en"])
    lesson["level"] = request.level
    return lesson

@app.post("/users")
async def create_user(user: User):
    try:
        conn = sqlite3.connect('ai_learning.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email) VALUES (?, ?)",
            (user.username, user.email)
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {"user_id": user_id, "username": user.username, "email": user.email}
    
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User creation failed: {str(e)}")

@app.get("/users/{user_id}/progress")
async def get_user_progress(user_id: int):
    try:
        conn = sqlite3.connect('ai_learning.db')
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT language_code, lesson_id, score, completed_at 
            FROM user_progress 
            WHERE user_id = ? 
            ORDER BY completed_at DESC
            """,
            (user_id,)
        )
        progress = cursor.fetchall()
        conn.close()
        
        return {
            "user_id": user_id,
            "progress": [
                {
                    "language_code": row[0],
                    "lesson_id": row[1],
                    "score": row[2],
                    "completed_at": row[3]
                }
                for row in progress
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get progress: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
