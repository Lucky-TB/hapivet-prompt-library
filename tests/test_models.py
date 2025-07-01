import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from src.models.base_model import BaseAIModel
from src.models.openai_model import OpenAIModel
from src.models.anthropic_model import AnthropicModel
from src.models.gemini_model import GeminiModel
from src.models.deepseek_model import DeepSeekModel
from src.utils.types import PromptRequest, PromptResponse, AIModel


class TestBaseAIModel:
    """Test the base AI model class"""
    
    def test_base_model_initialization(self):
        """Test base model initialization"""
        config = {
            'id': 'test-model',
            'name': 'Test Model',
            'provider': 'test-provider',
            'cost_per_1k_tokens': 0.01,
            'max_tokens': 1000,
            'capabilities': ['text-generation'],
            'is_available': True
        }
        model = BaseAIModel(config)
        assert model.model_id == "test-model"
        assert model.name == "Test Model"
        assert model.provider == "test-provider"
        assert model.cost_per_1k_tokens == 0.01
        assert model.max_tokens == 1000
        assert model.capabilities == ['text-generation']
        assert model.is_available is True
    
    def test_estimate_tokens(self):
        """Test token estimation"""
        config = {'id': 'test', 'provider': 'test', 'name': 'Test'}
        model = BaseAIModel(config)
        tokens = model.estimate_tokens("Hello world")
        assert isinstance(tokens, int)
        assert tokens > 0
    
    @pytest.mark.asyncio
    async def test_generate_response_not_implemented(self):
        """Test that base generate_response method raises NotImplementedError"""
        config = {'id': 'test', 'provider': 'test', 'name': 'Test'}
        model = BaseAIModel(config)
        request = PromptRequest(
            id="test-id",
            user_id="test-user",
            prompt="test prompt"
        )
        with pytest.raises(NotImplementedError):
            await model.generate_response(request)


class TestOpenAIModel:
    """Test OpenAI model implementation"""
    
    @patch('src.models.openai_model.openai.AsyncOpenAI')
    def test_openai_initialization(self, mock_openai):
        """Test OpenAI model initialization"""
        config = ModelConfig(
            model_id="gpt-4",
            provider="openai",
            max_tokens=1000,
            temperature=0.7
        )
        model = OpenAIModel(config)
        assert model.model_id == "gpt-4"
        assert model.provider == "openai"
        mock_openai.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('src.models.openai_model.openai.AsyncOpenAI')
    async def test_openai_generate_success(self, mock_openai):
        """Test successful OpenAI generation"""
        # Mock the OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.usage.total_tokens = 10
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client
        
        config = ModelConfig(model_id="gpt-4", provider="openai")
        model = OpenAIModel(config)
        
        response = await model.generate("Test prompt")
        
        assert isinstance(response, ModelResponse)
        assert response.content == "Test response"
        assert response.tokens_used == 10
        assert response.model_id == "gpt-4"
    
    @pytest.mark.asyncio
    @patch('src.models.openai_model.openai.AsyncOpenAI')
    async def test_openai_generate_error(self, mock_openai):
        """Test OpenAI generation error handling"""
        mock_client = Mock()
        mock_client.chat.completions.create = AsyncMock(side_effect=Exception("API Error"))
        mock_openai.return_value = mock_client
        
        config = ModelConfig(model_id="gpt-4", provider="openai")
        model = OpenAIModel(config)
        
        with pytest.raises(Exception):
            await model.generate("Test prompt")


class TestAnthropicModel:
    """Test Anthropic model implementation"""
    
    @patch('src.models.anthropic_model.Anthropic')
    def test_anthropic_initialization(self, mock_anthropic):
        """Test Anthropic model initialization"""
        config = ModelConfig(
            model_id="claude-3-sonnet",
            provider="anthropic",
            max_tokens=1000,
            temperature=0.7
        )
        model = AnthropicModel(config)
        assert model.model_id == "claude-3-sonnet"
        assert model.provider == "anthropic"
        mock_anthropic.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('src.models.anthropic_model.Anthropic')
    async def test_anthropic_generate_success(self, mock_anthropic):
        """Test successful Anthropic generation"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = "Test response"
        mock_response.usage.input_tokens = 5
        mock_response.usage.output_tokens = 10
        mock_client.messages.create = AsyncMock(return_value=mock_response)
        mock_anthropic.return_value = mock_client
        
        config = ModelConfig(model_id="claude-3-sonnet", provider="anthropic")
        model = AnthropicModel(config)
        
        response = await model.generate("Test prompt")
        
        assert isinstance(response, ModelResponse)
        assert response.content == "Test response"
        assert response.tokens_used == 15  # input + output
        assert response.model_id == "claude-3-sonnet"


class TestGeminiModel:
    """Test Google Gemini model implementation"""
    
    @patch('src.models.gemini_model.google.generativeai')
    def test_gemini_initialization(self, mock_gemini):
        """Test Gemini model initialization"""
        config = ModelConfig(
            model_id="gemini-pro",
            provider="google",
            max_tokens=1000,
            temperature=0.7
        )
        model = GeminiModel(config)
        assert model.model_id == "gemini-pro"
        assert model.provider == "google"
        mock_gemini.configure.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('src.models.gemini_model.google.generativeai')
    async def test_gemini_generate_success(self, mock_gemini):
        """Test successful Gemini generation"""
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "Test response"
        mock_model.generate_content = AsyncMock(return_value=mock_response)
        mock_gemini.GenerativeModel.return_value = mock_model
        
        config = ModelConfig(model_id="gemini-pro", provider="google")
        model = GeminiModel(config)
        
        response = await model.generate("Test prompt")
        
        assert isinstance(response, ModelResponse)
        assert response.content == "Test response"
        assert response.model_id == "gemini-pro"


class TestDeepSeekModel:
    """Test DeepSeek model implementation"""
    
    @patch('src.models.deepseek_model.requests.post')
    def test_deepseek_initialization(self, mock_requests):
        """Test DeepSeek model initialization"""
        config = ModelConfig(
            model_id="deepseek-chat",
            provider="deepseek",
            max_tokens=1000,
            temperature=0.7
        )
        model = DeepSeekModel(config)
        assert model.model_id == "deepseek-chat"
        assert model.provider == "deepseek"
    
    @pytest.mark.asyncio
    @patch('src.models.deepseek_model.requests.post')
    async def test_deepseek_generate_success(self, mock_requests):
        """Test successful DeepSeek generation"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}],
            "usage": {"total_tokens": 15}
        }
        mock_response.status_code = 200
        mock_requests.return_value = mock_response
        
        config = ModelConfig(model_id="deepseek-chat", provider="deepseek")
        model = DeepSeekModel(config)
        
        response = await model.generate("Test prompt")
        
        assert isinstance(response, ModelResponse)
        assert response.content == "Test response"
        assert response.tokens_used == 15
        assert response.model_id == "deepseek-chat" 