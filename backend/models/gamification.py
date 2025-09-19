from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from backend.database import Base

class Achievement(Base):
    """Achievement definitions"""
    __tablename__ = 'achievements'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String, nullable=True)
    category = Column(String, nullable=False)  # 'streak', 'level', 'milestone', 'special'
    requirements = Column(JSON, nullable=False)  # Criteria for earning
    points = Column(Integer, default=0)
    rarity = Column(String, default='common')  # 'common', 'rare', 'epic', 'legendary'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserAchievement(Base):
    """User's earned achievements"""
    __tablename__ = 'user_achievements'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    achievement_id = Column(Integer, ForeignKey('achievements.id'), nullable=False)
    earned_at = Column(DateTime, default=datetime.utcnow)
    progress = Column(Integer, default=100)  # Progress percentage
    
    # Relationships
    user = relationship("User", back_populates="user_achievements")
    achievement = relationship("Achievement")

class UserStreak(Base):
    """User learning streaks"""
    __tablename__ = 'user_streaks'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    language_code = Column(String, nullable=False)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_activity = Column(DateTime, default=datetime.utcnow)
    streak_freeze_count = Column(Integer, default=0)  # Freeze tokens available
    
    # Relationships
    user = relationship("User", back_populates="user_streaks")

class UserLevel(Base):
    """User levels and XP"""
    __tablename__ = 'user_levels'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    language_code = Column(String, nullable=False)
    current_level = Column(Integer, default=1)
    total_xp = Column(Integer, default=0)
    xp_to_next_level = Column(Integer, default=100)
    level_progress = Column(Float, default=0.0)  # Percentage to next level
    
    # Relationships
    user = relationship("User", back_populates="user_levels")

class Leaderboard(Base):
    """Leaderboard entries"""
    __tablename__ = 'leaderboards'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    language_code = Column(String, nullable=False)
    category = Column(String, nullable=False)  # 'weekly', 'monthly', 'all_time', 'streak'
    score = Column(Integer, default=0)
    rank = Column(Integer, nullable=True)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="leaderboard_entries")

class DailyChallenge(Base):
    """Daily challenges"""
    __tablename__ = 'daily_challenges'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    language_code = Column(String, nullable=False)
    challenge_type = Column(String, nullable=False)  # 'vocabulary', 'grammar', 'conversation', 'listening'
    difficulty = Column(String, default='medium')  # 'easy', 'medium', 'hard'
    requirements = Column(JSON, nullable=False)  # What needs to be completed
    reward_xp = Column(Integer, default=50)
    reward_points = Column(Integer, default=10)
    is_active = Column(Boolean, default=True)
    date = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

class UserDailyChallenge(Base):
    """User's daily challenge progress"""
    __tablename__ = 'user_daily_challenges'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    challenge_id = Column(Integer, ForeignKey('daily_challenges.id'), nullable=False)
    progress = Column(Integer, default=0)  # Progress percentage
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="user_daily_challenges")
    challenge = relationship("DailyChallenge")

class UserReward(Base):
    """User rewards and virtual items"""
    __tablename__ = 'user_rewards'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    reward_type = Column(String, nullable=False)  # 'xp', 'points', 'streak_freeze', 'avatar', 'theme'
    reward_value = Column(Integer, nullable=False)
    reward_data = Column(JSON, nullable=True)  # Additional reward data
    source = Column(String, nullable=False)  # 'achievement', 'daily_challenge', 'level_up', 'purchase'
    earned_at = Column(DateTime, default=datetime.utcnow)
    is_used = Column(Boolean, default=False)
    used_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="user_rewards")

# Update User model to include relationships
def add_gamification_relationships():
    """Add gamification relationships to User model"""
    # This would be added to the existing User model
    pass
