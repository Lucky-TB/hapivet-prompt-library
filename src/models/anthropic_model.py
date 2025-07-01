import anthropic
from typing import Dict, Any
from src.models.base_model import BaseAIModel
from src.utils.types import PromptRequest, PromptResponse
from src.utils.config import config_manager


class AnthropicModel(BaseAIModel):
    """Anthropic model adapter"""
    
    def __init__(self, model_config: Dict[str, Any]):
        super().__init__(model_config)
        self.client = anthropic.AsyncAnthropic(api_key=config_manager.settings.anthropic_api_key)
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate tokens using Anthropic's tokenizer"""
        # Simple estimation: ~4 characters per token
        return len(text) // 4
    
    async def generate_response(self, request: PromptRequest) -> PromptResponse:
        """Generate response using Anthropic API"""
        try:
            # Prepare prompt
            prompt = ""
            if request.context:
                prompt += f"{request.context}\n\n"
            prompt += f"Human: {request.prompt}\n\nAssistant:"
            
            # Make API call
            response = await self.client.messages.create(
                model=self.model_id,
                max_tokens=request.max_tokens or self.max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Extract response
            response_text = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            
            # Create response object
            prompt_response = self.create_response(request, response_text, tokens_used)
            
            # Log the request
            self.log_request(request, prompt_response)
            
            return prompt_response
            
        except Exception as e:
            self.log_error(e, {"model": self.model_id, "request_id": request.id})
            raise 