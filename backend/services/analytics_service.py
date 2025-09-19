import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from backend.models import User, UserProgress, Conversation
from backend.models.gamification import UserLevel, UserStreak, UserAchievement
from backend.database import get_db

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Service for advanced analytics and learning insights"""
    
    def __init__(self):
        self.db = next(get_db())
    
    async def get_learning_insights(self, user_id: int, language_code: str, 
                                  period_days: int = 30) -> Dict:
        """Get comprehensive learning insights for a user"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period_days)
            
            # Get learning activity data
            activity_data = await self._get_learning_activity(user_id, language_code, start_date, end_date)
            
            # Get progress trends
            progress_trends = await self._get_progress_trends(user_id, language_code, start_date, end_date)
            
            # Get strength and weakness analysis
            strengths_weaknesses = await self._analyze_strengths_weaknesses(user_id, language_code)
            
            # Get learning patterns
            learning_patterns = await self._analyze_learning_patterns(user_id, language_code, start_date, end_date)
            
            # Get recommendations
            recommendations = await self._generate_recommendations(user_id, language_code, activity_data)
            
            return {
                "user_id": user_id,
                "language_code": language_code,
                "period_days": period_days,
                "generated_at": datetime.utcnow().isoformat(),
                "activity_summary": activity_data,
                "progress_trends": progress_trends,
                "strengths_weaknesses": strengths_weaknesses,
                "learning_patterns": learning_patterns,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error getting learning insights: {e}")
            return {}
    
    async def get_learning_activity(self, user_id: int, language_code: str,
                                  start_date: datetime, end_date: datetime) -> Dict:
        """Get learning activity summary"""
        try:
            # Get conversation data
            conversations = self.db.query(Conversation).filter(
                Conversation.user_id == user_id,
                Conversation.language_code == language_code,
                Conversation.timestamp >= start_date,
                Conversation.timestamp <= end_date
            ).all()
            
            # Get progress data
            progress_records = self.db.query(UserProgress).filter(
                UserProgress.user_id == user_id,
                UserProgress.timestamp >= start_date,
                UserProgress.timestamp <= end_date
            ).all()
            
            # Calculate metrics
            total_conversations = len(conversations)
            total_exercises = len(progress_records)
            avg_score = sum(p.score for p in progress_records) / max(len(progress_records), 1)
            
            # Calculate daily activity
            daily_activity = {}
            for conv in conversations:
                date = conv.timestamp.date()
                if date not in daily_activity:
                    daily_activity[date] = {"conversations": 0, "exercises": 0}
                daily_activity[date]["conversations"] += 1
            
            for prog in progress_records:
                date = prog.timestamp.date()
                if date not in daily_activity:
                    daily_activity[date] = {"conversations": 0, "exercises": 0}
                daily_activity[date]["exercises"] += 1
            
            return {
                "total_conversations": total_conversations,
                "total_exercises": total_exercises,
                "average_score": round(avg_score, 2),
                "daily_activity": daily_activity,
                "most_active_day": max(daily_activity.keys()) if daily_activity else None,
                "activity_consistency": self._calculate_consistency(daily_activity)
            }
            
        except Exception as e:
            logger.error(f"Error getting learning activity: {e}")
            return {}
    
    async def get_progress_trends(self, user_id: int, language_code: str,
                                start_date: datetime, end_date: datetime) -> Dict:
        """Analyze progress trends over time"""
        try:
            # Get weekly progress data
            weekly_progress = {}
            current_date = start_date
            
            while current_date <= end_date:
                week_end = min(current_date + timedelta(days=7), end_date)
                
                week_progress = self.db.query(UserProgress).filter(
                    UserProgress.user_id == user_id,
                    UserProgress.timestamp >= current_date,
                    UserProgress.timestamp <= week_end
                ).all()
                
                if week_progress:
                    avg_score = sum(p.score for p in week_progress) / len(week_progress)
                    weekly_progress[current_date.strftime("%Y-%m-%d")] = {
                        "average_score": round(avg_score, 2),
                        "total_exercises": len(week_progress),
                        "improvement": self._calculate_week_improvement(week_progress)
                    }
                
                current_date += timedelta(days=7)
            
            # Calculate overall trend
            trend = self._calculate_overall_trend(weekly_progress)
            
            return {
                "weekly_progress": weekly_progress,
                "overall_trend": trend,
                "improvement_rate": self._calculate_improvement_rate(weekly_progress)
            }
            
        except Exception as e:
            logger.error(f"Error getting progress trends: {e}")
            return {}
    
    async def analyze_strengths_weaknesses(self, user_id: int, language_code: str) -> Dict:
        """Analyze user's strengths and weaknesses"""
        try:
            # Get recent progress data
            recent_progress = self.db.query(UserProgress).filter(
                UserProgress.user_id == user_id
            ).order_by(desc(UserProgress.timestamp)).limit(50).all()
            
            if not recent_progress:
                return {"strengths": [], "weaknesses": []}
            
            # Analyze by category (this would be more sophisticated in practice)
            category_scores = {}
            for progress in recent_progress:
                category = progress.category or "general"
                if category not in category_scores:
                    category_scores[category] = []
                category_scores[category].append(progress.score)
            
            # Calculate average scores per category
            category_averages = {}
            for category, scores in category_scores.items():
                category_averages[category] = sum(scores) / len(scores)
            
            # Identify strengths and weaknesses
            overall_avg = sum(category_averages.values()) / len(category_averages)
            strengths = []
            weaknesses = []
            
            for category, avg_score in category_averages.items():
                if avg_score > overall_avg + 10:  # 10 points above average
                    strengths.append({
                        "category": category,
                        "average_score": round(avg_score, 2),
                        "performance": "above_average"
                    })
                elif avg_score < overall_avg - 10:  # 10 points below average
                    weaknesses.append({
                        "category": category,
                        "average_score": round(avg_score, 2),
                        "performance": "below_average"
                    })
            
            return {
                "strengths": strengths,
                "weaknesses": weaknesses,
                "overall_average": round(overall_avg, 2)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing strengths and weaknesses: {e}")
            return {"strengths": [], "weaknesses": []}
    
    async def analyze_learning_patterns(self, user_id: int, language_code: str,
                                      start_date: datetime, end_date: datetime) -> Dict:
        """Analyze user's learning patterns"""
        try:
            # Get conversation data
            conversations = self.db.query(Conversation).filter(
                Conversation.user_id == user_id,
                Conversation.language_code == language_code,
                Conversation.timestamp >= start_date,
                Conversation.timestamp <= end_date
            ).all()
            
            # Analyze time patterns
            hour_activity = {}
            day_activity = {}
            
            for conv in conversations:
                hour = conv.timestamp.hour
                day = conv.timestamp.strftime("%A")
                
                hour_activity[hour] = hour_activity.get(hour, 0) + 1
                day_activity[day] = day_activity.get(day, 0) + 1
            
            # Find peak learning times
            peak_hour = max(hour_activity.keys(), key=lambda h: hour_activity[h]) if hour_activity else None
            peak_day = max(day_activity.keys(), key=lambda d: day_activity[d]) if day_activity else None
            
            # Analyze session length patterns
            session_lengths = []
            current_session_start = None
            
            for conv in sorted(conversations, key=lambda c: c.timestamp):
                if current_session_start is None:
                    current_session_start = conv.timestamp
                else:
                    time_diff = (conv.timestamp - current_session_start).total_seconds() / 60
                    if time_diff > 30:  # 30 minutes gap = new session
                        session_lengths.append(time_diff)
                        current_session_start = conv.timestamp
            
            avg_session_length = sum(session_lengths) / max(len(session_lengths), 1) if session_lengths else 0
            
            return {
                "peak_learning_hour": peak_hour,
                "peak_learning_day": peak_day,
                "hour_distribution": hour_activity,
                "day_distribution": day_activity,
                "average_session_length_minutes": round(avg_session_length, 2),
                "total_sessions": len(session_lengths),
                "learning_consistency": self._calculate_learning_consistency(day_activity)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing learning patterns: {e}")
            return {}
    
    async def generate_recommendations(self, user_id: int, language_code: str,
                                     activity_data: Dict) -> List[Dict]:
        """Generate personalized learning recommendations"""
        try:
            recommendations = []
            
            # Get user level
            user_level = self.db.query(UserLevel).filter(
                UserLevel.user_id == user_id,
                UserLevel.language_code == language_code
            ).first()
            
            current_level = user_level.current_level if user_level else 1
            
            # Activity-based recommendations
            if activity_data.get("total_conversations", 0) < 5:
                recommendations.append({
                    "type": "activity",
                    "priority": "high",
                    "title": "Increase Conversation Practice",
                    "description": "Try to have at least one conversation per day to improve fluency",
                    "action": "Start a conversation with the AI tutor"
                })
            
            if activity_data.get("activity_consistency", 0) < 0.5:
                recommendations.append({
                    "type": "consistency",
                    "priority": "medium",
                    "title": "Build Learning Habit",
                    "description": "Consistent daily practice is key to language learning success",
                    "action": "Set a daily reminder for your learning time"
                })
            
            # Level-based recommendations
            if current_level < 5:
                recommendations.append({
                    "type": "foundation",
                    "priority": "high",
                    "title": "Focus on Vocabulary Building",
                    "description": "Build a strong vocabulary foundation with daily word practice",
                    "action": "Complete vocabulary exercises daily"
                })
            elif current_level < 10:
                recommendations.append({
                    "type": "intermediate",
                    "priority": "medium",
                    "title": "Practice Grammar Structures",
                    "description": "Work on complex grammar patterns to improve accuracy",
                    "action": "Complete grammar-focused lessons"
                })
            else:
                recommendations.append({
                    "type": "advanced",
                    "priority": "medium",
                    "title": "Engage in Real Conversations",
                    "description": "Practice with native speakers or advanced conversation topics",
                    "action": "Join study groups or find conversation partners"
                })
            
            # Performance-based recommendations
            avg_score = activity_data.get("average_score", 0)
            if avg_score < 60:
                recommendations.append({
                    "type": "performance",
                    "priority": "high",
                    "title": "Review Previous Lessons",
                    "description": "Your recent scores suggest reviewing earlier material would help",
                    "action": "Revisit beginner lessons to strengthen foundation"
                })
            elif avg_score > 85:
                recommendations.append({
                    "type": "challenge",
                    "priority": "low",
                    "title": "Take on Advanced Challenges",
                    "description": "You're doing great! Try more challenging exercises",
                    "action": "Attempt advanced conversation topics"
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    def _calculate_consistency(self, daily_activity: Dict) -> float:
        """Calculate learning consistency score"""
        if not daily_activity:
            return 0.0
        
        total_days = len(daily_activity)
        active_days = sum(1 for day_data in daily_activity.values() 
                         if day_data["conversations"] > 0 or day_data["exercises"] > 0)
        
        return active_days / total_days if total_days > 0 else 0.0
    
    def _calculate_week_improvement(self, week_progress: List) -> float:
        """Calculate improvement for a week"""
        if len(week_progress) < 2:
            return 0.0
        
        first_half = week_progress[:len(week_progress)//2]
        second_half = week_progress[len(week_progress)//2:]
        
        first_avg = sum(p.score for p in first_half) / len(first_half)
        second_avg = sum(p.score for p in second_half) / len(second_half)
        
        return second_avg - first_avg
    
    def _calculate_overall_trend(self, weekly_progress: Dict) -> str:
        """Calculate overall progress trend"""
        if len(weekly_progress) < 2:
            return "insufficient_data"
        
        scores = [week["average_score"] for week in weekly_progress.values()]
        first_half_avg = sum(scores[:len(scores)//2]) / (len(scores)//2)
        second_half_avg = sum(scores[len(scores)//2:]) / (len(scores) - len(scores)//2)
        
        improvement = second_half_avg - first_half_avg
        
        if improvement > 5:
            return "improving"
        elif improvement < -5:
            return "declining"
        else:
            return "stable"
    
    def _calculate_improvement_rate(self, weekly_progress: Dict) -> float:
        """Calculate rate of improvement"""
        if len(weekly_progress) < 2:
            return 0.0
        
        scores = [week["average_score"] for week in weekly_progress.values()]
        if len(scores) < 2:
            return 0.0
        
        # Simple linear regression slope
        n = len(scores)
        x_mean = (n - 1) / 2
        y_mean = sum(scores) / n
        
        numerator = sum((i - x_mean) * (scores[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        return numerator / denominator if denominator != 0 else 0.0
    
    def _calculate_learning_consistency(self, day_activity: Dict) -> float:
        """Calculate learning consistency across days of week"""
        if not day_activity:
            return 0.0
        
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        activity_by_day = [day_activity.get(day, 0) for day in days_of_week]
        
        # Calculate coefficient of variation (lower = more consistent)
        mean_activity = sum(activity_by_day) / len(activity_by_day)
        if mean_activity == 0:
            return 0.0
        
        variance = sum((activity - mean_activity) ** 2 for activity in activity_by_day) / len(activity_by_day)
        std_dev = variance ** 0.5
        coefficient_of_variation = std_dev / mean_activity
        
        # Convert to consistency score (0-1, higher is more consistent)
        return max(0, 1 - coefficient_of_variation)
