import redis
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from src.utils.types import TokenUsage, UsageAlert, AlertType, Severity
from src.utils.config import config_manager
from src.utils.logger import LoggerMixin
from src.utils.database import db_manager
from collections import defaultdict
import json


class UsageMonitor(LoggerMixin):
    """Monitors token usage and detects anomalies"""
    
    def __init__(self):
        self.redis_client = redis.from_url(config_manager.settings.redis_url)
        self.monitoring_config = config_manager.get_monitoring_config()
        self.spike_threshold = self.monitoring_config.get('spike_threshold', 1000)
        self.fraud_threshold = self.monitoring_config.get('fraud_threshold', 10000)
        self.alert_cooldown = self.monitoring_config.get('alert_cooldown', 3600)
    
    def record_usage(self, usage: TokenUsage) -> None:
        """Record token usage for monitoring"""
        try:
            # Store in Redis for fast access
            key = f"usage:{usage.user_id}:{usage.model_id}:{datetime.utcnow().strftime('%Y-%m-%d:%H')}"
            current_usage = self.redis_client.get(key)
            
            if current_usage:
                current_usage = int(current_usage)
            else:
                current_usage = 0
            
            new_usage = current_usage + usage.tokens_used
            self.redis_client.setex(key, 3600, new_usage)  # Expire in 1 hour
            
            # Store in database
            with db_manager.get_session() as session:
                from src.utils.database import Request
                db_request = Request(
                    user_id=int(usage.user_id),
                    model_used=usage.model_id,
                    prompt="",  # We don't store the actual prompt for privacy
                    response="",
                    tokens_used=usage.tokens_used,
                    cost=usage.cost
                )
                session.add(db_request)
                session.commit()
            
            # Check for anomalies
            self._check_for_anomalies(usage.user_id, usage.model_id, new_usage)
            
        except Exception as e:
            self.log_error(e, {"user_id": usage.user_id, "model_id": usage.model_id})
    
    def _check_for_anomalies(self, user_id: str, model_id: str, current_usage: int) -> None:
        """Check for usage anomalies and generate alerts"""
        try:
            # Check for spike in usage
            if current_usage > self.spike_threshold:
                self._create_alert(
                    user_id=user_id,
                    alert_type=AlertType.SPIKE,
                    message=f"Token usage spike detected: {current_usage} tokens in the last hour",
                    severity=Severity.MEDIUM
                )
            
            # Check for potential fraud
            if current_usage > self.fraud_threshold:
                self._create_alert(
                    user_id=user_id,
                    alert_type=AlertType.FRAUD,
                    message=f"Unusually high token usage detected: {current_usage} tokens in the last hour",
                    severity=Severity.HIGH
                )
            
            # Check for abnormal patterns
            self._check_abnormal_patterns(user_id, model_id, current_usage)
            
        except Exception as e:
            self.log_error(e, {"user_id": user_id, "model_id": model_id})
    
    def _check_abnormal_patterns(self, user_id: str, model_id: str, current_usage: int) -> None:
        """Check for abnormal usage patterns"""
        try:
            # Get historical usage for this user
            historical_key = f"historical:{user_id}:{model_id}"
            historical_data = self.redis_client.get(historical_key)
            
            if historical_data:
                historical_usage = json.loads(historical_data)
                avg_usage = sum(historical_usage) / len(historical_usage)
                
                # Check if current usage is significantly higher than average
                if current_usage > avg_usage * 3:  # 3x the average
                    self._create_alert(
                        user_id=user_id,
                        alert_type=AlertType.ABNORMAL,
                        message=f"Abnormal usage pattern detected: {current_usage} vs avg {avg_usage:.0f}",
                        severity=Severity.MEDIUM
                    )
            
            # Update historical data
            if historical_data:
                historical_usage = json.loads(historical_data)
            else:
                historical_usage = []
            
            historical_usage.append(current_usage)
            # Keep only last 24 hours of data
            if len(historical_usage) > 24:
                historical_usage = historical_usage[-24:]
            
            self.redis_client.setex(historical_key, 86400, json.dumps(historical_usage))  # Expire in 24 hours
            
        except Exception as e:
            self.log_error(e, {"user_id": user_id, "model_id": model_id})
    
    def _create_alert(self, user_id: str, alert_type: AlertType, message: str, severity: Severity) -> None:
        """Create and store a usage alert"""
        try:
            # Check if we already have a recent alert for this user and type
            alert_key = f"alert:{user_id}:{alert_type.value}"
            if self.redis_client.exists(alert_key):
                return  # Alert already exists, don't create duplicate
            
            # Create alert
            alert = UsageAlert(
                type=alert_type,
                user_id=user_id,
                message=message,
                severity=severity,
                timestamp=datetime.utcnow()
            )
            
            # Store in database
            with db_manager.get_session() as session:
                from src.utils.database import UsageAlert as DBUsageAlert
                db_alert = DBUsageAlert(
                    user_id=int(user_id),
                    alert_type=alert.type.value,
                    message=alert.message,
                    severity=alert.severity.value
                )
                session.add(db_alert)
                session.commit()
            
            # Set cooldown in Redis
            self.redis_client.setex(alert_key, self.alert_cooldown, "1")
            
            # Log the alert
            self.log_alert(alert_type.value, user_id, message, severity.value)
            
        except Exception as e:
            self.log_error(e, {"user_id": user_id, "alert_type": alert_type.value})
    
    def get_user_usage(self, user_id: str, hours: int = 24) -> Dict[str, Any]:
        """Get usage statistics for a user"""
        try:
            usage_data = {}
            current_time = datetime.utcnow()
            
            for hour in range(hours):
                time_key = (current_time - timedelta(hours=hour)).strftime('%Y-%m-%d:%H')
                
                # Get usage for all models
                for model_id in ['openai-gpt-4', 'openai-gpt-3.5-turbo', 'anthropic-claude-3', 'google-gemini-pro', 'deepseek-deepseek-chat', 'deepseek-deepseek-coder']:
                    key = f"usage:{user_id}:{model_id}:{time_key}"
                    usage = self.redis_client.get(key)
                    if usage:
                        if model_id not in usage_data:
                            usage_data[model_id] = []
                        usage_data[model_id].append(int(usage))
            
            # Calculate statistics
            stats = {}
            for model_id, usage_list in usage_data.items():
                if usage_list:
                    stats[model_id] = {
                        'total_tokens': sum(usage_list),
                        'average_tokens': sum(usage_list) / len(usage_list),
                        'max_tokens': max(usage_list),
                        'usage_count': len(usage_list)
                    }
            
            return stats
            
        except Exception as e:
            self.log_error(e, {"user_id": user_id})
            return {}
    
    def get_active_alerts(self, user_id: Optional[str] = None) -> List[UsageAlert]:
        """Get active alerts"""
        try:
            with db_manager.get_session() as session:
                from src.utils.database import UsageAlert as DBUsageAlert
                
                query = session.query(DBUsageAlert)
                if user_id:
                    query = query.filter(DBUsageAlert.user_id == int(user_id))
                
                # Get alerts from last 24 hours
                yesterday = datetime.utcnow() - timedelta(days=1)
                query = query.filter(DBUsageAlert.created_at >= yesterday)
                
                db_alerts = query.all()
                
                alerts = []
                for db_alert in db_alerts:
                    alert = UsageAlert(
                        type=AlertType(db_alert.alert_type),
                        user_id=str(db_alert.user_id),
                        message=db_alert.message,
                        severity=Severity(db_alert.severity),
                        timestamp=db_alert.created_at
                    )
                    alerts.append(alert)
                
                return alerts
                
        except Exception as e:
            self.log_error(e, {"user_id": user_id})
            return [] 