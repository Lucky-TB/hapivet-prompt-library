import redis
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from src.utils.types import AIModel
from src.utils.config import config_manager
from src.utils.logger import LoggerMixin
import json


class CostOptimizer(LoggerMixin):
    """Optimizes costs by managing free tier limits and model rotation"""
    
    def __init__(self):
        self.redis_client = redis.from_url(config_manager.settings.redis_url)
        self.free_tier_limits = config_manager.get_free_tier_limits()
        self.monthly_usage = {}
        self._load_monthly_usage()
    
    def _load_monthly_usage(self):
        """Load current monthly usage from Redis"""
        current_month = datetime.utcnow().strftime('%Y-%m')
        
        for provider in self.free_tier_limits.keys():
            key = f"monthly_usage:{provider}:{current_month}"
            try:
                usage_data = self.redis_client.get(key)
                
                if usage_data:
                    self.monthly_usage[provider] = json.loads(usage_data)
                else:
                    self.monthly_usage[provider] = {
                        'tokens_used': 0,
                        'cost': 0.0,
                        'requests': 0
                    }
            except Exception as e:
                # If Redis is not available, use in-memory storage
                self.monthly_usage[provider] = {
                    'tokens_used': 0,
                    'cost': 0.0,
                    'requests': 0
                }
    
    def record_usage(self, provider: str, tokens: int, cost: float) -> None:
        """Record usage for cost optimization"""
        try:
            current_month = datetime.utcnow().strftime('%Y-%m')
            key = f"monthly_usage:{provider}:{current_month}"
            
            # Update usage
            if provider not in self.monthly_usage:
                self.monthly_usage[provider] = {
                    'tokens_used': 0,
                    'cost': 0.0,
                    'requests': 0
                }
            
            self.monthly_usage[provider]['tokens_used'] += tokens
            self.monthly_usage[provider]['cost'] += cost
            self.monthly_usage[provider]['requests'] += 1
            
            # Store in Redis (if available)
            try:
                self.redis_client.setex(key, 2592000, json.dumps(self.monthly_usage[provider]))  # 30 days
            except Exception as e:
                # If Redis is not available, just use in-memory storage
                pass
            
        except Exception as e:
            self.log_error(e, {"provider": provider, "tokens": tokens, "cost": cost})
    
    def get_remaining_free_tier(self, provider: str) -> Dict[str, Any]:
        """Get remaining free tier limits for a provider"""
        try:
            if provider not in self.free_tier_limits:
                return {'tokens_remaining': 0, 'percentage_used': 100}
            
            limit = self.free_tier_limits[provider]
            used = self.monthly_usage.get(provider, {}).get('tokens_used', 0)
            remaining = max(0, limit - used)
            percentage_used = (used / limit) * 100 if limit > 0 else 100
            
            return {
                'tokens_remaining': remaining,
                'percentage_used': percentage_used,
                'tokens_used': used,
                'limit': limit
            }
            
        except Exception as e:
            self.log_error(e, {"provider": provider})
            return {'tokens_remaining': 0, 'percentage_used': 100}
    
    def is_free_tier_available(self, provider: str) -> bool:
        """Check if free tier is still available for a provider"""
        remaining = self.get_remaining_free_tier(provider)
        return remaining['tokens_remaining'] > 0
    
    def optimize_model_selection(self, available_models: List[AIModel], estimated_tokens: int) -> List[AIModel]:
        """Optimize model selection based on cost and free tier availability"""
        try:
            optimized_models = []
            
            for model in available_models:
                provider = model.provider
                
                # Check if this model is free
                if model.cost_per_1k_tokens == 0:
                    # Check if free tier is available
                    if self.is_free_tier_available(provider):
                        optimized_models.append(model)
                    else:
                        # Free tier exhausted, but still consider it if no other options
                        optimized_models.append(model)
                else:
                    # Paid model, always consider it
                    optimized_models.append(model)
            
            # Sort by cost (free models first, then by cost)
            optimized_models.sort(key=lambda m: (m.cost_per_1k_tokens > 0, m.cost_per_1k_tokens))
            
            return optimized_models
            
        except Exception as e:
            self.log_error(e, {"estimated_tokens": estimated_tokens})
            return available_models
    
    def get_cost_analysis(self) -> Dict[str, Any]:
        """Get comprehensive cost analysis"""
        try:
            analysis = {
                'monthly_usage': {},
                'free_tier_status': {},
                'total_cost': 0.0,
                'total_tokens': 0,
                'recommendations': []
            }
            
            for provider in self.free_tier_limits.keys():
                usage = self.monthly_usage.get(provider, {})
                remaining = self.get_remaining_free_tier(provider)
                
                analysis['monthly_usage'][provider] = usage
                analysis['free_tier_status'][provider] = remaining
                analysis['total_cost'] += usage.get('cost', 0.0)
                analysis['total_tokens'] += usage.get('tokens_used', 0)
                
                # Generate recommendations
                if remaining['percentage_used'] > 80:
                    analysis['recommendations'].append(
                        f"Free tier for {provider} is {remaining['percentage_used']:.1f}% used. "
                        f"Consider switching to paid models soon."
                    )
                
                if usage.get('cost', 0.0) > 10.0:  # More than $10
                    analysis['recommendations'].append(
                        f"High cost detected for {provider}: ${usage.get('cost', 0.0):.2f}. "
                        f"Consider optimizing usage patterns."
                    )
            
            return analysis
            
        except Exception as e:
            self.log_error(e)
            return {}
    
    def get_provider_ranking(self) -> List[Dict[str, Any]]:
        """Get providers ranked by cost efficiency"""
        try:
            rankings = []
            
            for provider in self.free_tier_limits.keys():
                usage = self.monthly_usage.get(provider, {})
                remaining = self.get_remaining_free_tier(provider)
                
                # Calculate efficiency score (lower is better)
                efficiency_score = usage.get('cost', 0.0)
                if remaining['tokens_remaining'] > 0:
                    efficiency_score *= 0.5  # Bonus for having free tier available
                
                rankings.append({
                    'provider': provider,
                    'cost': usage.get('cost', 0.0),
                    'tokens_used': usage.get('tokens_used', 0),
                    'free_tier_remaining': remaining['tokens_remaining'],
                    'efficiency_score': efficiency_score
                })
            
            # Sort by efficiency score
            rankings.sort(key=lambda x: x['efficiency_score'])
            
            return rankings
            
        except Exception as e:
            self.log_error(e)
            return []
    
    def reset_monthly_usage(self, provider: Optional[str] = None) -> None:
        """Reset monthly usage (useful for testing or manual reset)"""
        try:
            current_month = datetime.utcnow().strftime('%Y-%m')
            
            if provider:
                key = f"monthly_usage:{provider}:{current_month}"
                self.redis_client.delete(key)
                if provider in self.monthly_usage:
                    self.monthly_usage[provider] = {
                        'tokens_used': 0,
                        'cost': 0.0,
                        'requests': 0
                    }
            else:
                # Reset all providers
                for provider in self.free_tier_limits.keys():
                    key = f"monthly_usage:{provider}:{current_month}"
                    self.redis_client.delete(key)
                
                self.monthly_usage = {}
                self._load_monthly_usage()
            
            self.logger.info(f"Reset monthly usage for {provider or 'all providers'}")
            
        except Exception as e:
            self.log_error(e, {"provider": provider}) 