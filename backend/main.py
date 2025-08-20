from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
import os
from openai import OpenAI
import base64
import tempfile
import jwt
import hashlib
from datetime import datetime, timedelta
import secrets
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="AI-Learning API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 168  # 7 days

# Security
security = HTTPBearer()

# Language configurations
SUPPORTED_LANGUAGES = {
    "en": {"code": "en", "name": "English", "native": "English", "nativeName": "English"},
    "ja": {"code": "ja", "name": "Japanese", "native": "日本語", "nativeName": "日本語"},
    "zh": {"code": "zh", "name": "Chinese", "native": "中文", "nativeName": "中文"},
    "es": {"code": "es", "name": "Spanish", "native": "Español", "nativeName": "Español"},
    "el": {"code": "el", "name": "Greek", "native": "Ελληνικά", "nativeName": "Ελληνικά"},
    "he": {"code": "he", "name": "Hebrew", "native": "עברית", "nativeName": "עברית"},
    "de": {"code": "de", "name": "German", "native": "Deutsch", "nativeName": "Deutsch"},
    "fr": {"code": "fr", "name": "French", "native": "Français", "nativeName": "Français"},
    "it": {"code": "it", "name": "Italian", "native": "Italiano", "nativeName": "Italiano"}
}

# Database initialization
def init_db():
    conn = sqlite3.connect('language_learning.db')
    cursor = conn.cursor()
    
    # Create users table with authentication fields
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            email TEXT,
            password_hash TEXT,
            name TEXT NOT NULL,
            avatar TEXT,
            auth_method TEXT NOT NULL,
            wallet_address TEXT,
            social_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Create unique indexes for partial uniqueness
    cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email) WHERE email IS NOT NULL')
    cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_users_wallet ON users(wallet_address) WHERE wallet_address IS NOT NULL')
    cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_users_social ON users(social_id, auth_method) WHERE social_id IS NOT NULL')
    
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

# Initialize database
init_db()

# Authentication Helper Functions
def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return hash_password(password) == hashed

