from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from collections import Counter
import logging

from app.models.database import Conversation, Message, ConversationAnalytics

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Customer Insight Analytics Service
    
    Provides deep insights into:
    - Conversation patterns
    - Sentiment trends
    - Intent distribution
    - Performance metrics
    - Cost analytics
    - Agent effectiveness
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def generate_daily_analytics(self, agent_id: str, date: datetime) -> Dict:
        """
        Generate comprehensive daily analytics for an agent
        
        This is the CORE analytics function that runs daily via Celery
        """
        logger.info(f"Generating analytics for agent {agent_id} on {date}")
        
        # Query all conversations for the day
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        query = select(Conversation).where(
            and_(
                Conversation.agent_id == agent_id,
                Conversation.started_at >= start_date,
                Conversation.started_at < end_date
            )
        )
        
        result = await self.db.execute(query)
        conversations = result.scalars().all()
        
        if not conversations:
            logger.warning(f"No conversations found for {agent_id} on {date}")
            return {}
        
        # Calculate all metrics
        analytics = {
            "agent_id": agent_id,
            "date": date.date(),
            **await self._calculate_volume_metrics(conversations),
            **await self._calculate_performance_metrics(conversations),
            **await self._calculate_sentiment_metrics(conversations),
            **await self._calculate_cost_metrics(conversations),
            **await self._calculate_intent_distribution(agent_id, start_date, end_date),
            **await self._calculate_channel_distribution(conversations)
        }
        
        # Save to database
        await self._save_analytics(analytics)
        
        return analytics
    
    async def _calculate_volume_metrics(self, conversations: List[Conversation]) -> Dict:
        """Calculate conversation volume metrics"""
        total_conversations = len(conversations)
        total_messages = sum(conv.total_messages or 0 for conv in conversations)
        unique_visitors = len(set(conv.visitor_id for conv in conversations if conv.visitor_id))
        
        return {
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "unique_visitors": unique_visitors,
            "avg_messages_per_conversation": total_messages / total_conversations if total_conversations > 0 else 0
        }
    
    async def _calculate_performance_metrics(self, conversations: List[Conversation]) -> Dict:
        """Calculate performance metrics"""
        # First response time
        first_response_times = [c.first_response_time for c in conversations if c.first_response_time]
        avg_first_response = np.mean(first_response_times) if first_response_times else 0
        
        # Average response time
        avg_response_times = [c.avg_response_time for c in conversations if c.avg_response_time]
        avg_response = np.mean(avg_response_times) if avg_response_times else 0
        
        # Resolution rate
        resolved = sum(1 for c in conversations if c.status == "resolved")
        resolution_rate = (resolved / len(conversations) * 100) if conversations else 0
        
        # Escalation rate
        escalated = sum(1 for c in conversations if c.status == "escalated")
        escalation_rate = (escalated / len(conversations) * 100) if conversations else 0
        
        # Conversation duration
        durations = []
        for conv in conversations:
            if conv.ended_at and conv.started_at:
                duration = (conv.ended_at - conv.started_at).total_seconds()
                durations.append(duration)
        
        avg_duration = np.mean(durations) if durations else 0
        
        return {
            "avg_first_response_time": int(avg_first_response),
            "avg_conversation_duration": int(avg_duration),
            "resolution_rate": round(resolution_rate, 2),
            "escalation_rate": round(escalation_rate, 2),
            "avg_response_time": int(avg_response)
        }
    
    async def _calculate_sentiment_metrics(self, conversations: List[Conversation]) -> Dict:
        """Calculate sentiment distribution"""
        sentiments = [c.sentiment_score for c in conversations if c.sentiment_score is not None]
        
        if not sentiments:
            return {
                "avg_sentiment_score": 0.0,
                "positive_conversations": 0,
                "neutral_conversations": 0,
                "negative_conversations": 0,
                "sentiment_distribution": {}
            }
        
        avg_sentiment = np.mean(sentiments)
        
        # Classify sentiments (0.0 to 1.0 scale)
        positive = sum(1 for s in sentiments if s > 0.6)
        neutral = sum(1 for s in sentiments if 0.4 <= s <= 0.6)
        negative = sum(1 for s in sentiments if s < 0.4)
        
        return {
            "avg_sentiment_score": round(avg_sentiment, 3),
            "positive_conversations": positive,
            "neutral_conversations": neutral,
            "negative_conversations": negative,
            "sentiment_distribution": {
                "positive": f"{positive / len(sentiments) * 100:.1f}%",
                "neutral": f"{neutral / len(sentiments) * 100:.1f}%",
                "negative": f"{negative / len(sentiments) * 100:.1f}%"
            }
        }
    
    async def _calculate_cost_metrics(self, conversations: List[Conversation]) -> Dict:
        """Calculate cost analytics"""
        total_cost = sum(c.total_cost_usd or 0 for c in conversations)
        
        cost_per_conversation = total_cost / len(conversations) if conversations else 0
        
        return {
            "total_cost_usd": round(total_cost, 2),
            "cost_per_conversation": round(cost_per_conversation, 4)
        }
    
    async def _calculate_intent_distribution(
        self,
        agent_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """Calculate intent distribution from messages"""
        
        # Query messages with intents
        query = select(Message).join(Conversation).where(
            and_(
                Conversation.agent_id == agent_id,
                Message.created_at >= start_date,
                Message.created_at < end_date,
                Message.intent.isnot(None),
                Message.role == "user"
            )
        )
        
        result = await self.db.execute(query)
        messages = result.scalars().all()
        
        if not messages:
            return {"top_intents": {}}
        
        # Count intents
        intents = [msg.intent for msg in messages]
        intent_counts = Counter(intents)
        
        # Get top 10 intents
        top_intents = dict(intent_counts.most_common(10))
        
        return {"top_intents": top_intents}
    
    async def _calculate_channel_distribution(self, conversations: List[Conversation]) -> Dict:
        """Calculate channel distribution"""
        channels = [c.channel for c in conversations]
        channel_counts = Counter(channels)
        
        total = len(conversations)
        channel_distribution = {
            channel: {
                "count": count,
                "percentage": f"{count / total * 100:.1f}%"
            }
            for channel, count in channel_counts.items()
        }
        
        return {"channel_distribution": channel_distribution}
    
    async def _save_analytics(self, analytics: Dict):
        """Save analytics to database"""
        analytics_record = ConversationAnalytics(**analytics)
        self.db.add(analytics_record)
        await self.db.commit()
    
    # ============================================
    # REAL-TIME ANALYTICS QUERIES
    # ============================================
    
    async def get_realtime_dashboard(self, agent_id: str, hours: int = 24) -> Dict:
        """
        Get real-time dashboard metrics for last N hours
        """
        since = datetime.utcnow() - timedelta(hours=hours)
        
        query = select(Conversation).where(
            and_(
                Conversation.agent_id == agent_id,
                Conversation.started_at >= since
            )
        )
        
        result = await self.db.execute(query)
        conversations = result.scalars().all()
        
        active_conversations = sum(1 for c in conversations if c.status == "active")
        
        return {
            "period_hours": hours,
            "active_conversations": active_conversations,
            "total_conversations": len(conversations),
            "total_messages": sum(c.total_messages or 0 for c in conversations),
            "avg_sentiment": np.mean([c.sentiment_score for c in conversations if c.sentiment_score]) if conversations else 0,
            "recent_conversations": [
                {
                    "id": str(c.id),
                    "status": c.status,
                    "started_at": c.started_at.isoformat(),
                    "sentiment": c.sentiment_score,
                    "messages": c.total_messages
                }
                for c in sorted(conversations, key=lambda x: x.started_at, reverse=True)[:10]
            ]
        }
    
    async def get_trend_analysis(self, agent_id: str, days: int = 30) -> Dict:
        """
        Analyze trends over time period
        """
        start_date = (datetime.utcnow() - timedelta(days=days)).date()
        
        query = select(ConversationAnalytics).where(
            and_(
                ConversationAnalytics.agent_id == agent_id,
                ConversationAnalytics.date >= start_date
            )
        ).order_by(ConversationAnalytics.date)
        
        result = await self.db.execute(query)
        analytics = result.scalars().all()
        
        if not analytics:
            return {"trends": []}
        
        # Convert to dataframe for easier analysis
        df = pd.DataFrame([
            {
                "date": a.date,
                "conversations": a.total_conversations,
                "messages": a.total_messages,
                "sentiment": a.avg_sentiment_score,
                "resolution_rate": a.resolution_rate,
                "cost": float(a.total_cost_usd)
            }
            for a in analytics
        ])
        
        # Calculate trends
        trends = {
            "daily_data": df.to_dict('records'),
            "summary": {
                "total_conversations": int(df['conversations'].sum()),
                "total_messages": int(df['messages'].sum()),
                "avg_sentiment": round(df['sentiment'].mean(), 3),
                "avg_resolution_rate": round(df['resolution_rate'].mean(), 2),
                "total_cost": round(df['cost'].sum(), 2),
                "cost_trend": self._calculate_trend(df['cost'].tolist()),
                "volume_trend": self._calculate_trend(df['conversations'].tolist()),
                "sentiment_trend": self._calculate_trend(df['sentiment'].tolist())
            }
        }
        
        return trends
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return "stable"
        
        first_half = np.mean(values[:len(values)//2])
        second_half = np.mean(values[len(values)//2:])
        
        change_pct = ((second_half - first_half) / first_half * 100) if first_half > 0 else 0
        
        if change_pct > 10:
            return "increasing"
        elif change_pct < -10:
            return "decreasing"
        else:
            return "stable"
    
    async def get_top_performers(self, agent_id: str, metric: str = "resolution_rate") -> Dict:
        """
        Identify best performing time periods or channels
        """
        query = select(ConversationAnalytics).where(
            ConversationAnalytics.agent_id == agent_id
        ).order_by(desc(getattr(ConversationAnalytics, metric))).limit(10)
        
        result = await self.db.execute(query)
        top_days = result.scalars().all()
        
        return {
            "metric": metric,
            "top_days": [
                {
                    "date": str(day.date),
                    "value": getattr(day, metric),
                    "conversations": day.total_conversations
                }
                for day in top_days
            ]
        }
    
    async def get_cost_breakdown(self, agent_id: str, days: int = 30) -> Dict:
        """
        Detailed cost analytics by model usage
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Query messages with cost data
        query = select(
            Message.model_used,
            func.count(Message.id).label('count'),
            func.sum(Message.cost_usd).label('total_cost'),
            func.sum(Message.tokens_used).label('total_tokens')
        ).join(Conversation).where(
            and_(
                Conversation.agent_id == agent_id,
                Message.created_at >= start_date,
                Message.model_used.isnot(None)
            )
        ).group_by(Message.model_used)
        
        result = await self.db.execute(query)
        model_costs = result.all()
        
        cost_breakdown = {
            "models": [
                {
                    "model": row.model_used,
                    "requests": row.count,
                    "total_cost": float(row.total_cost) if row.total_cost else 0,
                    "total_tokens": row.total_tokens or 0,
                    "avg_cost_per_request": float(row.total_cost / row.count) if row.count > 0 and row.total_cost else 0
                }
                for row in model_costs
            ],
            "total_cost": sum(float(row.total_cost) for row in model_costs if row.total_cost),
            "total_requests": sum(row.count for row in model_costs)
        }
        
        return cost_breakdown
