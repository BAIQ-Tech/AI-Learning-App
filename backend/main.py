from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import json
import os
import jwt
import hashlib
import secrets
import uuid
from dotenv import load_dotenv

# Import database and models
from database import get_db, Base, engine
from models import User, UserProgress, Conversation, Lesson, Story, Comment, StoryLike

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="AI Learning API", version="1.0.0")

# Static files (media uploads)
MEDIA_DIR = os.path.join(os.path.dirname(__file__), "media")
os.makedirs(MEDIA_DIR, exist_ok=True)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-vercel-app.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

# Security
security = HTTPBearer()

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Initialize database
try:
    print("Attempting to connect to the database...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
except Exception as e:
    print(f"Error creating database tables: {e}")
    import traceback
    traceback.print_exc()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))

# Health check endpoint
@app.get("/health")
async def health_check():
    from datetime import datetime
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

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

# SQLAlchemy Models
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=True)
    email = Column(String, unique=True, nullable=True)
    password_hash = Column(String, nullable=True)
    name = Column(String, nullable=False)
    avatar = Column(String, nullable=True)
    auth_method = Column(String, nullable=False)
    wallet_address = Column(String, unique=True, nullable=True)
    social_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    progress = relationship("UserProgress", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")

class UserProgress(Base):
    __tablename__ = 'user_progress'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    lesson_id = Column(Integer, ForeignKey('lessons.id'))
    completed = Column(Boolean, default=False)
    score = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="progress")
    lesson = relationship("Lesson", back_populates="progress")

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

# Stories models
class StoryListResponse(BaseModel):
    id: int
    user_id: int
    content_type: str
    text: Optional[str] = None
    media_url: Optional[str] = None
    created_at: str
    likes: int
    liked_by_me: bool

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

# -----------------------
# Stories Endpoints
# -----------------------

@app.post("/api/stories")
async def create_story(
    content_type: str = Form(...),
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user),
):
    """
    Create a story. Supports:
      - content_type: 'image' | 'video' | 'audio' | 'text'
      - text: optional caption or content (required for text-only)
      - file: optional media file for image/video/audio
    """
    if content_type not in {"image", "video", "audio", "text"}:
        raise HTTPException(status_code=400, detail="Invalid content_type")

    media_url = None
    if content_type != "text":
        if not file:
            raise HTTPException(status_code=400, detail="Media file is required for non-text stories")
        # Save file
        ext = os.path.splitext(file.filename or "")[1].lower()
        safe_ext = ext if ext in {".png", ".jpg", ".jpeg", ".mp4", ".mov", ".m4a", ".wav", ".aac"} else ""
        filename = f"{uuid.uuid4().hex}{safe_ext}"
        dest_path = os.path.join(MEDIA_DIR, filename)
        with open(dest_path, "wb") as out:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                out.write(chunk)
        media_url = f"/media/{filename}"
    else:
        if not text:
            raise HTTPException(status_code=400, detail="Text content required for text stories")

    conn = sqlite3.connect('language_learning.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO stories (user_id, content_type, text, media_url) VALUES (?, ?, ?, ?)",
        (current_user["id"], content_type, text, media_url)
    )
    story_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {"id": story_id, "media_url": media_url}


@app.get("/api/stories", response_model=List[StoryListResponse])
async def list_stories(current_user: dict = Depends(get_current_user)):
    conn = sqlite3.connect('language_learning.db')
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT s.id, s.user_id, s.content_type, s.text, s.media_url, s.created_at,
               IFNULL(l.likes, 0) as likes,
               CASE WHEN lm.user_id IS NULL THEN 0 ELSE 1 END as liked_by_me
        FROM stories s
        LEFT JOIN (
            SELECT story_id, COUNT(*) as likes FROM story_likes GROUP BY story_id
        ) l ON l.story_id = s.id
        LEFT JOIN (
            SELECT story_id, user_id FROM story_likes WHERE user_id = ?
        ) lm ON lm.story_id = s.id
        ORDER BY s.created_at DESC
        LIMIT 100
        """,
        (current_user["id"],)
    )
    rows = cursor.fetchall()
    conn.close()

    results: List[StoryListResponse] = []
    for r in rows:
        results.append(StoryListResponse(
            id=r[0], user_id=r[1], content_type=r[2], text=r[3], media_url=r[4], created_at=str(r[5]), likes=int(r[6]), liked_by_me=bool(r[7])
        ))
    return results


@app.post("/api/stories/{story_id}/like")
async def like_story(story_id: int, current_user: dict = Depends(get_current_user)):
    conn = sqlite3.connect('language_learning.db')
    cursor = conn.cursor()

    # Ensure story exists
    cursor.execute("SELECT id FROM stories WHERE id = ?", (story_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Story not found")

    # Toggle like
    cursor.execute(
        "SELECT 1 FROM story_likes WHERE story_id = ? AND user_id = ?",
        (story_id, current_user["id"]) 
    )
    if cursor.fetchone():
        cursor.execute(
            "DELETE FROM story_likes WHERE story_id = ? AND user_id = ?",
            (story_id, current_user["id"]) 
        )
        action = "unliked"
    else:
        cursor.execute(
            "INSERT INTO story_likes (story_id, user_id) VALUES (?, ?)",
            (story_id, current_user["id"]) 
        )
        action = "liked"

    conn.commit()
    # Return new like count
    cursor.execute("SELECT COUNT(*) FROM story_likes WHERE story_id = ?", (story_id,))
    likes = cursor.fetchone()[0]
    conn.close()

    return {"story_id": story_id, "status": action, "likes": likes}

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
