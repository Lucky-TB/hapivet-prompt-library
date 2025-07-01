from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from src.utils.types import PromptRequest, PromptResponse, AIModel
from src.utils.logger import LoggerMixin
import uuid
from datetime import datetime


class BaseAIModel(ABC, LoggerMixin):
    """Base class for all AI model adapters"""
    
    def __init__(self, model_config: Dict[str, Any]):
        self.model_config = model_config
        self.model_id = model_config.get('id', '')
        self.name = model_config.get('name', '')
        self.provider = model_config.get('provider', '')
        self.cost_per_1k_tokens = model_config.get('cost_per_1k_tokens', 0.0)
        self.max_tokens = model_config.get('max_tokens', 4096)
        self.capabilities = model_config.get('capabilities', [])
        self.is_available = model_config.get('is_available', True)
    
    @abstractmethod
    async def generate_response(self, request: PromptRequest) -> PromptResponse:
        """Generate a response using the AI model"""
        pass
    
    @abstractmethod
    def estimate_tokens(self, text: str) -> int:
        """Estimate the number of tokens in the text"""
        pass
    
    def calculate_cost(self, tokens: int) -> float:
        """Calculate the cost for the given number of tokens"""
        return (tokens / 1000) * self.cost_per_1k_tokens
    
    def can_handle_capability(self, capability: str) -> bool:
        """Check if this model can handle a specific capability"""
        return capability in self.capabilities
    
    def get_model_info(self) -> AIModel:
        """Get model information"""
        return AIModel(
            id=self.model_id,
            name=self.name,
            provider=self.provider,
            cost_per_1k_tokens=self.cost_per_1k_tokens,
            max_tokens=self.max_tokens,
            capabilities=self.capabilities,
            is_available=self.is_available
        )
    
    def is_available_for_request(self, request: PromptRequest) -> bool:
        """Check if the model is available for the given request"""
        if not self.is_available:
            return False
        
        # Check if the request exceeds max tokens
        estimated_tokens = self.estimate_tokens(request.prompt)
        if estimated_tokens > self.max_tokens:
            return False
        
        return True
    
    def create_response(self, request: PromptRequest, response_text: str, tokens_used: int) -> PromptResponse:
        """Create a response object"""
        cost = self.calculate_cost(tokens_used)
        
        return PromptResponse(
            id=str(uuid.uuid4()),
            request_id=request.id,
            model_used=self.model_id,
            response=response_text,
            tokens_used=tokens_used,
            cost=cost,
            timestamp=datetime.utcnow()
        )
    
    def log_request(self, request: PromptRequest, response: PromptResponse) -> None:
        """Log the request and response"""
        super().log_request(
            request_id=request.id,
            user_id=request.user_id,
            model=self.model_id,
            tokens=response.tokens_used,
            cost=response.cost
        ) 