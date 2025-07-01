import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from src.services.model_manager import ModelManager
from src.services.cost_optimizer import CostOptimizer
from src.services.fraud_detector import FraudDetector
from src.services.prompt_optimizer import PromptOptimizer
from src.services.usage_monitor import UsageMonitor
from src.utils.types import PromptRequest, PromptResponse, AIModel


class TestModelManager:
    """Test the model manager service"""
    
    @pytest.fixture
    def model_manager(self):
        """Create a model manager instance for testing"""
        return ModelManager()
    
    def test_model_manager_initialization(self, model_manager):
        """Test model manager initialization"""
        assert len(model_manager.models) > 0
        assert 'openai-gpt-4' in model_manager.models
        assert 'anthropic-claude-3' in model_manager.models
        assert 'google-gemini-pro' in model_manager.models
        assert 'deepseek-deepseek-chat' in model_manager.models
    
    @pytest.mark.asyncio
    async def test_get_best_model_auto(self, model_manager):
        """Test automatic model selection"""
        # Test coding prompt
        coding_prompt = "Write a Python function to sort a list"
        model = await model_manager.get_best_model(coding_prompt, "auto")
        assert model is not None
        assert "deepseek" in model.model_id or "gpt" in model.model_id
        
        # Test creative prompt
        creative_prompt = "Write a poem about technology"
        model = await model_manager.get_best_model(creative_prompt, "auto")
        assert model is not None
        assert "claude" in model.model_id or "gpt" in model.model_id
    
    @pytest.mark.asyncio
    async def test_get_best_model_specific(self, model_manager):
        """Test specific model selection"""
        model = await model_manager.get_best_model("test", "openai-gpt-4")
        assert model.model_id == "openai-gpt-4"
    
    @pytest.mark.asyncio
    async def test_get_best_model_invalid(self, model_manager):
        """Test invalid model selection"""
        with pytest.raises(ValueError):
            await model_manager.get_best_model("test", "invalid-model")
    
    @pytest.mark.asyncio
    async def test_generate_response(self, model_manager):
        """Test response generation"""
        with patch.object(model_manager.models['openai-gpt-4'], 'generate') as mock_generate:
            mock_response = ModelResponse(
                content="Test response",
                tokens_used=10,
                model_id="openai-gpt-4",
                cost=0.001
            )
            mock_generate.return_value = mock_response
            
            request = PromptRequest(
                prompt="Test prompt",
                model_preference="openai-gpt-4",
                max_tokens=100
            )
            
            response = await model_manager.generate_response(request)
            assert response.content == "Test response"
            assert response.model_id == "openai-gpt-4"


class TestCostOptimizer:
    """Test the cost optimizer service"""
    
    @pytest.fixture
    def cost_optimizer(self):
        """Create a cost optimizer instance for testing"""
        return CostOptimizer()
    
    def test_cost_optimizer_initialization(self, cost_optimizer):
        """Test cost optimizer initialization"""
        assert cost_optimizer.free_tier_limits is not None
        assert 'openai' in cost_optimizer.free_tier_limits
        assert 'anthropic' in cost_optimizer.free_tier_limits
    
    def test_calculate_cost(self, cost_optimizer):
        """Test cost calculation"""
        cost = cost_optimizer.calculate_cost('openai', 1000)
        assert isinstance(cost, float)
        assert cost >= 0
    
    def test_is_within_free_tier(self, cost_optimizer):
        """Test free tier checking"""
        # Test within limits
        assert cost_optimizer.is_within_free_tier('openai', 100) is True
        
        # Test exceeding limits
        assert cost_optimizer.is_within_free_tier('openai', 1000000) is False
    
    def test_get_optimal_model(self, cost_optimizer):
        """Test optimal model selection"""
        models = [
            Mock(provider='openai', cost_per_1k_tokens=0.03),
            Mock(provider='anthropic', cost_per_1k_tokens=0.015),
            Mock(provider='google', cost_per_1k_tokens=0.0)
        ]
        
        optimal = cost_optimizer.get_optimal_model(models, 1000)
        assert optimal.provider == 'google'  # Should be free
    
    def test_record_usage(self, cost_optimizer):
        """Test usage recording"""
        cost_optimizer.record_usage('openai', 100, 0.003)
        assert cost_optimizer.monthly_usage['openai']['tokens_used'] == 100
        assert cost_optimizer.monthly_usage['openai']['cost'] == 0.003


