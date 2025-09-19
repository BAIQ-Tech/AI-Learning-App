from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Optional
from pydantic import BaseModel
from backend.services.ai_service import PersonalizedLearningService
from backend.services.gamification_service import GamificationService
from backend.services.social_service import SocialLearningService
from backend.main import get_current_user
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/ai", tags=["AI Features"])

# Initialize services
ai_service = PersonalizedLearningService(None)  # Will be injected with OpenAI client
gamification_service = GamificationService()
social_service = SocialLearningService()

# Pydantic models
class PersonalizedLessonRequest(BaseModel):
    language_code: str
    current_level: str
    weak_areas: List[str]
    learning_goals: List[str]

class DifficultyAdaptationRequest(BaseModel):
    language_code: str
    current_exercise: Dict
    performance: Dict

class LearningPathRequest(BaseModel):
    language_code: str
    target_level: str
    time_commitment: int  # minutes per day

class XPAwardRequest(BaseModel):
    language_code: str
    activity_type: str
    points: int

class StudyGroupRequest(BaseModel):
    name: str
    description: str
    language_code: str
    max_members: int = 10
    is_public: bool = True

class ContentShareRequest(BaseModel):
    content_type: str
    title: str
    description: str
    content_data: Dict
    language_code: str
    difficulty_level: str = "medium"
    tags: List[str] = []

