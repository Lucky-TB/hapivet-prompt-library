from typing import Dict, List, Optional, Any
from src.models.base_model import BaseAIModel
from src.models.openai_model import OpenAIModel
from src.models.anthropic_model import AnthropicModel
from src.models.gemini_model import GeminiModel
from src.models.deepseek_model import DeepSeekModel
from src.utils.types import PromptRequest, PromptResponse, AIModel
from src.utils.config import config_manager
from src.utils.logger import LoggerMixin
import uuid
from datetime import datetime


class ModelManager(LoggerMixin):
    """Manages AI models and routes requests to appropriate models"""
    
    def __init__(self):
        self.models: Dict[str, BaseAIModel] = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize all available models"""
        models_config = config_manager.get_models()
        
        for provider, provider_models in models_config.items():
            for model_name, model_config in provider_models.items():
                model_id = f"{provider}-{model_name}"
                model_config['id'] = model_id
                model_config['name'] = model_name
                model_config['provider'] = provider
                
                try:
                    if provider == 'openai':
                        self.models[model_id] = OpenAIModel(model_config)
                    elif provider == 'anthropic':
                        self.models[model_id] = AnthropicModel(model_config)
                    elif provider == 'google':
                        self.models[model_id] = GeminiModel(model_config)
                    elif provider == 'deepseek':
                        self.models[model_id] = DeepSeekModel(model_config)
                    
                    self.logger.info(f"Initialized model: {model_id}")
                except Exception as e:
                    self.logger.error(f"Failed to initialize model {model_id}: {e}")
    
    def _check_api_key_availability(self, model: BaseAIModel) -> bool:
        """Check if a model has a valid API key"""
        if model.provider == 'openai':
            return bool(config_manager.settings.openai_api_key and 
                       config_manager.settings.openai_api_key.strip() and
                       config_manager.settings.openai_api_key != "your_openai_key")
        elif model.provider == 'anthropic':
            return bool(config_manager.settings.anthropic_api_key and 
                       config_manager.settings.anthropic_api_key.strip() and
                       config_manager.settings.anthropic_api_key != "your_anthropic_key")
        elif model.provider == 'google':
            return bool(config_manager.settings.google_api_key and 
                       config_manager.settings.google_api_key.strip() and
                       config_manager.settings.google_api_key != "your_google_key")
        elif model.provider == 'deepseek':
            return bool(config_manager.settings.deepseek_api_key and 
                       config_manager.settings.deepseek_api_key.strip() and
                       config_manager.settings.deepseek_api_key != "your_deepseek_key")
        return False
    
    def get_available_models(self) -> List[AIModel]:
        """Get list of all available models with API keys"""
        available_models = []
        for model in self.models.values():
            if self._check_api_key_availability(model):
                model_info = model.get_model_info()
                model_info.is_available = True
                available_models.append(model_info)
            else:
                # Mark as unavailable if no API key
                model_info = model.get_model_info()
                model_info.is_available = False
                available_models.append(model_info)
        return available_models
    
    def get_model_by_id(self, model_id: str) -> Optional[BaseAIModel]:
        """Get a specific model by ID"""
        return self.models.get(model_id)
    
    def select_best_model(self, request: PromptRequest, required_capabilities: List[str] = None) -> Optional[BaseAIModel]:
        """Select the best model for the request based on capabilities and cost"""
        available_models = []
        
        for model in self.models.values():
            if not self._check_api_key_availability(model):
                continue
                
            if not model.is_available_for_request(request):
                continue
            
            # Check if model has required capabilities
            if required_capabilities:
                if not all(model.can_handle_capability(cap) for cap in required_capabilities):
                    continue
            
            available_models.append(model)
        
        if not available_models:
            return None
        
        # Sort by cost (cheapest first)
        available_models.sort(key=lambda m: m.cost_per_1k_tokens)
        
        return available_models[0]
    
    def get_model_fallback_order(self, request: PromptRequest, required_capabilities: List[str] = None) -> List[BaseAIModel]:
        """Get models in fallback order (preferred to least preferred)"""
        available_models = []
        
        for model in self.models.values():
            if not self._check_api_key_availability(model):
                continue
                
            if not model.is_available_for_request(request):
                continue
            
            # Check if model has required capabilities
            if required_capabilities:
                if not all(model.can_handle_capability(cap) for cap in required_capabilities):
                    continue
            
            available_models.append(model)
        
        if not available_models:
            return []
        
        # Sort by preference: free models first, then by cost
        def sort_key(model):
            # Free models first (cost = 0)
            if model.cost_per_1k_tokens == 0:
                return (0, 0)
            # Then by cost
            return (1, model.cost_per_1k_tokens)
        
        available_models.sort(key=sort_key)
        return available_models
    
    def detect_capabilities(self, prompt: str) -> List[str]:
        """Detect required capabilities from the prompt"""
        capabilities = []
        prompt_lower = prompt.lower()
        
        # Detect coding tasks
        coding_keywords = ['code', 'program', 'function', 'class', 'debug', 'algorithm', 'api', 'database', 'python', 'javascript', 'java', 'html', 'css', 'sql']
        if any(keyword in prompt_lower for keyword in coding_keywords):
            capabilities.append('coding')
        
        # Detect reasoning tasks
        reasoning_keywords = ['explain', 'analyze', 'compare', 'why', 'how', 'reason', 'logic', 'think', 'consider']
        if any(keyword in prompt_lower for keyword in reasoning_keywords):
            capabilities.append('reasoning')
        
        # Default to text generation
        if not capabilities:
            capabilities.append('text-generation')
        
        return capabilities
    
    async def process_request(self, request: PromptRequest) -> PromptResponse:
        """Process a prompt request and return the response"""
        # Generate request ID if not provided
        if not hasattr(request, 'id') or not request.id:
            request.id = str(uuid.uuid4())
        
        # Detect required capabilities
        required_capabilities = self.detect_capabilities(request.prompt)
        
        # If specific model is requested, try that first
        if request.model_preference and request.model_preference != 'auto':
            specific_model = self.get_model_by_id(request.model_preference)
            if specific_model and self._check_api_key_availability(specific_model):
                try:
                    self.logger.info(f"Using requested model: {specific_model.model_id}")
                    response = await specific_model.generate_response(request)
                    return response
                except Exception as e:
                    self.logger.warning(f"Requested model {specific_model.model_id} failed: {e}")
                    # Continue to fallback models
        
        # Get models in fallback order
        fallback_models = self.get_model_fallback_order(request, required_capabilities)
        
        if not fallback_models:
            raise ValueError("No suitable model available for this request")
        
        # Try each model in order until one works
        last_error = None
        for model in fallback_models:
            try:
                self.logger.info(f"Trying model: {model.model_id}")
                response = await model.generate_response(request)
                self.logger.info(f"Successfully used model: {model.model_id}")
                return response
            except Exception as e:
                last_error = e
                self.logger.warning(f"Model {model.model_id} failed: {e}")
                continue
        
        # If we get here, all models failed
        raise ValueError(f"All available models failed. Last error: {last_error}")
    
    def get_model_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics for all models"""
        stats = {}
        for model_id, model in self.models.items():
            stats[model_id] = {
                'name': model.name,
                'provider': model.provider,
                'cost_per_1k_tokens': model.cost_per_1k_tokens,
                'max_tokens': model.max_tokens,
                'capabilities': model.capabilities,
                'is_available': self._check_api_key_availability(model)
            }
        return stats 