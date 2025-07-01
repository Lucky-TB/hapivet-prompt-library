import pytest
import os
import tempfile
from unittest.mock import Mock, patch
from src.utils.logger import setup_logging, get_logger
from src.utils.database import DatabaseManager
from src.utils.types import PromptRequest, PromptResponse, AIModel, UsageAlert
from datetime import datetime


class TestLogger:
    """Test logging functionality"""
    
    def test_setup_logging(self):
        """Test logging setup"""
        # Should not raise any exceptions
        setup_logging()
    
    def test_get_logger(self):
        """Test logger retrieval"""
        logger = get_logger("test_module")
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'debug')
    
    def test_logger_singleton(self):
        """Test that logger is a singleton"""
        logger1 = get_logger("test_module")
        logger2 = get_logger("test_module")
        assert logger1 is logger2
    
    def test_logger_different_modules(self):
        """Test that different modules get different loggers"""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")
        assert logger1 is not logger2


class TestDatabaseManager:
    """Test database management functionality"""
    
    @pytest.fixture
    def db_manager(self):
        """Create a database manager for testing"""
        # Use in-memory SQLite for testing
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        manager = DatabaseManager(f"sqlite:///{db_path}")
        yield manager
        
        # Cleanup
        os.unlink(db_path)
    
    def test_database_initialization(self, db_manager):
        """Test database initialization"""
        assert db_manager.engine is not None
        assert db_manager.SessionLocal is not None
    
    def test_create_tables(self, db_manager):
        """Test table creation"""
        # Should not raise any exceptions
        db_manager.create_tables()
    
    def test_get_session(self, db_manager):
        """Test session creation"""
        session = db_manager.get_session()
        assert session is not None
        session.close()
    
    def test_database_connection(self, db_manager):
        """Test database connection"""
        with db_manager.get_session() as session:
            # Should be able to execute a simple query
            result = session.execute("SELECT 1")
            assert result.scalar() == 1


class TestTypes:
    """Test data type definitions"""
    
    def test_prompt_response_creation(self):
        """Test PromptResponse creation"""
        response = PromptResponse(
            id="test-id",
            request_id="req-id",
            model_used="test-model",
            response="Test response",
            tokens_used=100,
            cost=0.001
        )
        assert response.response == "Test response"
        assert response.tokens_used == 100
        assert response.model_used == "test-model"
        assert response.cost == 0.001
    
    def test_ai_model_creation(self):
        """Test AIModel creation"""
        model = AIModel(
            id="test-model",
            name="Test Model",
            provider="test-provider",
            cost_per_1k_tokens=0.01,
            max_tokens=1000,
            capabilities=["text-generation"]
        )
        assert model.id == "test-model"
        assert model.name == "Test Model"
        assert model.provider == "test-provider"
        assert model.cost_per_1k_tokens == 0.01
        assert model.max_tokens == 1000
        assert model.capabilities == ["text-generation"]
    
    def test_prompt_request_creation(self):
        """Test PromptRequest creation"""
        request = PromptRequest(
            id="test-id",
            user_id="test-user",
            prompt="Test prompt",
            model_preference="auto",
            max_tokens=100
        )
        assert request.prompt == "Test prompt"
        assert request.model_preference == "auto"
        assert request.max_tokens == 100
    
    def test_prompt_request_defaults(self):
        """Test PromptRequest default values"""
        request = PromptRequest(
            id="test-id",
            user_id="test-user",
            prompt="Test prompt"
        )
        assert request.prompt == "Test prompt"
        assert request.model_preference is None
        assert request.max_tokens is None
    
    def test_usage_alert_creation(self):
        """Test UsageAlert creation"""
        from src.utils.types import AlertType, Severity
        alert = UsageAlert(
            type=AlertType.SPIKE,
            user_id="test-user",
            message="High usage detected",
            severity=Severity.HIGH
        )
        assert alert.type == AlertType.SPIKE
        assert alert.user_id == "test-user"
        assert alert.message == "High usage detected"
        assert alert.severity == Severity.HIGH


class TestTypeValidation:
    """Test type validation and constraints"""
    
    def test_prompt_request_validation(self):
        """Test PromptRequest validation"""
        # Valid request
        request = PromptRequest(
            id="test-id",
            user_id="test-user",
            prompt="Valid prompt",
            model_preference="auto",
            max_tokens=100
        )
        assert request is not None
        
        # Test empty prompt
        with pytest.raises(ValueError):
            PromptRequest(
                id="test-id",
                user_id="test-user",
                prompt="",  # Invalid: empty
                model_preference="auto",
                max_tokens=100
            )


class TestTypeSerialization:
    """Test type serialization and deserialization"""
    
    def test_prompt_response_serialization(self):
        """Test PromptResponse JSON serialization"""
        response = PromptResponse(
            id="test-id",
            request_id="req-id",
            model_used="test-model",
            response="Test content",
            tokens_used=100,
            cost=0.001
        )
        
        # Convert to dict
        data = response.dict()
        assert data["response"] == "Test content"
        assert data["tokens_used"] == 100
        assert data["model_used"] == "test-model"
        assert data["cost"] == 0.001
    
    def test_ai_model_serialization(self):
        """Test AIModel JSON serialization"""
        model = AIModel(
            id="test-model",
            name="Test Model",
            provider="test-provider",
            cost_per_1k_tokens=0.01,
            max_tokens=1000,
            capabilities=["text-generation"]
        )
        
        # Convert to dict
        data = model.dict()
        assert data["id"] == "test-model"
        assert data["name"] == "Test Model"
        assert data["provider"] == "test-provider"
        assert data["cost_per_1k_tokens"] == 0.01
        assert data["max_tokens"] == 1000
    
    def test_prompt_request_serialization(self):
        """Test PromptRequest JSON serialization"""
        request = PromptRequest(
            id="test-id",
            user_id="test-user",
            prompt="Test prompt",
            model_preference="auto",
            max_tokens=100
        )
        
        # Convert to dict
        data = request.dict()
        assert data["prompt"] == "Test prompt"
        assert data["model_preference"] == "auto"
        assert data["max_tokens"] == 100


class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_enum_values(self):
        """Test enum values"""
        from src.utils.types import AlertType, Severity, ModelCapability
        
        # Test AlertType
        assert AlertType.SPIKE == "spike"
        assert AlertType.ABNORMAL == "abnormal"
        assert AlertType.FRAUD == "fraud"
        
        # Test Severity
        assert Severity.LOW == "low"
        assert Severity.MEDIUM == "medium"
        assert Severity.HIGH == "high"
        
        # Test ModelCapability
        assert ModelCapability.TEXT_GENERATION == "text-generation"
        assert ModelCapability.REASONING == "reasoning"
        assert ModelCapability.CODING == "coding" 