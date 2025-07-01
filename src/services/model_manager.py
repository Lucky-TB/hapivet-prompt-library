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
    
    def get_available_models(self) -> List[AIModel]:
        """Get list of all available models"""
        return [model.get_model_info() for model in self.models.values() if model.is_available]
    
    def get_model_by_id(self, model_id: str) -> Optional[BaseAIModel]:
        """Get a specific model by ID"""
        return self.models.get(model_id)
    
    def select_best_model(self, request: PromptRequest, required_capabilities: List[str] = None) -> Optional[BaseAIModel]:
        """Select the best model for the request based on capabilities and cost"""
        available_models = []
        
        for model in self.models.values():
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
    
    def detect_capabilities(self, prompt: str) -> List[str]:
        """Detect required capabilities from the prompt"""
        capabilities = []
        prompt_lower = prompt.lower()
        
        # Detect coding tasks
        coding_keywords = ['code', 'program', 'function', 'class', 'debug', 'algorithm', 'api', 'database']
        if any(keyword in prompt_lower for keyword in coding_keywords):
            capabilities.append('coding')
        
        # Detect reasoning tasks
        reasoning_keywords = ['explain', 'analyze', 'compare', 'why', 'how', 'reason', 'logic']
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
        
        # Select best model
        selected_model = self.select_best_model(request, required_capabilities)
        
        if not selected_model:
            raise ValueError("No suitable model available for this request")
        
        self.logger.info(
            "Processing request",
            request_id=request.id,
            user_id=request.user_id,
            selected_model=selected_model.model_id,
            capabilities=required_capabilities
        )
        
        # Generate response
        response = await selected_model.generate_response(request)
        
        return response
    
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
                'is_available': model.is_available
            }
        return stats 