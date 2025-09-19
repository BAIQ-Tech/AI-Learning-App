from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from backend.services.analytics_service import AnalyticsService
from backend.main import get_current_user
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

# Initialize analytics service
analytics_service = AnalyticsService()

@router.get("/insights/{language_code}")
async def get_learning_insights(
    language_code: str,
    period_days: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive learning insights for a user"""
    try:
        insights = await analytics_service.get_learning_insights(
            user_id=current_user["id"],
            language_code=language_code,
            period_days=period_days
        )
        return insights
    except Exception as e:
        logger.error(f"Error getting learning insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to get learning insights")

@router.get("/activity/{language_code}")
async def get_learning_activity(
    language_code: str,
    current_user: dict = Depends(get_current_user)
):
    """Get learning activity summary"""
    try:
        from datetime import datetime, timedelta
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        activity = await analytics_service.get_learning_activity(
            user_id=current_user["id"],
            language_code=language_code,
            start_date=start_date,
            end_date=end_date
        )
        return activity
    except Exception as e:
        logger.error(f"Error getting learning activity: {e}")
        raise HTTPException(status_code=500, detail="Failed to get learning activity")

@router.get("/progress-trends/{language_code}")
async def get_progress_trends(
    language_code: str,
    current_user: dict = Depends(get_current_user)
):
    """Get progress trends over time"""
    try:
        from datetime import datetime, timedelta
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        trends = await analytics_service.get_progress_trends(
            user_id=current_user["id"],
            language_code=language_code,
            start_date=start_date,
            end_date=end_date
        )
        return trends
    except Exception as e:
        logger.error(f"Error getting progress trends: {e}")
        raise HTTPException(status_code=500, detail="Failed to get progress trends")

@router.get("/strengths-weaknesses/{language_code}")
async def get_strengths_weaknesses(
    language_code: str,
    current_user: dict = Depends(get_current_user)
):
    """Get analysis of user's strengths and weaknesses"""
    try:
        analysis = await analytics_service.analyze_strengths_weaknesses(
            user_id=current_user["id"],
            language_code=language_code
        )
        return analysis
    except Exception as e:
        logger.error(f"Error getting strengths and weaknesses: {e}")
        raise HTTPException(status_code=500, detail="Failed to get strengths and weaknesses analysis")

@router.get("/learning-patterns/{language_code}")
async def get_learning_patterns(
    language_code: str,
    current_user: dict = Depends(get_current_user)
):
    """Get analysis of user's learning patterns"""
    try:
        from datetime import datetime, timedelta
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        patterns = await analytics_service.analyze_learning_patterns(
            user_id=current_user["id"],
            language_code=language_code,
            start_date=start_date,
            end_date=end_date
        )
        return patterns
    except Exception as e:
        logger.error(f"Error getting learning patterns: {e}")
        raise HTTPException(status_code=500, detail="Failed to get learning patterns")

@router.get("/recommendations/{language_code}")
async def get_recommendations(
    language_code: str,
    current_user: dict = Depends(get_current_user)
):
    """Get personalized learning recommendations"""
    try:
        from datetime import datetime, timedelta
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        # Get activity data for recommendations
        activity_data = await analytics_service.get_learning_activity(
            user_id=current_user["id"],
            language_code=language_code,
            start_date=start_date,
            end_date=end_date
        )
        
        recommendations = await analytics_service.generate_recommendations(
            user_id=current_user["id"],
            language_code=language_code,
            activity_data=activity_data
        )
        return {"recommendations": recommendations}
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")

@router.get("/dashboard/{language_code}")
async def get_dashboard_data(
    language_code: str,
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive dashboard data"""
    try:
        from datetime import datetime, timedelta
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        # Get all analytics data
        activity_data = await analytics_service.get_learning_activity(
            user_id=current_user["id"],
            language_code=language_code,
            start_date=start_date,
            end_date=end_date
        )
        
        progress_trends = await analytics_service.get_progress_trends(
            user_id=current_user["id"],
            language_code=language_code,
            start_date=start_date,
            end_date=end_date
        )
        
        strengths_weaknesses = await analytics_service.analyze_strengths_weaknesses(
            user_id=current_user["id"],
            language_code=language_code
        )
        
        learning_patterns = await analytics_service.analyze_learning_patterns(
            user_id=current_user["id"],
            language_code=language_code,
            start_date=start_date,
            end_date=end_date
        )
        
        recommendations = await analytics_service.generate_recommendations(
            user_id=current_user["id"],
            language_code=language_code,
            activity_data=activity_data
        )
        
        return {
            "language_code": language_code,
            "period_days": 30,
            "generated_at": datetime.utcnow().isoformat(),
            "activity": activity_data,
            "progress_trends": progress_trends,
            "strengths_weaknesses": strengths_weaknesses,
            "learning_patterns": learning_patterns,
            "recommendations": recommendations
        }
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard data")
