import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
# Note: Social models were not implemented in the consolidated models.py
# This service will need to be updated when social features are implemented
# from backend.models import (
#     StudyGroup, StudyGroupMember, StudySession, StudySessionParticipant,
#     PeerMatch, PeerConversation, MentorshipProgram, MentorshipSession,
#     ContentShare, ContentLike, ContentComment, LanguageExchange, LanguageExchangeMatch
# )
from backend.database import get_db

logger = logging.getLogger(__name__)

class SocialLearningService:
    """Service for social learning features"""
    
    def __init__(self):
        self.db = next(get_db())
    
    # Study Groups
    async def create_study_group(self, user_id: int, name: str, description: str,
                               language_code: str, max_members: int = 10,
                               is_public: bool = True) -> Dict:
        """Create a new study group"""
        try:
            group = StudyGroup(
                name=name,
                description=description,
                language_code=language_code,
                created_by=user_id,
                max_members=max_members,
                is_public=is_public
            )
            self.db.add(group)
            self.db.flush()  # Get the ID
            
            # Add creator as admin
            member = StudyGroupMember(
                group_id=group.id,
                user_id=user_id,
                role='admin'
            )
            self.db.add(member)
            self.db.commit()
            
            return {
                "id": group.id,
                "name": group.name,
                "description": group.description,
                "language_code": group.language_code,
                "max_members": group.max_members,
                "is_public": group.is_public,
                "created_at": group.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating study group: {e}")
            self.db.rollback()
            raise
    
    async def join_study_group(self, user_id: int, group_id: int) -> Dict:
        """Join a study group"""
        try:
            # Check if group exists and has space
            group = self.db.query(StudyGroup).filter(
                StudyGroup.id == group_id,
                StudyGroup.is_active == True
            ).first()
            
            if not group:
                return {"error": "Group not found"}
            
            # Check if user is already a member
            existing_member = self.db.query(StudyGroupMember).filter(
                StudyGroupMember.group_id == group_id,
                StudyGroupMember.user_id == user_id
            ).first()
            
            if existing_member:
                return {"error": "Already a member of this group"}
            
            # Check if group is full
            current_members = self.db.query(StudyGroupMember).filter(
                StudyGroupMember.group_id == group_id,
                StudyGroupMember.is_active == True
            ).count()
            
            if current_members >= group.max_members:
                return {"error": "Group is full"}
            
            # Add member
            member = StudyGroupMember(
                group_id=group_id,
                user_id=user_id,
                role='member'
            )
            self.db.add(member)
            self.db.commit()
            
            return {"success": True, "message": "Successfully joined group"}
            
        except Exception as e:
            logger.error(f"Error joining study group: {e}")
            self.db.rollback()
            raise
    
    async def get_study_groups(self, language_code: str, user_id: int = None) -> List[Dict]:
        """Get available study groups"""
        try:
            query = self.db.query(StudyGroup).filter(
                StudyGroup.language_code == language_code,
                StudyGroup.is_active == True,
                StudyGroup.is_public == True
            )
            
            if user_id:
                # Exclude groups user is already in
                user_groups = self.db.query(StudyGroupMember.group_id).filter(
                    StudyGroupMember.user_id == user_id
                ).subquery()
                query = query.filter(~StudyGroup.id.in_(user_groups))
            
            groups = query.order_by(desc(StudyGroup.created_at)).limit(20).all()
            
            result = []
            for group in groups:
                member_count = self.db.query(StudyGroupMember).filter(
                    StudyGroupMember.group_id == group.id,
                    StudyGroupMember.is_active == True
                ).count()
                
                result.append({
                    "id": group.id,
                    "name": group.name,
                    "description": group.description,
                    "language_code": group.language_code,
                    "member_count": member_count,
                    "max_members": group.max_members,
                    "created_by": group.created_by,
                    "created_at": group.created_at.isoformat()
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting study groups: {e}")
            return []
    
    # Peer Matching
    async def find_peer_matches(self, user_id: int, learning_language: str,
                              native_language: str) -> List[Dict]:
        """Find potential peer matches for language exchange"""
        try:
            # Find users who want to learn the user's native language
            # and speak the language the user wants to learn
            matches = self.db.query(LanguageExchange).filter(
                LanguageExchange.user_id != user_id,
                LanguageExchange.learning_language == native_language,
                LanguageExchange.native_language == learning_language,
                LanguageExchange.is_active == True
            ).limit(10).all()
            
            result = []
            for match in matches:
                # Calculate compatibility score
                compatibility = await self._calculate_compatibility(user_id, match.user_id)
                
                result.append({
                    "user_id": match.user_id,
                    "user_name": match.user.name if match.user else "Unknown",
                    "native_language": match.native_language,
                    "learning_language": match.learning_language,
                    "proficiency_level": match.proficiency_level,
                    "interests": match.interests or [],
                    "compatibility_score": compatibility,
                    "avatar": match.user.avatar if match.user else None
                })
            
            # Sort by compatibility score
            result.sort(key=lambda x: x["compatibility_score"], reverse=True)
            return result
            
        except Exception as e:
            logger.error(f"Error finding peer matches: {e}")
            return []
    
    async def create_peer_match(self, user1_id: int, user2_id: int,
                              user1_language: str, user2_language: str) -> Dict:
        """Create a peer match between two users"""
        try:
            # Check if match already exists
            existing = self.db.query(PeerMatch).filter(
                or_(
                    and_(PeerMatch.user1_id == user1_id, PeerMatch.user2_id == user2_id),
                    and_(PeerMatch.user1_id == user2_id, PeerMatch.user2_id == user1_id)
                )
            ).first()
            
            if existing:
                return {"error": "Match already exists"}
            
            # Calculate compatibility
            compatibility = await self._calculate_compatibility(user1_id, user2_id)
            
            # Create match
            match = PeerMatch(
                user1_id=user1_id,
                user2_id=user2_id,
                user1_language=user1_language,
                user2_language=user2_language,
                compatibility_score=compatibility,
                expires_at=datetime.utcnow() + timedelta(days=7)
            )
            self.db.add(match)
            self.db.commit()
            
            return {
                "id": match.id,
                "user1_id": user1_id,
                "user2_id": user2_id,
                "compatibility_score": compatibility,
                "expires_at": match.expires_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating peer match: {e}")
            self.db.rollback()
            raise
    
    # Content Sharing
    async def share_content(self, user_id: int, content_type: str, title: str,
                          description: str, content_data: Dict, language_code: str,
                          difficulty_level: str = "medium", tags: List[str] = None) -> Dict:
        """Share content with the community"""
        try:
            content = ContentShare(
                user_id=user_id,
                content_type=content_type,
                title=title,
                description=description,
                content_data=content_data,
                language_code=language_code,
                difficulty_level=difficulty_level,
                tags=tags or []
            )
            self.db.add(content)
            self.db.commit()
            
            return {
                "id": content.id,
                "title": content.title,
                "description": content.description,
                "content_type": content.content_type,
                "language_code": content.language_code,
                "difficulty_level": content.difficulty_level,
                "tags": content.tags,
                "created_at": content.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error sharing content: {e}")
            self.db.rollback()
            raise
    
    async def get_shared_content(self, language_code: str, content_type: str = None,
                               difficulty_level: str = None, limit: int = 20) -> List[Dict]:
        """Get shared content from the community"""
        try:
            query = self.db.query(ContentShare).filter(
                ContentShare.language_code == language_code,
                ContentShare.is_public == True
            )
            
            if content_type:
                query = query.filter(ContentShare.content_type == content_type)
            
            if difficulty_level:
                query = query.filter(ContentShare.difficulty_level == difficulty_level)
            
            content = query.order_by(desc(ContentShare.created_at)).limit(limit).all()
            
            result = []
            for item in content:
                result.append({
                    "id": item.id,
                    "title": item.title,
                    "description": item.description,
                    "content_type": item.content_type,
                    "language_code": item.language_code,
                    "difficulty_level": item.difficulty_level,
                    "tags": item.tags,
                    "likes_count": item.likes_count,
                    "shares_count": item.shares_count,
                    "author_name": item.user.name if item.user else "Unknown",
                    "created_at": item.created_at.isoformat()
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting shared content: {e}")
            return []
    
    async def like_content(self, user_id: int, content_id: int) -> Dict:
        """Like or unlike shared content"""
        try:
            # Check if already liked
            existing_like = self.db.query(ContentLike).filter(
                ContentLike.user_id == user_id,
                ContentLike.content_id == content_id
            ).first()
            
            content = self.db.query(ContentShare).filter(
                ContentShare.id == content_id
            ).first()
            
            if not content:
                return {"error": "Content not found"}
            
            if existing_like:
                # Unlike
                self.db.delete(existing_like)
                content.likes_count = max(0, content.likes_count - 1)
                action = "unliked"
            else:
                # Like
                like = ContentLike(user_id=user_id, content_id=content_id)
                self.db.add(like)
                content.likes_count += 1
                action = "liked"
            
            self.db.commit()
            
            return {
                "action": action,
                "likes_count": content.likes_count
            }
            
        except Exception as e:
            logger.error(f"Error liking content: {e}")
            self.db.rollback()
            raise
    
    # Mentorship Program
    async def create_mentorship_request(self, mentee_id: int, mentor_id: int,
                                      language_code: str, goals: List[str]) -> Dict:
        """Create a mentorship request"""
        try:
            # Check if mentorship already exists
            existing = self.db.query(MentorshipProgram).filter(
                MentorshipProgram.mentee_id == mentee_id,
                MentorshipProgram.mentor_id == mentor_id,
                MentorshipProgram.language_code == language_code
            ).first()
            
            if existing:
                return {"error": "Mentorship request already exists"}
            
            program = MentorshipProgram(
                mentee_id=mentee_id,
                mentor_id=mentor_id,
                language_code=language_code,
                goals=goals,
                status='pending'
            )
            self.db.add(program)
            self.db.commit()
            
            return {
                "id": program.id,
                "mentee_id": mentee_id,
                "mentor_id": mentor_id,
                "language_code": language_code,
                "goals": goals,
                "status": "pending",
                "created_at": program.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating mentorship request: {e}")
            self.db.rollback()
            raise
    
    async def get_mentorship_requests(self, user_id: int, role: str = "mentee") -> List[Dict]:
        """Get mentorship requests for a user"""
        try:
            if role == "mentee":
                programs = self.db.query(MentorshipProgram).filter(
                    MentorshipProgram.mentee_id == user_id
                ).all()
            else:
                programs = self.db.query(MentorshipProgram).filter(
                    MentorshipProgram.mentor_id == user_id
                ).all()
            
            result = []
            for program in programs:
                result.append({
                    "id": program.id,
                    "mentee_id": program.mentee_id,
                    "mentor_id": program.mentor_id,
                    "language_code": program.language_code,
                    "goals": program.goals,
                    "status": program.status,
                    "start_date": program.start_date.isoformat() if program.start_date else None,
                    "created_at": program.created_at.isoformat()
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting mentorship requests: {e}")
            return []
    
    # Study Sessions
    async def create_study_session(self, group_id: int, title: str, description: str,
                                 session_type: str, language_code: str,
                                 scheduled_at: datetime, duration_minutes: int = 30,
                                 max_participants: int = 6, created_by: int = None) -> Dict:
        """Create a study session"""
        try:
            session = StudySession(
                group_id=group_id,
                title=title,
                description=description,
                session_type=session_type,
                language_code=language_code,
                scheduled_at=scheduled_at,
                duration_minutes=duration_minutes,
                max_participants=max_participants,
                created_by=created_by
            )
            self.db.add(session)
            self.db.commit()
            
            return {
                "id": session.id,
                "title": session.title,
                "description": session.description,
                "session_type": session.session_type,
                "language_code": session.language_code,
                "scheduled_at": session.scheduled_at.isoformat(),
                "duration_minutes": session.duration_minutes,
                "max_participants": session.max_participants,
                "created_at": session.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating study session: {e}")
            self.db.rollback()
            raise
    
    async def join_study_session(self, user_id: int, session_id: int) -> Dict:
        """Join a study session"""
        try:
            # Check if session exists and has space
            session = self.db.query(StudySession).filter(
                StudySession.id == session_id,
                StudySession.is_active == True
            ).first()
            
            if not session:
                return {"error": "Session not found"}
            
            # Check if user is already participating
            existing = self.db.query(StudySessionParticipant).filter(
                StudySessionParticipant.session_id == session_id,
                StudySessionParticipant.user_id == user_id
            ).first()
            
            if existing:
                return {"error": "Already participating in this session"}
            
            # Check if session is full
            current_participants = self.db.query(StudySessionParticipant).filter(
                StudySessionParticipant.session_id == session_id
            ).count()
            
            if current_participants >= session.max_participants:
                return {"error": "Session is full"}
            
            # Add participant
            participant = StudySessionParticipant(
                session_id=session_id,
                user_id=user_id
            )
            self.db.add(participant)
            self.db.commit()
            
            return {"success": True, "message": "Successfully joined session"}
            
        except Exception as e:
            logger.error(f"Error joining study session: {e}")
            self.db.rollback()
            raise
    
    async def _calculate_compatibility(self, user1_id: int, user2_id: int) -> int:
        """Calculate compatibility score between two users"""
        # This is a simplified compatibility calculation
        # In a real implementation, this would consider:
        # - Learning goals
        # - Availability
        # - Interests
        # - Proficiency levels
        # - Previous interactions
        
        # For now, return a random score between 60-100
        import random
        return random.randint(60, 100)
