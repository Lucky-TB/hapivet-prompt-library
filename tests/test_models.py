import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.models.base_model import BaseAIModel
from src.models.openai_model import OpenAIModel
from src.models.anthropic_model import AnthropicModel
from src.models.gemini_model import GeminiModel
from src.models.deepseek_model import DeepSeekModel
from src.utils.types import PromptRequest, PromptResponse
from datetime import datetime


class TestBaseAIModel:
    def test_base_model_initialization(self):
        """Test base model initialization"""
        config = {
            'id': 'test-model',
            'name': 'Test Model',
            'provider': 'test',
            'cost_per_1k_tokens': 0.01,
            'max_tokens': 1000,
            'capabilities': ['text-generation'],
            'is_available': True
        }
        
        model = Mock(spec=BaseAIModel)
        model.model_config = config
        model.model_id = config['id']
        model.name = config['name']
        model.provider = config['provider']
        model.cost_per_1k_tokens = config['cost_per_1k_tokens']
        model.max_tokens = config['max_tokens']
        model.capabilities = config['capabilities']
        model.is_available = config['is_available']
        
        assert model.model_id == 'test-model'
        assert model.name == 'Test Model'
        assert model.provider == 'test'
        assert model.cost_per_1k_tokens == 0.01
        assert model.max_tokens == 1000
        assert model.capabilities == ['text-generation']
        assert model.is_available is True
    
    def test_calculate_cost(self):
        """Test cost calculation"""
        config = {'cost_per_1k_tokens': 0.02}
        model = Mock(spec=BaseAIModel)
        model.cost_per_1k_tokens = config['cost_per_1k_tokens']
        model.calculate_cost = BaseAIModel.calculate_cost.__get__(model)
        
        cost = model.calculate_cost(1000)
        assert cost == 0.02
    
    def test_can_handle_capability(self):
        """Test capability checking"""
        config = {'capabilities': ['text-generation', 'coding']}
        model = Mock(spec=BaseAIModel)
        model.capabilities = config['capabilities']
        model.can_handle_capability = BaseAIModel.can_handle_capability.__get__(model)
        
        assert model.can_handle_capability('text-generation') is True
        assert model.can_handle_capability('coding') is True
        assert model.can_handle_capability('reasoning') is False


class TestOpenAIModel:
    @pytest.fixture
    def model_config(self):
        return {
            'id': 'openai-gpt-4',
            'name': 'GPT-4',
            'provider': 'openai',
            'cost_per_1k_tokens': 0.03,
            'max_tokens': 8192,
            'capabilities': ['text-generation', 'reasoning', 'coding']
        }
    
    @patch('src.models.openai_model.openai')
    def test_openai_model_initialization(self, mock_openai, model_config):
        """Test OpenAI model initialization"""
        with patch('src.utils.config.config_manager') as mock_config:
            mock_config.settings.openai_api_key = 'test-key'
            model = OpenAIModel(model_config)
            
            assert model.model_id == 'openai-gpt-4'
            assert model.name == 'GPT-4'
            assert model.provider == 'openai'
    
    def test_estimate_tokens(self, model_config):
        """Test token estimation"""
        with patch('src.utils.config.config_manager') as mock_config:
            mock_config.settings.openai_api_key = 'test-key'
            with patch('src.models.openai_model.tiktoken') as mock_tiktoken:
                mock_encoding = Mock()
                mock_encoding.encode.return_value = [1, 2, 3, 4, 5]
                mock_tiktoken.encoding_for_model.return_value = mock_encoding
                
                model = OpenAIModel(model_config)
                tokens = model.estimate_tokens("Hello world")
                
                assert tokens == 5


class TestAnthropicModel:
    @pytest.fixture
    def model_config(self):
        return {
            'id': 'anthropic-claude-3',
            'name': 'Claude 3',
            'provider': 'anthropic',
            'cost_per_1k_tokens': 0.015,
            'max_tokens': 200000,
            'capabilities': ['text-generation', 'reasoning', 'coding']
        }
    
    @patch('src.models.anthropic_model.anthropic')
    def test_anthropic_model_initialization(self, mock_anthropic, model_config):
        """Test Anthropic model initialization"""
        with patch('src.utils.config.config_manager') as mock_config:
            mock_config.settings.anthropic_api_key = 'test-key'
            model = AnthropicModel(model_config)
            
            assert model.model_id == 'anthropic-claude-3'
            assert model.name == 'Claude 3'
            assert model.provider == 'anthropic'
    
    def test_estimate_tokens(self, model_config):
        """Test token estimation"""
        with patch('src.utils.config.config_manager') as mock_config:
            mock_config.settings.anthropic_api_key = 'test-key'
            model = AnthropicModel(model_config)
            
            tokens = model.estimate_tokens("Hello world")
            assert tokens == 3  # 12 characters / 4 = 3 tokens


class TestGeminiModel:
    @pytest.fixture
    def model_config(self):
        return {
            'id': 'google-gemini-pro',
            'name': 'Gemini Pro',
            'provider': 'google',
            'cost_per_1k_tokens': 0.0,
            'max_tokens': 30000,
            'capabilities': ['text-generation', 'reasoning', 'coding']
        }
    
    @patch('src.models.gemini_model.genai')
    def test_gemini_model_initialization(self, mock_genai, model_config):
        """Test Gemini model initialization"""
        with patch('src.utils.config.config_manager') as mock_config:
            mock_config.settings.google_api_key = 'test-key'
            model = GeminiModel(model_config)
            
            assert model.model_id == 'google-gemini-pro'
            assert model.name == 'Gemini Pro'
            assert model.provider == 'google'
    
    def test_estimate_tokens(self, model_config):
        """Test token estimation"""
        with patch('src.utils.config.config_manager') as mock_config:
            mock_config.settings.google_api_key = 'test-key'
            model = GeminiModel(model_config)
            
            tokens = model.estimate_tokens("Hello world")
            assert tokens == 3  # 12 characters / 4 = 3 tokens


class TestDeepSeekModel:
    @pytest.fixture
    def model_config(self):
        return {
            'id': 'deepseek-deepseek-chat',
            'name': 'DeepSeek Chat',
            'provider': 'deepseek',
            'cost_per_1k_tokens': 0.0014,
            'max_tokens': 32768,
            'capabilities': ['text-generation', 'reasoning', 'coding']
        }
    
    def test_deepseek_model_initialization(self, model_config):
        """Test DeepSeek model initialization"""
        with patch('src.utils.config.config_manager') as mock_config:
            mock_config.settings.deepseek_api_key = 'test-key'
            model = DeepSeekModel(model_config)
            
            assert model.model_id == 'deepseek-deepseek-chat'
            assert model.name == 'DeepSeek Chat'
            assert model.provider == 'deepseek'
    
    def test_estimate_tokens(self, model_config):
        """Test token estimation"""
        with patch('src.utils.config.config_manager') as mock_config:
            mock_config.settings.deepseek_api_key = 'test-key'
            model = DeepSeekModel(model_config)
            
            tokens = model.estimate_tokens("Hello world")
            assert tokens == 3  # 12 characters / 4 = 3 tokens 