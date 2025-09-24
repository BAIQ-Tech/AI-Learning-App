from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from backend.database import Base

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
    stories = relationship("Story", back_populates="author")
    comments = relationship("Comment", back_populates="author")
    story_likes = relationship("StoryLike", back_populates="user")
    
    # Gamification relationships
    user_achievements = relationship("UserAchievement", back_populates="user")
    user_streaks = relationship("UserStreak", back_populates="user")
    user_levels = relationship("UserLevel", back_populates="user")
    leaderboard_entries = relationship("Leaderboard", back_populates="user")
    user_daily_challenges = relationship("UserDailyChallenge", back_populates="user")
    user_rewards = relationship("UserReward", back_populates="user")

class UserProgress(Base):
    __tablename__ = 'user_progress'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    language_code = Column(String)
    lesson_id = Column(String)
    score = Column(Integer)
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="progress")

class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    language_code = Column(String)
    message = Column(Text)
    response = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="conversations")

class Lesson(Base):
    __tablename__ = 'lessons'
    
    id = Column(Integer, primary_key=True, index=True)
    language_code = Column(String)
    level = Column(String)
    topic = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Story(Base):
    __tablename__ = 'stories'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    language_code = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    author = relationship("User", back_populates="stories")
    comments = relationship("Comment", back_populates="story")
    likes = relationship("StoryLike", back_populates="story")

class Comment(Base):
    __tablename__ = 'comments'
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    story_id = Column(Integer, ForeignKey('stories.id'))
    author_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    story = relationship("Story", back_populates="comments")
    author = relationship("User", back_populates="comments")

class StoryLike(Base):
    __tablename__ = 'story_likes'
    
    story_id = Column(Integer, ForeignKey('stories.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    story = relationship("Story", back_populates="likes")
    user = relationship("User", back_populates="story_likes")

# Gamification Models
class Achievement(Base):
    """Achievement definitions"""
    __tablename__ = 'achievements'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String, nullable=True)
    category = Column(String, nullable=False)  # 'streak', 'level', 'milestone', 'special'
    requirements = Column(Text, nullable=False)  # JSON string of criteria for earning
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
    requirements = Column(Text, nullable=False)  # JSON string of what needs to be completed
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
    reward_data = Column(Text, nullable=True)  # JSON string of additional reward data
    source = Column(String, nullable=False)  # 'achievement', 'daily_challenge', 'level_up', 'purchase'
    earned_at = Column(DateTime, default=datetime.utcnow)
    is_used = Column(Boolean, default=False)
    used_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="user_rewards")