def create_jwt_token(user_id: int) -> str:
    """Create a JWT token for a user"""
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get the current authenticated user"""
    token = credentials.credentials
    payload = verify_jwt_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired. Please sign in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    conn = sqlite3.connect('language_learning.db')
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, name, email, auth_method, wallet_address, avatar FROM users WHERE id = ?",
        (payload["user_id"],)
    )
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return {
        "id": user[0],
        "name": user[1],
        "email": user[2],
        "auth_method": user[3],
        "wallet_address": user[4],
        "avatar": user[5]
    }

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
    level: str  # beginner, intermediate, advanced
    topic: Optional[str] = None

class UserProgress(BaseModel):
    user_id: int
    progress: List[dict]

# Authentication Models
class EmailLoginRequest(BaseModel):
    email: str
    password: str

class UserRegistrationRequest(BaseModel):
    email: str
    password: str
    name: str

class AuthResponse(BaseModel):
    token: str
    user: dict

class WalletLoginRequest(BaseModel):
    wallet_address: str
    signature: str
    message: str
    wallet_type: str  # 'metamask', 'coinbase', 'phantom'

class SocialLoginRequest(BaseModel):
    provider: str  # 'google', 'apple'
    token: str
    user_info: dict

class VoiceConversationRequest(BaseModel):
    audio_data: str  # base64 encoded audio
    language_code: str
    user_id: Optional[int] = None

class GameRequest(BaseModel):
    game_type: str  # "vocabulary_quiz", "pronunciation_practice", "word_match"
    language_code: str
    difficulty: str  # "easy", "medium", "hard"
    topic: Optional[str] = None

class PronunciationRequest(BaseModel):
    text: str
    language_code: str
    audio_data: str  # base64 encoded audio

# Routes
@app.get("/")
async def root():
    return {"message": "AI-Learning API is running"}

# Authentication Endpoints
@app.post("/api/auth/register", response_model=AuthResponse)
async def register_user(request: UserRegistrationRequest):
    """Register a new user with email and password"""
    conn = sqlite3.connect('language_learning.db')
    cursor = conn.cursor()
    
    # Check if user already exists
    cursor.execute("SELECT id FROM users WHERE email = ?", (request.email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create new user
    password_hash = hash_password(request.password)
    cursor.execute(
        "INSERT INTO users (email, password_hash, name, auth_method) VALUES (?, ?, ?, ?)",
        (request.email, password_hash, request.name, "email")
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Create JWT token
    token = create_jwt_token(user_id)
    
    return AuthResponse(
        token=token,
        user={
            "id": user_id,
            "email": request.email,
            "name": request.name,
            "auth_method": "email"
        }
    )

@app.post("/api/auth/email", response_model=AuthResponse)
async def login_with_email(request: EmailLoginRequest):
    """Login with email and password"""
    conn = sqlite3.connect('language_learning.db')
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, password_hash, name, email FROM users WHERE email = ? AND auth_method = ?",
        (request.email, "email")
    )
    user = cursor.fetchone()
    
    if not user or not verify_password(request.password, user[1]):
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Update last login
    cursor.execute(
        "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
        (user[0],)
    )
    conn.commit()
    conn.close()
    
    # Create JWT token
    token = create_jwt_token(user[0])
    
    return AuthResponse(
        token=token,
        user={
            "id": user[0],
            "email": user[3],
            "name": user[2],
            "auth_method": "email"
        }
    )

@app.post("/api/auth/wallet", response_model=AuthResponse)
async def login_with_wallet(request: WalletLoginRequest):
    """Login with Web3 wallet"""
    conn = sqlite3.connect('language_learning.db')
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute(
        "SELECT id, name FROM users WHERE wallet_address = ? AND auth_method = ?",
        (request.wallet_address, request.wallet_type)
    )
    user = cursor.fetchone()
    
    if not user:
        # Create new user for wallet
        wallet_name = f"{request.wallet_type.title()} User ({request.wallet_address[:6]}...{request.wallet_address[-4:]})"
        cursor.execute(
            "INSERT INTO users (name, auth_method, wallet_address) VALUES (?, ?, ?)",
            (wallet_name, request.wallet_type, request.wallet_address)
        )
        user_id = cursor.lastrowid
        user_name = wallet_name
    else:
        user_id = user[0]
        user_name = user[1]
        # Update last login
        cursor.execute(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
            (user_id,)
        )
    
    conn.commit()
    conn.close()
    
    # Create JWT token
    token = create_jwt_token(user_id)
    
    return AuthResponse(
        token=token,
        user={
            "id": user_id,
            "name": user_name,
            "auth_method": request.wallet_type,
            "wallet_address": request.wallet_address
        }
    )

@app.post("/api/auth/social", response_model=AuthResponse)
async def login_with_social(request: SocialLoginRequest):
    """Login with social provider (Google, Apple)"""
    conn = sqlite3.connect('language_learning.db')
    cursor = conn.cursor()
    
    social_id = request.user_info.get("id") or request.user_info.get("sub")
    email = request.user_info.get("email")
    name = request.user_info.get("name") or f"{request.provider.title()} User"
    avatar = request.user_info.get("picture") or request.user_info.get("avatar")
    
    # Check if user exists
    cursor.execute(
        "SELECT id, name FROM users WHERE social_id = ? AND auth_method = ?",
        (social_id, request.provider)
    )
    user = cursor.fetchone()
    
    if not user:
        # Create new user
        cursor.execute(
            "INSERT INTO users (email, name, auth_method, social_id, avatar) VALUES (?, ?, ?, ?, ?)",
            (email, name, request.provider, social_id, avatar)
        )
        user_id = cursor.lastrowid
        user_name = name
    else:
        user_id = user[0]
        user_name = user[1]
        # Update last login and avatar
        cursor.execute(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP, avatar = ? WHERE id = ?",
            (avatar, user_id)
        )
    
    conn.commit()
    conn.close()
    
    # Create JWT token
    token = create_jwt_token(user_id)
    
    return AuthResponse(
        token=token,
        user={
            "id": user_id,
            "email": email,
            "name": user_name,
            "auth_method": request.provider,
            "avatar": avatar
        }
    )

@app.get("/api/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@app.post("/api/auth/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout current user"""
    # In a more sophisticated implementation, you would invalidate the token
    # For now, we'll just return success as the frontend will remove the token
    return {"message": "Logged out successfully"}

@app.get("/api/languages")
async def get_supported_languages():
    return SUPPORTED_LANGUAGES