class TestFraudDetector:
    """Test the fraud detector service"""
    
    @pytest.fixture
    def fraud_detector(self):
        """Create a fraud detector instance for testing"""
        return FraudDetector()
    
    def test_fraud_detector_initialization(self, fraud_detector):
        """Test fraud detector initialization"""
        assert fraud_detector.suspicious_patterns is not None
        assert len(fraud_detector.suspicious_patterns) > 0
    
    def test_detect_suspicious_patterns(self, fraud_detector):
        """Test suspicious pattern detection"""
        # Test normal prompt
        result = fraud_detector.detect_suspicious_patterns("Hello, how are you?")
        assert result.is_suspicious is False
        
        # Test suspicious prompt
        suspicious_prompt = "password" * 100  # Repeated pattern
        result = fraud_detector.detect_suspicious_patterns(suspicious_prompt)
        assert result.is_suspicious is True
    
    def test_detect_rate_limiting(self, fraud_detector):
        """Test rate limiting detection"""
        user_id = "test_user"
        
        # Test normal usage
        for _ in range(5):
            result = fraud_detector.check_rate_limit(user_id)
            assert result.is_allowed is True
        
        # Test excessive usage
        for _ in range(100):
            result = fraud_detector.check_rate_limit(user_id)
            if not result.is_allowed:
                break
        else:
            pytest.fail("Rate limiting should have been triggered")
    
    def test_detect_token_abuse(self, fraud_detector):
        """Test token abuse detection"""
        # Test normal token usage
        result = fraud_detector.detect_token_abuse(1000)
        assert result.is_suspicious is False
        
        # Test excessive token usage
        result = fraud_detector.detect_token_abuse(100000)
        assert result.is_suspicious is True


class TestPromptOptimizer:
    """Test the prompt optimizer service"""
    
    @pytest.fixture
    def prompt_optimizer(self):
        """Create a prompt optimizer instance for testing"""
        return PromptOptimizer()
    
    def test_prompt_optimizer_initialization(self, prompt_optimizer):
        """Test prompt optimizer initialization"""
        assert prompt_optimizer.model_adapters is not None
        assert len(prompt_optimizer.model_adapters) > 0
    
    def test_optimize_for_model(self, prompt_optimizer):
        """Test prompt optimization for specific models"""
        original_prompt = "Write a function to sort a list"
        
        # Test OpenAI optimization
        optimized = prompt_optimizer.optimize_for_model(original_prompt, "openai-gpt-4")
        assert optimized != original_prompt
        assert len(optimized) > 0
        
        # Test Anthropic optimization
        optimized = prompt_optimizer.optimize_for_model(original_prompt, "anthropic-claude-3")
        assert optimized != original_prompt
        assert len(optimized) > 0
    
    def test_optimize_for_capability(self, prompt_optimizer):
        """Test capability-based optimization"""
        coding_prompt = "Write a Python function"
        optimized = prompt_optimizer.optimize_for_capability(coding_prompt, "coding")
        assert "python" in optimized.lower() or "function" in optimized.lower()
        
        creative_prompt = "Write a story"
        optimized = prompt_optimizer.optimize_for_capability(creative_prompt, "creative")
        assert len(optimized) > len(creative_prompt)


class TestUsageMonitor:
    """Test the usage monitor service"""
    
    @pytest.fixture
    def usage_monitor(self):
        """Create a usage monitor instance for testing"""
        return UsageMonitor()
    
    def test_usage_monitor_initialization(self, usage_monitor):
        """Test usage monitor initialization"""
        assert usage_monitor.usage_data is not None
    
    def test_record_request(self, usage_monitor):
        """Test request recording"""
        user_id = "test_user"
        model_id = "openai-gpt-4"
        tokens = 100
        cost = 0.003
        
        usage_monitor.record_request(user_id, model_id, tokens, cost)
        
        assert user_id in usage_monitor.usage_data
        assert model_id in usage_monitor.usage_data[user_id]
        assert usage_monitor.usage_data[user_id][model_id]['tokens'] == tokens
        assert usage_monitor.usage_data[user_id][model_id]['cost'] == cost
    
    def test_get_user_usage(self, usage_monitor):
        """Test user usage retrieval"""
        user_id = "test_user"
        model_id = "openai-gpt-4"
        
        # Record some usage
        usage_monitor.record_request(user_id, model_id, 100, 0.003)
        usage_monitor.record_request(user_id, model_id, 200, 0.006)
        
        usage = usage_monitor.get_user_usage(user_id)
        assert usage['total_tokens'] == 300
        assert usage['total_cost'] == 0.009
    
    def test_detect_usage_spikes(self, usage_monitor):
        """Test usage spike detection"""
        user_id = "test_user"
        model_id = "openai-gpt-4"
        
        # Normal usage
        for _ in range(5):
            usage_monitor.record_request(user_id, model_id, 100, 0.003)
        
        # Spike usage
        for _ in range(50):
            usage_monitor.record_request(user_id, model_id, 1000, 0.03)
        
        spikes = usage_monitor.detect_usage_spikes()
        assert len(spikes) > 0
        assert user_id in [spike['user_id'] for spike in spikes]
    
    def test_get_model_usage_stats(self, usage_monitor):
        """Test model usage statistics"""
        # Record usage for different models
        usage_monitor.record_request("user1", "openai-gpt-4", 100, 0.003)
        usage_monitor.record_request("user2", "anthropic-claude-3", 200, 0.006)
        usage_monitor.record_request("user3", "google-gemini-pro", 150, 0.0)
        
        stats = usage_monitor.get_model_usage_stats()
        assert "openai-gpt-4" in stats
        assert "anthropic-claude-3" in stats
        assert "google-gemini-pro" in stats 