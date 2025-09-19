import openai
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.models import User, UserProgress, Conversation
from backend.database import get_db

logger = logging.getLogger(__name__)

class PersonalizedLearningService:
    """Service for personalized AI learning features"""
    
    def __init__(self, openai_client):
        self.client = openai_client
        self.learning_analytics = LearningAnalytics()
    
    async def generate_personalized_lesson(self, user_id: int, language_code: str, 
                                         current_level: str, weak_areas: List[str],
                                         learning_goals: List[str]) -> Dict:
        """Generate a personalized lesson based on user's learning profile"""
        try:
            # Get user's learning history
            learning_history = await self.learning_analytics.get_user_learning_history(user_id, language_code)
            
            # Create personalized prompt
            prompt = self._create_personalized_lesson_prompt(
                language_code, current_level, weak_areas, learning_goals, learning_history
            )
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.7
            )
            
            lesson_content = json.loads(response.choices[0].message.content)
            
            # Add personalization metadata
            lesson_content.update({
                "personalized": True,
                "user_id": user_id,
                "generated_at": datetime.utcnow().isoformat(),
                "weak_areas_focused": weak_areas,
                "learning_goals": learning_goals
            })
            
            return lesson_content
            
        except Exception as e:
            logger.error(f"Error generating personalized lesson: {e}")
            raise
    
    async def adapt_difficulty(self, user_id: int, language_code: str, 
                             current_exercise: Dict, performance: Dict) -> Dict:
        """Adapt exercise difficulty based on user performance"""
        try:
            # Analyze performance patterns
            performance_analysis = await self.learning_analytics.analyze_performance(
                user_id, language_code, performance
            )
            
            # Determine difficulty adjustment
            difficulty_adjustment = self._calculate_difficulty_adjustment(performance_analysis)
            
            # Generate adapted exercise
            adapted_exercise = await self._generate_adapted_exercise(
                current_exercise, difficulty_adjustment, language_code
            )
            
            return adapted_exercise
            
        except Exception as e:
            logger.error(f"Error adapting difficulty: {e}")
            raise
    
    async def generate_learning_path(self, user_id: int, language_code: str, 
                                   target_level: str, time_commitment: int) -> Dict:
        """Generate a complete learning path for the user"""
        try:
            # Get user's current profile
            user_profile = await self.learning_analytics.get_user_profile(user_id, language_code)
            
            # Create learning path prompt
            prompt = self._create_learning_path_prompt(
                user_profile, language_code, target_level, time_commitment
            )
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.6
            )
            
            learning_path = json.loads(response.choices[0].message.content)
            
            # Add metadata
            learning_path.update({
                "user_id": user_id,
                "language_code": language_code,
                "created_at": datetime.utcnow().isoformat(),
                "estimated_duration": time_commitment
            })
            
            return learning_path
            
        except Exception as e:
            logger.error(f"Error generating learning path: {e}")
            raise
    
    def _create_personalized_lesson_prompt(self, language_code: str, current_level: str,
                                         weak_areas: List[str], learning_goals: List[str],
                                         learning_history: Dict) -> str:
        """Create prompt for personalized lesson generation"""
        return f"""
        Create a personalized {language_code} lesson for a {current_level} level learner.
        
        User Profile:
        - Current Level: {current_level}
        - Weak Areas: {', '.join(weak_areas)}
        - Learning Goals: {', '.join(learning_goals)}
        - Recent Performance: {learning_history.get('recent_performance', 'No data')}
        - Learning Style: {learning_history.get('learning_style', 'Mixed')}
        
        Generate a lesson that:
        1. Focuses on the identified weak areas
        2. Aligns with learning goals
        3. Matches the user's learning style
        4. Builds on previous knowledge
        5. Includes interactive exercises
        
        Format as JSON with:
        {{
            "title": "Lesson title",
            "level": "{current_level}",
            "focus_areas": ["area1", "area2"],
            "vocabulary": [{{"word": "word", "translation": "translation", "difficulty": "easy/medium/hard"}}],
            "grammar": [{{"point": "grammar rule", "explanation": "explanation", "examples": ["example1", "example2"]}}],
            "exercises": [{{"type": "exercise_type", "question": "question", "difficulty": "easy/medium/hard"}}],
            "conversation_practice": "scenario for practice",
            "estimated_time": "X minutes",
            "prerequisites": ["required knowledge"],
            "learning_objectives": ["objective1", "objective2"]
        }}
        """
    
    def _calculate_difficulty_adjustment(self, performance_analysis: Dict) -> str:
        """Calculate how to adjust difficulty based on performance"""
        accuracy = performance_analysis.get('accuracy', 0.5)
        speed = performance_analysis.get('speed', 0.5)
        confidence = performance_analysis.get('confidence', 0.5)
        
        # Simple difficulty adjustment logic
        if accuracy > 0.8 and speed > 0.7 and confidence > 0.8:
            return "increase"  # User is doing well, increase difficulty
        elif accuracy < 0.6 or speed < 0.4 or confidence < 0.5:
            return "decrease"  # User is struggling, decrease difficulty
        else:
            return "maintain"  # Keep current difficulty
    
    async def _generate_adapted_exercise(self, current_exercise: Dict, 
                                       adjustment: str, language_code: str) -> Dict:
        """Generate an adapted version of the exercise"""
        if adjustment == "maintain":
            return current_exercise
        
        # Create adaptation prompt
        prompt = f"""
        Adapt this {language_code} exercise to {adjustment} difficulty:
        
        Current Exercise: {json.dumps(current_exercise)}
        
        Requirements:
        - Keep the same learning objective
        - Adjust vocabulary complexity
        - Modify grammar difficulty
        - Change exercise format if needed
        
        Return the adapted exercise in the same JSON format.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.5
        )
        
        return json.loads(response.choices[0].message.content)
    
    def _create_learning_path_prompt(self, user_profile: Dict, language_code: str,
                                   target_level: str, time_commitment: int) -> str:
        """Create prompt for learning path generation"""
        return f"""
        Create a comprehensive learning path for {language_code} from {user_profile.get('current_level', 'beginner')} to {target_level}.
        
        User Profile:
        - Current Level: {user_profile.get('current_level', 'beginner')}
        - Learning Goals: {user_profile.get('goals', [])}
        - Available Time: {time_commitment} minutes per day
        - Learning Style: {user_profile.get('learning_style', 'mixed')}
        - Weak Areas: {user_profile.get('weak_areas', [])}
        
        Create a structured learning path with:
        1. Weekly milestones
        2. Daily lesson plans
        3. Practice exercises
        4. Assessment points
        5. Progress tracking
        
        Format as JSON with:
        {{
            "overview": {{
                "total_weeks": X,
                "daily_time": {time_commitment},
                "target_level": "{target_level}",
                "estimated_completion": "date"
            }},
            "weekly_plans": [
                {{
                    "week": 1,
                    "focus": "basic vocabulary and greetings",
                    "lessons": ["lesson1", "lesson2", "lesson3"],
                    "goals": ["goal1", "goal2"],
                    "assessment": "assessment_description"
                }}
            ],
            "daily_schedule": {{
                "monday": ["exercise1", "exercise2"],
                "tuesday": ["exercise1", "exercise2"],
                // ... for each day
            }},
            "milestones": [
                {{
                    "week": 2,
                    "description": "Can introduce yourself",
                    "assessment": "conversation_practice"
                }}
            ]
        }}
        """

class LearningAnalytics:
    """Service for learning analytics and insights"""
    
    def __init__(self):
        self.db = next(get_db())
    
    async def get_user_learning_history(self, user_id: int, language_code: str) -> Dict:
        """Get user's learning history and patterns"""
        try:
            # Get recent conversations
            conversations = self.db.query(Conversation).filter(
                Conversation.user_id == user_id,
                Conversation.language_code == language_code
            ).order_by(Conversation.timestamp.desc()).limit(50).all()
            
            # Get progress data
            progress = self.db.query(UserProgress).filter(
                UserProgress.user_id == user_id
            ).all()
            
            # Analyze patterns
            return {
                "total_conversations": len(conversations),
                "recent_performance": self._analyze_recent_performance(progress),
                "learning_style": self._determine_learning_style(conversations),
                "weak_areas": self._identify_weak_areas(progress),
                "strengths": self._identify_strengths(progress)
            }
            
        except Exception as e:
            logger.error(f"Error getting learning history: {e}")
            return {}
    
    async def analyze_performance(self, user_id: int, language_code: str, 
                                performance: Dict) -> Dict:
        """Analyze user performance for difficulty adaptation"""
        return {
            "accuracy": performance.get("correct_answers", 0) / max(performance.get("total_questions", 1), 1),
            "speed": performance.get("avg_response_time", 30) / 30,  # Normalize to 30 seconds
            "confidence": performance.get("confidence_score", 0.5),
            "consistency": self._calculate_consistency(performance),
            "improvement_trend": self._calculate_improvement_trend(user_id, language_code)
        }
    
    async def get_user_profile(self, user_id: int, language_code: str) -> Dict:
        """Get comprehensive user learning profile"""
        learning_history = await self.get_user_learning_history(user_id, language_code)
        
        return {
            "user_id": user_id,
            "language_code": language_code,
            "current_level": self._determine_current_level(learning_history),
            "learning_style": learning_history.get("learning_style", "mixed"),
            "weak_areas": learning_history.get("weak_areas", []),
            "strengths": learning_history.get("strengths", []),
            "goals": self._get_user_goals(user_id),
            "preferred_exercise_types": self._get_preferred_exercises(user_id)
        }
    
    def _analyze_recent_performance(self, progress: List) -> Dict:
        """Analyze recent performance data"""
        if not progress:
            return {"accuracy": 0.5, "trend": "stable"}
        
        recent_scores = [p.score for p in progress[-10:]]  # Last 10 exercises
        return {
            "accuracy": sum(recent_scores) / len(recent_scores) / 100,
            "trend": "improving" if len(recent_scores) > 1 and recent_scores[-1] > recent_scores[0] else "stable"
        }
    
    def _determine_learning_style(self, conversations: List) -> str:
        """Determine user's learning style based on conversation patterns"""
        if not conversations:
            return "mixed"
        
        # Simple heuristic based on conversation length and complexity
        avg_length = sum(len(c.message or "") for c in conversations) / len(conversations)
        
        if avg_length > 100:
            return "conversational"
        elif avg_length > 50:
            return "balanced"
        else:
            return "structured"
    
    def _identify_weak_areas(self, progress: List) -> List[str]:
        """Identify areas where user struggles"""
        # This would be more sophisticated in a real implementation
        return ["grammar", "pronunciation"]  # Placeholder
    
    def _identify_strengths(self, progress: List) -> List[str]:
        """Identify user's strong areas"""
        return ["vocabulary", "listening"]  # Placeholder
    
    def _calculate_consistency(self, performance: Dict) -> float:
        """Calculate performance consistency"""
        # Placeholder implementation
        return 0.7
    
    def _calculate_improvement_trend(self, user_id: int, language_code: str) -> str:
        """Calculate if user is improving over time"""
        # Placeholder implementation
        return "improving"
    
    def _determine_current_level(self, learning_history: Dict) -> str:
        """Determine user's current proficiency level"""
        performance = learning_history.get("recent_performance", {})
        accuracy = performance.get("accuracy", 0.5)
        
        if accuracy > 0.8:
            return "advanced"
        elif accuracy > 0.6:
            return "intermediate"
        else:
            return "beginner"
    
    def _get_user_goals(self, user_id: int) -> List[str]:
        """Get user's learning goals"""
        # Placeholder - would come from user preferences
        return ["conversation", "travel", "business"]
    
    def _get_preferred_exercises(self, user_id: int) -> List[str]:
        """Get user's preferred exercise types"""
        # Placeholder - would come from user interaction data
        return ["vocabulary_quiz", "conversation_practice"]
