import httpx
from typing import Dict, Any
from src.models.base_model import BaseAIModel
from src.utils.types import PromptRequest, PromptResponse
from src.utils.config import config_manager


class DeepSeekModel(BaseAIModel):
    """DeepSeek model adapter"""
    
    def __init__(self, model_config: Dict[str, Any]):
        super().__init__(model_config)
        self.api_key = config_manager.settings.deepseek_api_key
        self.base_url = "https://api.deepseek.com/v1"
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate tokens for DeepSeek"""
        # Simple estimation: ~4 characters per token
        return len(text) // 4
    
    async def generate_response(self, request: PromptRequest) -> PromptResponse:
        """Generate response using DeepSeek API"""
        try:
            # Prepare messages
            messages = []
            if request.context:
                messages.append({"role": "system", "content": request.context})
            messages.append({"role": "user", "content": request.prompt})
            
            # Prepare request payload
            payload = {
                "model": self.name,  # Use the actual model name, not the full ID
                "messages": messages,
                "max_tokens": request.max_tokens or self.max_tokens,
                "temperature": 0.7
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Make API call
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()
            
            # Extract response
            response_text = data["choices"][0]["message"]["content"]
            tokens_used = data["usage"]["total_tokens"]
            
            # Create response object
            prompt_response = self.create_response(request, response_text, tokens_used)
            
            # Log the request
            self.log_request(request, prompt_response)
            
            return prompt_response
            
        except Exception as e:
            self.log_error(e, {"model": self.model_id, "request_id": request.id})
            raise 