# AI Learning Routes
@router.post("/personalized-lesson")
async def generate_personalized_lesson(
    request: PersonalizedLessonRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate a personalized lesson based on user's learning profile"""
    try:
        lesson = await ai_service.generate_personalized_lesson(
            user_id=current_user["id"],
            language_code=request.language_code,
            current_level=request.current_level,
            weak_areas=request.weak_areas,
            learning_goals=request.learning_goals
        )
        return lesson
    except Exception as e:
        logger.error(f"Error generating personalized lesson: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate personalized lesson")

@router.post("/adapt-difficulty")
async def adapt_difficulty(
    request: DifficultyAdaptationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Adapt exercise difficulty based on user performance"""
    try:
        adapted_exercise = await ai_service.adapt_difficulty(
            user_id=current_user["id"],
            language_code=request.language_code,
            current_exercise=request.current_exercise,
            performance=request.performance
        )
        return adapted_exercise
    except Exception as e:
        logger.error(f"Error adapting difficulty: {e}")
        raise HTTPException(status_code=500, detail="Failed to adapt difficulty")

@router.post("/learning-path")
async def generate_learning_path(
    request: LearningPathRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate a complete learning path for the user"""
    try:
        learning_path = await ai_service.generate_learning_path(
            user_id=current_user["id"],
            language_code=request.language_code,
            target_level=request.target_level,
            time_commitment=request.time_commitment
        )
        return learning_path
    except Exception as e:
        logger.error(f"Error generating learning path: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate learning path")

# Gamification Routes
@router.post("/award-xp")
async def award_xp(
    request: XPAwardRequest,
    current_user: dict = Depends(get_current_user)
):
    """Award XP to user and check for level up"""
    try:
        result = await gamification_service.award_xp(
            user_id=current_user["id"],
            language_code=request.language_code,
            activity_type=request.activity_type,
            points=request.points
        )
        return result
    except Exception as e:
        logger.error(f"Error awarding XP: {e}")
        raise HTTPException(status_code=500, detail="Failed to award XP")

@router.get("/leaderboard/{language_code}")
async def get_leaderboard(
    language_code: str,
    category: str = "weekly",
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Get leaderboard for a specific language"""
    try:
        leaderboard = await gamification_service.get_leaderboard(
            language_code=language_code,
            category=category,
            limit=limit
        )
        return {"leaderboard": leaderboard}
    except Exception as e:
        logger.error(f"Error getting leaderboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to get leaderboard")

@router.get("/daily-challenge/{language_code}")
async def get_daily_challenge(
    language_code: str,
    current_user: dict = Depends(get_current_user)
):
    """Get today's daily challenge"""
    try:
        challenge = await gamification_service.get_daily_challenge(language_code)
        if not challenge:
            return {"message": "No daily challenge available today"}
        return challenge
    except Exception as e:
        logger.error(f"Error getting daily challenge: {e}")
        raise HTTPException(status_code=500, detail="Failed to get daily challenge")

@router.post("/daily-challenge/{challenge_id}/complete")
async def complete_daily_challenge(
    challenge_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Complete a daily challenge"""
    try:
        result = await gamification_service.complete_daily_challenge(
            user_id=current_user["id"],
            challenge_id=challenge_id
        )
        return result
    except Exception as e:
        logger.error(f"Error completing daily challenge: {e}")
        raise HTTPException(status_code=500, detail="Failed to complete daily challenge")

@router.get("/user-stats/{language_code}")
async def get_user_stats(
    language_code: str,
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive user statistics"""
    try:
        stats = await gamification_service.get_user_stats(
            user_id=current_user["id"],
            language_code=language_code
        )
        return stats
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user stats")

# Social Learning Routes
@router.post("/study-groups")
async def create_study_group(
    request: StudyGroupRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new study group"""
    try:
        group = await social_service.create_study_group(
            user_id=current_user["id"],
            name=request.name,
            description=request.description,
            language_code=request.language_code,
            max_members=request.max_members,
            is_public=request.is_public
        )
        return group
    except Exception as e:
        logger.error(f"Error creating study group: {e}")
        raise HTTPException(status_code=500, detail="Failed to create study group")

@router.get("/study-groups/{language_code}")
async def get_study_groups(
    language_code: str,
    current_user: dict = Depends(get_current_user)
):
    """Get available study groups"""
    try:
        groups = await social_service.get_study_groups(
            language_code=language_code,
            user_id=current_user["id"]
        )
        return {"groups": groups}
    except Exception as e:
        logger.error(f"Error getting study groups: {e}")
        raise HTTPException(status_code=500, detail="Failed to get study groups")

@router.post("/study-groups/{group_id}/join")
async def join_study_group(
    group_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Join a study group"""
    try:
        result = await social_service.join_study_group(
            user_id=current_user["id"],
            group_id=group_id
        )
        return result
    except Exception as e:
        logger.error(f"Error joining study group: {e}")
        raise HTTPException(status_code=500, detail="Failed to join study group")

@router.get("/peer-matches/{learning_language}/{native_language}")
async def find_peer_matches(
    learning_language: str,
    native_language: str,
    current_user: dict = Depends(get_current_user)
):
    """Find potential peer matches for language exchange"""
    try:
        matches = await social_service.find_peer_matches(
            user_id=current_user["id"],
            learning_language=learning_language,
            native_language=native_language
        )
        return {"matches": matches}
    except Exception as e:
        logger.error(f"Error finding peer matches: {e}")
        raise HTTPException(status_code=500, detail="Failed to find peer matches")

@router.post("/content/share")
async def share_content(
    request: ContentShareRequest,
    current_user: dict = Depends(get_current_user)
):
    """Share content with the community"""
    try:
        content = await social_service.share_content(
            user_id=current_user["id"],
            content_type=request.content_type,
            title=request.title,
            description=request.description,
            content_data=request.content_data,
            language_code=request.language_code,
            difficulty_level=request.difficulty_level,
            tags=request.tags
        )
        return content
    except Exception as e:
        logger.error(f"Error sharing content: {e}")
        raise HTTPException(status_code=500, detail="Failed to share content")

@router.get("/content/{language_code}")
async def get_shared_content(
    language_code: str,
    content_type: str = None,
    difficulty_level: str = None,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get shared content from the community"""
    try:
        content = await social_service.get_shared_content(
            language_code=language_code,
            content_type=content_type,
            difficulty_level=difficulty_level,
            limit=limit
        )
        return {"content": content}
    except Exception as e:
        logger.error(f"Error getting shared content: {e}")
        raise HTTPException(status_code=500, detail="Failed to get shared content")

@router.post("/content/{content_id}/like")
async def like_content(
    content_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Like or unlike shared content"""
    try:
        result = await social_service.like_content(
            user_id=current_user["id"],
            content_id=content_id
        )
        return result
    except Exception as e:
        logger.error(f"Error liking content: {e}")
        raise HTTPException(status_code=500, detail="Failed to like content")
