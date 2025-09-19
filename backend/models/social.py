from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.database import Base

class StudyGroup(Base):
    """Study groups for collaborative learning"""
    __tablename__ = 'study_groups'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    language_code = Column(String, nullable=False)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    max_members = Column(Integer, default=10)
    is_public = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    members = relationship("StudyGroupMember", back_populates="group")
    sessions = relationship("StudySession", back_populates="group")

class StudyGroupMember(Base):
    """Study group membership"""
    __tablename__ = 'study_group_members'
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey('study_groups.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    role = Column(String, default='member')  # 'admin', 'moderator', 'member'
    joined_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    group = relationship("StudyGroup", back_populates="members")
    user = relationship("User")

class StudySession(Base):
    """Study sessions within groups"""
    __tablename__ = 'study_sessions'
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey('study_groups.id'), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    session_type = Column(String, nullable=False)  # 'conversation', 'lesson', 'quiz', 'game'
    language_code = Column(String, nullable=False)
    scheduled_at = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, default=30)
    max_participants = Column(Integer, default=6)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    group = relationship("StudyGroup", back_populates="sessions")
    creator = relationship("User", foreign_keys=[created_by])
    participants = relationship("StudySessionParticipant", back_populates="session")

class StudySessionParticipant(Base):
    """Study session participants"""
    __tablename__ = 'study_session_participants'
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('study_sessions.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)
    left_at = Column(DateTime, nullable=True)
    participation_score = Column(Integer, default=0)
    
    # Relationships
    session = relationship("StudySession", back_populates="participants")
    user = relationship("User")

class PeerMatch(Base):
    """Peer matching for language exchange"""
    __tablename__ = 'peer_matches'
    
    id = Column(Integer, primary_key=True, index=True)
    user1_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user2_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user1_language = Column(String, nullable=False)  # Language user1 wants to learn
    user2_language = Column(String, nullable=False)  # Language user2 wants to learn
    compatibility_score = Column(Integer, default=0)
    status = Column(String, default='pending')  # 'pending', 'accepted', 'rejected', 'expired'
    created_at = Column(DateTime, default=datetime.utcnow)
    accepted_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    
    # Relationships
    user1 = relationship("User", foreign_keys=[user1_id])
    user2 = relationship("User", foreign_keys=[user2_id])
    conversations = relationship("PeerConversation", back_populates="match")

class PeerConversation(Base):
    """Conversations between matched peers"""
    __tablename__ = 'peer_conversations'
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey('peer_matches.id'), nullable=False)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    message = Column(Text, nullable=False)
    language_code = Column(String, nullable=False)
    message_type = Column(String, default='text')  # 'text', 'audio', 'image', 'video'
    media_url = Column(String, nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    match = relationship("PeerMatch", back_populates="conversations")
    sender = relationship("User")

class MentorshipProgram(Base):
    """Mentorship program for advanced learners"""
    __tablename__ = 'mentorship_programs'
    
    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    mentee_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    language_code = Column(String, nullable=False)
    status = Column(String, default='active')  # 'active', 'completed', 'paused', 'cancelled'
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    goals = Column(JSON, nullable=True)  # Learning goals
    progress_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    mentor = relationship("User", foreign_keys=[mentor_id])
    mentee = relationship("User", foreign_keys=[mentee_id])
    sessions = relationship("MentorshipSession", back_populates="program")

class MentorshipSession(Base):
    """Individual mentorship sessions"""
    __tablename__ = 'mentorship_sessions'
    
    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey('mentorship_programs.id'), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    session_type = Column(String, nullable=False)  # 'lesson', 'practice', 'review', 'assessment'
    scheduled_at = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=60)
    status = Column(String, default='scheduled')  # 'scheduled', 'completed', 'cancelled', 'rescheduled'
    notes = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    program = relationship("MentorshipProgram", back_populates="sessions")

class ContentShare(Base):
    """Shared content between users"""
    __tablename__ = 'content_shares'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content_type = Column(String, nullable=False)  # 'lesson', 'exercise', 'story', 'tip'
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    content_data = Column(JSON, nullable=False)
    language_code = Column(String, nullable=False)
    difficulty_level = Column(String, default='medium')
    tags = Column(JSON, nullable=True)  # Array of tags
    is_public = Column(Boolean, default=True)
    likes_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    likes = relationship("ContentLike", back_populates="content")
    comments = relationship("ContentComment", back_populates="content")

class ContentLike(Base):
    """Likes on shared content"""
    __tablename__ = 'content_likes'
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey('content_shares.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    content = relationship("ContentShare", back_populates="likes")
    user = relationship("User")

class ContentComment(Base):
    """Comments on shared content"""
    __tablename__ = 'content_comments'
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey('content_shares.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    comment = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    content = relationship("ContentShare", back_populates="comments")
    user = relationship("User")

class LanguageExchange(Base):
    """Language exchange matching"""
    __tablename__ = 'language_exchanges'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    native_language = Column(String, nullable=False)
    learning_language = Column(String, nullable=False)
    proficiency_level = Column(String, nullable=False)  # 'beginner', 'intermediate', 'advanced'
    availability = Column(JSON, nullable=True)  # Available time slots
    interests = Column(JSON, nullable=True)  # Topics of interest
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    matches = relationship("LanguageExchangeMatch", back_populates="exchange")

class LanguageExchangeMatch(Base):
    """Matches for language exchange"""
    __tablename__ = 'language_exchange_matches'
    
    id = Column(Integer, primary_key=True, index=True)
    exchange1_id = Column(Integer, ForeignKey('language_exchanges.id'), nullable=False)
    exchange2_id = Column(Integer, ForeignKey('language_exchanges.id'), nullable=False)
    compatibility_score = Column(Integer, default=0)
    status = Column(String, default='pending')  # 'pending', 'accepted', 'rejected'
    created_at = Column(DateTime, default=datetime.utcnow)
    accepted_at = Column(DateTime, nullable=True)
    
    # Relationships
    exchange1 = relationship("LanguageExchange", foreign_keys=[exchange1_id])
    exchange2 = relationship("LanguageExchange", foreign_keys=[exchange2_id])
    exchange = relationship("LanguageExchange")
