import pytest
import os
from unittest.mock import patch
from src.utils.config import config_manager, Settings


class TestSettings:
    """Test the Settings configuration class"""
    
    def test_settings_defaults(self):
        """Test that settings have proper defaults"""
        with patch.dict(os.environ, {}):
            settings = Settings()
            assert settings.environment == "development"
            assert settings.database_url == "postgresql://user:password@localhost/hapivet"
            assert settings.redis_url == "redis://localhost:6379"
    
    def test_settings_from_env(self):
        """Test that settings can be loaded from environment variables"""
        test_env = {
            "OPENAI_API_KEY": "test_openai_key",
            "ANTHROPIC_API_KEY": "test_anthropic_key",
            "GOOGLE_API_KEY": "test_google_key",
            "DEEPSEEK_API_KEY": "test_deepseek_key",
            "ENVIRONMENT": "production",
            "DATABASE_URL": "postgresql://test:test@localhost/test",
            "REDIS_URL": "redis://test:6379",
            "SECRET_KEY": "test_secret_key"
        }
        
        with patch.dict(os.environ, test_env):
            settings = Settings()
            assert settings.openai_api_key == "test_openai_key"
            assert settings.anthropic_api_key == "test_anthropic_key"
            assert settings.google_api_key == "test_google_key"
            assert settings.deepseek_api_key == "test_deepseek_key"
            assert settings.environment == "production"
            assert settings.database_url == "postgresql://test:test@localhost/test"
            assert settings.redis_url == "redis://test:6379"
            assert settings.secret_key == "test_secret_key"


class TestConfigManager:
    """Test the configuration manager"""
    
    def test_config_manager_singleton(self):
        """Test that config_manager is a singleton"""
        from src.utils.config import config_manager as cm1
        from src.utils.config import config_manager as cm2
        assert cm1 is cm2
    
    def test_get_models(self):
        """Test getting models from config manager"""
        models = config_manager.get_models()
        assert isinstance(models, dict)
    
    def test_get_model_config(self):
        """Test getting specific model configuration"""
        config = config_manager.get_model_config("openai", "gpt-4")
        assert isinstance(config, dict)
    
    def test_get_monitoring_config(self):
        """Test getting monitoring configuration"""
        config = config_manager.get_monitoring_config()
        assert isinstance(config, dict) 