@app.post("/api/translate")
async def translate_text(request: TranslationRequest, current_user: dict = Depends(get_current_user)):
    try:
        if not client.api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        prompt = f"""
        Translate the following text from {SUPPORTED_LANGUAGES.get(request.source_language, {}).get('name', request.source_language)} 
        to {SUPPORTED_LANGUAGES.get(request.target_language, {}).get('name', request.target_language)}:
        
        Text: {request.text}
        
        Provide only the translation without any additional explanation.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3
        )
        
        translation = response.choices[0].message.content.strip()
        
        return {
            "original_text": request.text,
            "translated_text": translation,
            "source_language": request.source_language,
            "target_language": request.target_language
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@app.post("/api/conversation")
async def ai_conversation(request: ConversationRequest, current_user: dict = Depends(get_current_user)):
    try:
        if not client.api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        language_info = SUPPORTED_LANGUAGES.get(request.language_code, {})
        language_name = language_info.get('name', request.language_code)
        
        system_prompt = f"""
        You are an AI language tutor helping someone learn {language_name}. 
        Respond in {language_name} and provide helpful corrections and explanations when needed.
        Be encouraging and patient. If the user makes mistakes, gently correct them and explain why.
        Keep responses conversational and educational.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.message}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        # Save conversation to database if user_id provided
        if request.user_id:
            conn = sqlite3.connect('language_learning.db')
            cursor = conn.cursor()
            conversation_data = json.dumps([
                {"role": "user", "content": request.message},
                {"role": "assistant", "content": ai_response}
            ])
            cursor.execute(
                "INSERT INTO conversations (user_id, language_code, messages) VALUES (?, ?, ?)",
                (request.user_id, request.language_code, conversation_data)
            )
            conn.commit()
            conn.close()
        
        return {
            "user_message": request.message,
            "ai_response": ai_response,
            "language_code": request.language_code
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversation failed: {str(e)}")

@app.post("/api/lessons/generate")
async def generate_lesson(request: LessonRequest, current_user: dict = Depends(get_current_user)):
    try:
        if not client.api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        language_info = SUPPORTED_LANGUAGES.get(request.language_code, {})
        language_name = language_info.get('name', request.language_code)
        
        topic_text = f" about {request.topic}" if request.topic else ""
        
        prompt = f"""
        Create a {request.level} level {language_name} lesson{topic_text}.
        
        Include:
        1. 5 key vocabulary words with translations
        2. 2 example sentences using the vocabulary
        3. 1 grammar point explanation
        4. 3 practice exercises
        
        Format as JSON with the following structure:
        {{
            "title": "lesson title",
            "level": "{request.level}",
            "vocabulary": [
                {{"word": "word", "translation": "translation", "pronunciation": "pronunciation guide"}}
            ],
            "examples": ["sentence 1", "sentence 2"],
            "grammar": {{"point": "grammar rule", "explanation": "detailed explanation"}},
            "exercises": [
                {{"type": "fill-blank", "question": "question", "answer": "answer"}},
                {{"type": "translate", "question": "translate this", "answer": "translation"}},
                {{"type": "multiple-choice", "question": "question", "options": ["a", "b", "c"], "answer": "correct option"}}
            ]
        }}
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.5
        )
        
        lesson_content = response.choices[0].message.content.strip()
        
        try:
            lesson_json = json.loads(lesson_content)
            return lesson_json
        except json.JSONDecodeError:
            return {"error": "Failed to parse lesson content", "raw_content": lesson_content}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lesson generation failed: {str(e)}")

@app.post("/api/voice-conversation")
async def voice_conversation(request: VoiceConversationRequest, current_user: dict = Depends(get_current_user)):
    try:
        if not client.api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        # Decode base64 audio data
        audio_data = base64.b64decode(request.audio_data)
        
        # Create temporary file for audio
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            temp_audio.write(audio_data)
            temp_audio_path = temp_audio.name
        
        try:
            # Speech-to-text using OpenAI Whisper
            with open(temp_audio_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=request.language_code if request.language_code != "zh" else "zh-CN"
                )
            
            user_text = transcript.text
            
            # Generate AI response
            language_info = SUPPORTED_LANGUAGES.get(request.language_code, {})
            language_name = language_info.get('name', request.language_code)
            
            system_prompt = f"""
            You are an AI language tutor for voice conversation practice in {language_name}. 
            Respond naturally in {language_name} and provide gentle corrections if needed.
            Keep responses conversational, encouraging, and under 50 words.
            Focus on pronunciation and natural conversation flow.
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_text}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Generate speech from AI response
            speech_response = client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=ai_response
            )
            
            # Convert audio to base64
            audio_base64 = base64.b64encode(speech_response.content).decode()
            
            return {
                "user_text": user_text,
                "ai_response": ai_response,
                "ai_audio": audio_base64,
                "language_code": request.language_code
            }
            
        finally:
            # Clean up temporary file
            os.unlink(temp_audio_path)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice conversation failed: {str(e)}")

@app.post("/games/generate")
async def generate_game(request: GameRequest):
    try:
        if not client.api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        language_info = SUPPORTED_LANGUAGES.get(request.language_code, {})
        language_name = language_info.get('name', request.language_code)
        
        if request.game_type == "vocabulary_quiz":
            return await generate_vocabulary_quiz(request, language_name)
        elif request.game_type == "pronunciation_practice":
            return await generate_pronunciation_practice(request, language_name)
        elif request.game_type == "word_match":
            return await generate_word_match_game(request, language_name)
        else:
            raise HTTPException(status_code=400, detail="Invalid game type")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Game generation failed: {str(e)}")

