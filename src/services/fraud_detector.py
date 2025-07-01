import redis
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from src.utils.types import UsageAlert, AlertType, Severity
from src.utils.config import config_manager
from src.utils.logger import LoggerMixin
import json
import hashlib


class FraudDetector(LoggerMixin):
    """Detects fraudulent API usage patterns"""
    
    def __init__(self):
        self.redis_client = redis.from_url(config_manager.settings.redis_url)
        self.monitoring_config = config_manager.get_monitoring_config()
        self.fraud_threshold = self.monitoring_config.get('fraud_threshold', 10000)
        
        # Fraud detection patterns
        self.suspicious_patterns = {
            'rapid_requests': {'threshold': 100, 'window': 300},  # 100 requests in 5 minutes
            'high_token_usage': {'threshold': 50000, 'window': 3600},  # 50k tokens in 1 hour
            'unusual_hours': {'start_hour': 2, 'end_hour': 6},  # 2 AM to 6 AM
            'multiple_ips': {'threshold': 5, 'window': 3600},  # 5 different IPs in 1 hour
        }
    
    def analyze_request(self, user_id: str, request_data: Dict[str, Any]) -> List[UsageAlert]:
        """Analyze a single request for fraud indicators"""
        alerts = []
        
        try:
            # Check for rapid requests
            if self._check_rapid_requests(user_id):
                alerts.append(UsageAlert(
                    type=AlertType.FRAUD,
                    user_id=user_id,
                    message="Rapid request pattern detected - possible automated abuse",
                    severity=Severity.HIGH,
                    timestamp=datetime.utcnow()
                ))
            
            # Check for high token usage
            tokens_used = request_data.get('tokens_used', 0)
            if tokens_used > self.suspicious_patterns['high_token_usage']['threshold']:
                alerts.append(UsageAlert(
                    type=AlertType.FRAUD,
                    user_id=user_id,
                    message=f"Unusually high token usage: {tokens_used} tokens",
                    severity=Severity.HIGH,
                    timestamp=datetime.utcnow()
                ))
            
            # Check for unusual hours
            current_hour = datetime.utcnow().hour
            if (current_hour >= self.suspicious_patterns['unusual_hours']['start_hour'] and 
                current_hour <= self.suspicious_patterns['unusual_hours']['end_hour']):
                alerts.append(UsageAlert(
                    type=AlertType.ABNORMAL,
                    user_id=user_id,
                    message=f"Request made during unusual hours: {current_hour}:00 UTC",
                    severity=Severity.MEDIUM,
                    timestamp=datetime.utcnow()
                ))
            
            # Check for multiple IP addresses
            ip_address = request_data.get('ip_address')
            if ip_address and self._check_multiple_ips(user_id, ip_address):
                alerts.append(UsageAlert(
                    type=AlertType.FRAUD,
                    user_id=user_id,
                    message="Multiple IP addresses detected - possible account sharing",
                    severity=Severity.HIGH,
                    timestamp=datetime.utcnow()
                ))
            
        except Exception as e:
            self.log_error(e, {"user_id": user_id, "request_data": request_data})
        
        return alerts
    
    def _check_rapid_requests(self, user_id: str) -> bool:
        """Check if user is making requests too rapidly"""
        try:
            window = self.suspicious_patterns['rapid_requests']['window']
            threshold = self.suspicious_patterns['rapid_requests']['threshold']
            
            # Get request count in the time window
            key = f"requests:{user_id}:{datetime.utcnow().strftime('%Y-%m-%d:%H:%M')}"
            request_count = self.redis_client.get(key)
            
            if request_count:
                request_count = int(request_count)
            else:
                request_count = 0
            
            # Increment request count
            request_count += 1
            self.redis_client.setex(key, window, request_count)
            
            return request_count > threshold
            
        except Exception as e:
            self.log_error(e, {"user_id": user_id})
            return False
    
    def _check_multiple_ips(self, user_id: str, ip_address: str) -> bool:
        """Check if user is accessing from multiple IP addresses"""
        try:
            window = self.suspicious_patterns['multiple_ips']['window']
            threshold = self.suspicious_patterns['multiple_ips']['threshold']
            
            key = f"ips:{user_id}:{datetime.utcnow().strftime('%Y-%m-%d:%H')}"
            
            # Get existing IPs
            ips_data = self.redis_client.get(key)
            if ips_data:
                ips = json.loads(ips_data)
            else:
                ips = []
            
            # Add current IP if not already present
            if ip_address not in ips:
                ips.append(ip_address)
                self.redis_client.setex(key, window, json.dumps(ips))
            
            return len(ips) > threshold
            
        except Exception as e:
            self.log_error(e, {"user_id": user_id, "ip_address": ip_address})
            return False
    
    def get_user_risk_score(self, user_id: str) -> Dict[str, Any]:
        """Calculate risk score for a user"""
        try:
            risk_factors = []
            risk_score = 0
            
            # Check recent alerts
            alerts_key = f"alerts:{user_id}:{datetime.utcnow().strftime('%Y-%m-%d')}"
            alert_count = self.redis_client.get(alerts_key)
            if alert_count:
                alert_count = int(alert_count)
                if alert_count > 5:
                    risk_factors.append("High number of alerts")
                    risk_score += 30
            
            # Check usage patterns
            usage_key = f"usage:{user_id}:{datetime.utcnow().strftime('%Y-%m-%d')}"
            usage_data = self.redis_client.get(usage_key)
            if usage_data:
                usage = json.loads(usage_data)
                if usage.get('total_tokens', 0) > 100000:
                    risk_factors.append("High token usage")
                    risk_score += 25
                
                if usage.get('request_count', 0) > 1000:
                    risk_factors.append("High request count")
                    risk_score += 20
            
            # Check for unusual patterns
            if self._check_rapid_requests(user_id):
                risk_factors.append("Rapid request pattern")
                risk_score += 25
            
            # Determine risk level
            if risk_score >= 70:
                risk_level = "HIGH"
            elif risk_score >= 40:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
            
            return {
                'user_id': user_id,
                'risk_score': risk_score,
                'risk_level': risk_level,
                'risk_factors': risk_factors,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.log_error(e, {"user_id": user_id})
            return {
                'user_id': user_id,
                'risk_score': 0,
                'risk_level': 'UNKNOWN',
                'risk_factors': [],
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_suspicious_users(self) -> List[Dict[str, Any]]:
        """Get list of users with suspicious activity"""
        try:
            suspicious_users = []
            current_time = datetime.utcnow()
            
            # Scan for users with recent alerts
            pattern = f"alerts:*:{current_time.strftime('%Y-%m-%d')}"
            keys = self.redis_client.keys(pattern)
            
            for key in keys:
                user_id = key.split(':')[1]
                alert_count = self.redis_client.get(key)
                
                if alert_count and int(alert_count) > 3:
                    risk_score = self.get_user_risk_score(user_id)
                    if risk_score['risk_level'] in ['MEDIUM', 'HIGH']:
                        suspicious_users.append(risk_score)
            
            return suspicious_users
            
        except Exception as e:
            self.log_error(e)
            return []
    
    def block_user(self, user_id: str, reason: str) -> bool:
        """Block a user due to suspicious activity"""
        try:
            block_key = f"blocked:{user_id}"
            block_data = {
                'user_id': user_id,
                'reason': reason,
                'blocked_at': datetime.utcnow().isoformat(),
                'blocked_by': 'fraud_detector'
            }
            
            # Block for 24 hours
            self.redis_client.setex(block_key, 86400, json.dumps(block_data))
            
            self.logger.warning(f"User {user_id} blocked due to: {reason}")
            return True
            
        except Exception as e:
            self.log_error(e, {"user_id": user_id, "reason": reason})
            return False
    
    def is_user_blocked(self, user_id: str) -> bool:
        """Check if a user is currently blocked"""
        try:
            block_key = f"blocked:{user_id}"
            return self.redis_client.exists(block_key) > 0
            
        except Exception as e:
            self.log_error(e, {"user_id": user_id})
            return False 