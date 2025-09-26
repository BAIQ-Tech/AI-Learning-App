import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from models import (
    Achievement, UserAchievement, UserStreak, UserLevel,
    Leaderboard, DailyChallenge, UserDailyChallenge, UserReward
)
from backend.database import get_db

logger = logging.getLogger(__name__)

class GamificationService:
    """Service for gamification features"""
    
    def __init__(self):
        self.db = next(get_db())
    
    async def award_xp(self, user_id: int, language_code: str, 
                      activity_type: str, points: int) -> Dict:
        """Award XP to user and check for level up"""
        try:
            # Get or create user level
            user_level = self.db.query(UserLevel).filter(
                UserLevel.user_id == user_id,
                UserLevel.language_code == language_code
            ).first()
            
            if not user_level:
                user_level = UserLevel(
                    user_id=user_id,
                    language_code=language_code,
                    current_level=1,
                    total_xp=0,
                    xp_to_next_level=100
                )
                self.db.add(user_level)
            
            # Add XP
            user_level.total_xp += points
            old_level = user_level.current_level
            
            # Check for level up
            level_up_result = self._check_level_up(user_level)
            
            # Update streak
            await self.update_streak(user_id, language_code)
            
            # Check for achievements
            achievements_earned = await self.check_achievements(user_id, language_code, activity_type)
            
            # Update leaderboard
            await self.update_leaderboard(user_id, language_code, points)
            
            self.db.commit()
            
            return {
                "xp_awarded": points,
                "total_xp": user_level.total_xp,
                "current_level": user_level.current_level,
                "level_up": level_up_result["leveled_up"],
                "level_up_rewards": level_up_result.get("rewards", []),
                "achievements_earned": achievements_earned,
                "streak_updated": True
            }
            
        except Exception as e:
            logger.error(f"Error awarding XP: {e}")
            self.db.rollback()
            raise
    
    async def update_streak(self, user_id: int, language_code: str) -> Dict:
        """Update user's learning streak"""
        try:
            streak = self.db.query(UserStreak).filter(
                UserStreak.user_id == user_id,
                UserStreak.language_code == language_code
            ).first()
            
            now = datetime.utcnow()
            
            if not streak:
                streak = UserStreak(
                    user_id=user_id,
                    language_code=language_code,
                    current_streak=1,
                    longest_streak=1,
                    last_activity=now
                )
                self.db.add(streak)
            else:
                # Check if streak should continue or reset
                time_diff = now - streak.last_activity
                
                if time_diff.days == 1:
                    # Continue streak
                    streak.current_streak += 1
                    streak.longest_streak = max(streak.longest_streak, streak.current_streak)
                elif time_diff.days > 1:
                    # Reset streak
                    streak.current_streak = 1
                
                streak.last_activity = now
            
            self.db.commit()
            
            return {
                "current_streak": streak.current_streak,
                "longest_streak": streak.longest_streak,
                "streak_freeze_count": streak.streak_freeze_count
            }
            
        except Exception as e:
            logger.error(f"Error updating streak: {e}")
            self.db.rollback()
            raise
    
    async def check_achievements(self, user_id: int, language_code: str, 
                               activity_type: str) -> List[Dict]:
        """Check and award achievements based on user activity"""
        try:
            achievements_earned = []
            
            # Get all active achievements
            achievements = self.db.query(Achievement).filter(
                Achievement.is_active == True
            ).all()
            
            for achievement in achievements:
                # Check if user already has this achievement
                existing = self.db.query(UserAchievement).filter(
                    UserAchievement.user_id == user_id,
                    UserAchievement.achievement_id == achievement.id
                ).first()
                
                if existing:
                    continue
                
                # Check if achievement criteria are met
                if await self._check_achievement_criteria(user_id, language_code, achievement, activity_type):
                    # Award achievement
                    user_achievement = UserAchievement(
                        user_id=user_id,
                        achievement_id=achievement.id,
                        progress=100
                    )
                    self.db.add(user_achievement)
                    
                    # Award XP and points
                    await self.award_xp(user_id, language_code, "achievement", achievement.points)
                    
                    achievements_earned.append({
                        "id": achievement.id,
                        "name": achievement.name,
                        "description": achievement.description,
                        "icon": achievement.icon,
                        "points": achievement.points,
                        "rarity": achievement.rarity
                    })
            
            self.db.commit()
            return achievements_earned
            
        except Exception as e:
            logger.error(f"Error checking achievements: {e}")
            self.db.rollback()
            raise
    
    async def get_leaderboard(self, language_code: str, category: str = "weekly", 
                            limit: int = 10) -> List[Dict]:
        """Get leaderboard for a specific language and category"""
        try:
            # Calculate period dates
            now = datetime.utcnow()
            if category == "weekly":
                period_start = now - timedelta(days=7)
            elif category == "monthly":
                period_start = now - timedelta(days=30)
            else:  # all_time
                period_start = datetime.min
            
            # Get leaderboard entries
            entries = self.db.query(Leaderboard).filter(
                Leaderboard.language_code == language_code,
                Leaderboard.category == category,
                Leaderboard.period_start >= period_start
            ).order_by(desc(Leaderboard.score)).limit(limit).all()
            
            leaderboard = []
            for i, entry in enumerate(entries):
                leaderboard.append({
                    "rank": i + 1,
                    "user_id": entry.user_id,
                    "user_name": entry.user.name if entry.user else "Unknown",
                    "score": entry.score,
                    "avatar": entry.user.avatar if entry.user else None
                })
            
            return leaderboard
            
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []
    
    async def get_daily_challenge(self, language_code: str) -> Optional[Dict]:
        """Get today's daily challenge for a language"""
        try:
            today = datetime.utcnow().date()
            
            challenge = self.db.query(DailyChallenge).filter(
                DailyChallenge.language_code == language_code,
                DailyChallenge.is_active == True,
                func.date(DailyChallenge.date) == today
            ).first()
            
            if not challenge:
                return None
            
            return {
                "id": challenge.id,
                "title": challenge.title,
                "description": challenge.description,
                "challenge_type": challenge.challenge_type,
                "difficulty": challenge.difficulty,
                "requirements": challenge.requirements,
                "reward_xp": challenge.reward_xp,
                "reward_points": challenge.reward_points,
                "expires_at": challenge.expires_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting daily challenge: {e}")
            return None
    
    async def complete_daily_challenge(self, user_id: int, challenge_id: int) -> Dict:
        """Complete a daily challenge"""
        try:
            # Check if user already completed this challenge
            existing = self.db.query(UserDailyChallenge).filter(
                UserDailyChallenge.user_id == user_id,
                UserDailyChallenge.challenge_id == challenge_id
            ).first()
            
            if existing and existing.is_completed:
                return {"error": "Challenge already completed"}
            
            # Get challenge details
            challenge = self.db.query(DailyChallenge).filter(
                DailyChallenge.id == challenge_id
            ).first()
            
            if not challenge:
                return {"error": "Challenge not found"}
            
            # Mark as completed
            if existing:
                existing.is_completed = True
                existing.completed_at = datetime.utcnow()
            else:
                user_challenge = UserDailyChallenge(
                    user_id=user_id,
                    challenge_id=challenge_id,
                    progress=100,
                    is_completed=True,
                    completed_at=datetime.utcnow()
                )
                self.db.add(user_challenge)
            
            # Award rewards
            await self.award_xp(user_id, challenge.language_code, "daily_challenge", challenge.reward_xp)
            
            # Add points to user rewards
            reward = UserReward(
                user_id=user_id,
                reward_type="points",
                reward_value=challenge.reward_points,
                source="daily_challenge"
            )
            self.db.add(reward)
            
            self.db.commit()
            
            return {
                "success": True,
                "xp_awarded": challenge.reward_xp,
                "points_awarded": challenge.reward_points,
                "challenge_completed": True
            }
            
        except Exception as e:
            logger.error(f"Error completing daily challenge: {e}")
            self.db.rollback()
            raise
    
    async def get_user_stats(self, user_id: int, language_code: str) -> Dict:
        """Get comprehensive user statistics"""
        try:
            # Get user level
            user_level = self.db.query(UserLevel).filter(
                UserLevel.user_id == user_id,
                UserLevel.language_code == language_code
            ).first()
            
            # Get streak info
            streak = self.db.query(UserStreak).filter(
                UserStreak.user_id == user_id,
                UserStreak.language_code == language_code
            ).first()
            
            # Get achievements
            achievements = self.db.query(UserAchievement).join(Achievement).filter(
                UserAchievement.user_id == user_id
            ).all()
            
            # Get total points
            total_points = self.db.query(func.sum(UserReward.reward_value)).filter(
                UserReward.user_id == user_id,
                UserReward.reward_type == "points"
            ).scalar() or 0
            
            # Get leaderboard rank
            leaderboard_rank = await self._get_user_leaderboard_rank(user_id, language_code)
            
            return {
                "level": user_level.current_level if user_level else 1,
                "total_xp": user_level.total_xp if user_level else 0,
                "xp_to_next_level": user_level.xp_to_next_level if user_level else 100,
                "level_progress": user_level.level_progress if user_level else 0.0,
                "current_streak": streak.current_streak if streak else 0,
                "longest_streak": streak.longest_streak if streak else 0,
                "total_achievements": len(achievements),
                "total_points": total_points,
                "leaderboard_rank": leaderboard_rank,
                "achievements": [
                    {
                        "name": ach.achievement.name,
                        "description": ach.achievement.description,
                        "icon": ach.achievement.icon,
                        "rarity": ach.achievement.rarity,
                        "earned_at": ach.earned_at.isoformat()
                    }
                    for ach in achievements
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {}
    
    def _check_level_up(self, user_level: UserLevel) -> Dict:
        """Check if user should level up and calculate rewards"""
        old_level = user_level.current_level
        
        # Calculate new level based on XP
        new_level = 1
        xp_needed = 100
        
        while user_level.total_xp >= xp_needed:
            new_level += 1
            xp_needed += 100 + (new_level - 1) * 50  # Increasing XP requirement
        
        if new_level > old_level:
            user_level.current_level = new_level
            user_level.xp_to_next_level = xp_needed - user_level.total_xp
            user_level.level_progress = (user_level.total_xp - (xp_needed - 100)) / 100
            
            # Calculate level up rewards
            rewards = []
            for level in range(old_level + 1, new_level + 1):
                if level % 5 == 0:  # Every 5 levels
                    rewards.append({
                        "type": "streak_freeze",
                        "value": 1,
                        "description": "1 Streak Freeze Token"
                    })
                if level % 10 == 0:  # Every 10 levels
                    rewards.append({
                        "type": "points",
                        "value": 100,
                        "description": "100 Bonus Points"
                    })
            
            return {
                "leveled_up": True,
                "old_level": old_level,
                "new_level": new_level,
                "rewards": rewards
            }
        
        return {"leveled_up": False}
    
    async def _check_achievement_criteria(self, user_id: int, language_code: str, 
                                        achievement: Achievement, activity_type: str) -> bool:
        """Check if achievement criteria are met"""
        requirements = achievement.requirements
        
        if achievement.category == "streak":
            streak = self.db.query(UserStreak).filter(
                UserStreak.user_id == user_id,
                UserStreak.language_code == language_code
            ).first()
            return streak and streak.current_streak >= requirements.get("streak_days", 0)
        
        elif achievement.category == "level":
            user_level = self.db.query(UserLevel).filter(
                UserLevel.user_id == user_id,
                UserLevel.language_code == language_code
            ).first()
            return user_level and user_level.current_level >= requirements.get("level", 0)
        
        elif achievement.category == "milestone":
            # Check specific milestones based on requirements
            if "lessons_completed" in requirements:
                # Implementation would check lesson completion count
                pass
            if "xp_earned" in requirements:
                user_level = self.db.query(UserLevel).filter(
                    UserLevel.user_id == user_id,
                    UserLevel.language_code == language_code
                ).first()
                return user_level and user_level.total_xp >= requirements["xp_earned"]
        
        return False
    
    async def _get_user_leaderboard_rank(self, user_id: int, language_code: str) -> int:
        """Get user's current leaderboard rank"""
        try:
            # Get user's score
            user_entry = self.db.query(Leaderboard).filter(
                Leaderboard.user_id == user_id,
                Leaderboard.language_code == language_code,
                Leaderboard.category == "weekly"
            ).first()
            
            if not user_entry:
                return 0
            
            # Count users with higher scores
            rank = self.db.query(func.count(Leaderboard.id)).filter(
                Leaderboard.language_code == language_code,
                Leaderboard.category == "weekly",
                Leaderboard.score > user_entry.score
            ).scalar()
            
            return rank + 1
            
        except Exception as e:
            logger.error(f"Error getting leaderboard rank: {e}")
            return 0
    
    async def update_leaderboard(self, user_id: int, language_code: str, points: int):
        """Update leaderboard with new points"""
        try:
            # Get or create leaderboard entry
            entry = self.db.query(Leaderboard).filter(
                Leaderboard.user_id == user_id,
                Leaderboard.language_code == language_code,
                Leaderboard.category == "weekly"
            ).first()
            
            if entry:
                entry.score += points
            else:
                # Create new entry
                now = datetime.utcnow()
                entry = Leaderboard(
                    user_id=user_id,
                    language_code=language_code,
                    category="weekly",
                    score=points,
                    period_start=now - timedelta(days=7),
                    period_end=now
                )
                self.db.add(entry)
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error updating leaderboard: {e}")
            self.db.rollback()