async def generate_vocabulary_quiz(request: GameRequest, language_name: str):
    topic_text = f" about {request.topic}" if request.topic else ""
    difficulty_words = {"easy": 5, "medium": 8, "hard": 12}
    num_questions = difficulty_words.get(request.difficulty, 5)
    
    prompt = f"""
    Create a {request.difficulty} level vocabulary quiz in {language_name}{topic_text}.
    Generate {num_questions} multiple choice questions.
    
    Format as JSON:
    {{
        "game_type": "vocabulary_quiz",
        "title": "quiz title",
        "questions": [
            {{
                "question": "What does 'word' mean?",
                "options": ["option1", "option2", "option3", "option4"],
                "correct_answer": 0,
                "explanation": "brief explanation"
            }}
        ]
    }}
    """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
        temperature=0.5
    )
    
    try:
        return json.loads(response.choices[0].message.content.strip())
    except json.JSONDecodeError:
        return {"error": "Failed to parse quiz content"}

async def generate_pronunciation_practice(request: GameRequest, language_name: str):
    difficulty_phrases = {"easy": 5, "medium": 8, "hard": 10}
    num_phrases = difficulty_phrases.get(request.difficulty, 5)
    
    prompt = f"""
    Create {num_phrases} pronunciation practice phrases in {language_name} for {request.difficulty} level.
    Include common words and phrases that are challenging for learners.
    
    Format as JSON:
    {{
        "game_type": "pronunciation_practice",
        "title": "Pronunciation Practice",
        "phrases": [
            {{
                "text": "phrase to pronounce",
                "phonetic": "phonetic transcription",
                "difficulty": "easy/medium/hard",
                "tip": "pronunciation tip"
            }}
        ]
    }}
    """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1200,
        temperature=0.5
    )
    
    try:
        return json.loads(response.choices[0].message.content.strip())
    except json.JSONDecodeError:
        return {"error": "Failed to parse pronunciation content"}

async def generate_word_match_game(request: GameRequest, language_name: str):
    difficulty_pairs = {"easy": 6, "medium": 10, "hard": 15}
    num_pairs = difficulty_pairs.get(request.difficulty, 6)
    
    prompt = f"""
    Create a word matching game in {language_name} with {num_pairs} word pairs.
    Include words and their translations or synonyms.
    
    Format as JSON:
    {{
        "game_type": "word_match",
        "title": "Word Match Game",
        "pairs": [
            {{
                "word1": "word in {language_name}",
                "word2": "translation or synonym",
                "category": "noun/verb/adjective/etc"
            }}
        ]
    }}
    """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.5
    )
    
    try:
        return json.loads(response.choices[0].message.content.strip())
    except json.JSONDecodeError:
        return {"error": "Failed to parse word match content"}

@app.post("/pronunciation/check")
async def check_pronunciation(request: PronunciationRequest):
    try:
        if not client.api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        # Decode base64 audio data
        audio_data = base64.b64decode(request.audio_data)
        
        # Create temporary file for audio
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            temp_audio.write(audio_data)
            temp_audio_path = temp_audio.name
        
        try:
            # Speech-to-text using OpenAI Whisper
            with open(temp_audio_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=request.language_code if request.language_code != "zh" else "zh-CN"
                )
            
            user_pronunciation = transcript.text.lower().strip()
            expected_text = request.text.lower().strip()
            
            # Calculate similarity score (simple approach)
            similarity = calculate_similarity(user_pronunciation, expected_text)
            
            # Generate feedback
            language_info = SUPPORTED_LANGUAGES.get(request.language_code, {})
            language_name = language_info.get('name', request.language_code)
            
            feedback_prompt = f"""
            Compare pronunciation accuracy in {language_name}:
            Expected: "{request.text}"
            User said: "{user_pronunciation}"
            
            Provide constructive feedback on pronunciation accuracy and tips for improvement.
            Keep feedback encouraging and specific.
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": feedback_prompt}],
                max_tokens=200,
                temperature=0.3
            )
            
            feedback = response.choices[0].message.content.strip()
            
            return {
                "expected_text": request.text,
                "user_pronunciation": user_pronunciation,
                "similarity_score": similarity,
                "feedback": feedback,
                "passed": similarity > 0.7
            }
            
        finally:
            # Clean up temporary file
            os.unlink(temp_audio_path)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pronunciation check failed: {str(e)}")

def calculate_similarity(text1: str, text2: str) -> float:
    """Simple similarity calculation based on common words"""
    words1 = set(text1.split())
    words2 = set(text2.split())
    
    if not words1 and not words2:
        return 1.0
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
