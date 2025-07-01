import yaml
import os
from typing import Dict, Any
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://user:password@localhost/hapivet"
    redis_url: str = "redis://localhost:6379"
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""
    deepseek_api_key: str = ""
    sentry_dsn: str = ""
    secret_key: str = "your-secret-key-change-this"
    environment: str = "development"
    
    class Config:
        env_file = ".env"


class ConfigManager:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.settings = Settings()
        self._load_config()
    
    def _load_config(self):
        """Load configuration from YAML file"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as file:
                self.config = yaml.safe_load(file)
        else:
            self.config = {}
    
    def get_models(self) -> Dict[str, Any]:
        """Get all model configurations"""
        return self.config.get('models', {})
    
    def get_model_config(self, provider: str, model: str) -> Dict[str, Any]:
        """Get specific model configuration"""
        models = self.get_models()
        return models.get(provider, {}).get(model, {})
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration"""
        return self.config.get('monitoring', {})
    
    def get_cost_optimization_config(self) -> Dict[str, Any]:
        """Get cost optimization configuration"""
        return self.config.get('cost_optimization', {})
    
    def get_free_tier_limits(self) -> Dict[str, int]:
        """Get free tier limits for each provider"""
        cost_config = self.get_cost_optimization_config()
        return cost_config.get('free_tier_limits', {})


# Global config instance
config_manager = ConfigManager() 