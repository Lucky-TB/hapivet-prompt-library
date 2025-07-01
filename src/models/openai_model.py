import openai
from typing import Dict, Any
from src.models.base_model import BaseAIModel
from src.utils.types import PromptRequest, PromptResponse
from src.utils.config import config_manager
import tiktoken


class OpenAIModel(BaseAIModel):
    """OpenAI model adapter"""
    
    def __init__(self, model_config: Dict[str, Any]):
        super().__init__(model_config)
        self.client = openai.AsyncOpenAI(api_key=config_manager.settings.openai_api_key)
        # Use a default encoding for token estimation
        try:
            self.encoding = tiktoken.encoding_for_model(self.model_id)
        except:
            # Fallback to cl100k_base encoding (used by GPT-4 and GPT-3.5)
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate tokens using tiktoken"""
        return len(self.encoding.encode(text))
    
    async def generate_response(self, request: PromptRequest) -> PromptResponse:
        """Generate response using OpenAI API"""
        try:
            # Prepare messages
            messages = []
            if request.context:
                messages.append({"role": "system", "content": request.context})
            messages.append({"role": "user", "content": request.prompt})
            
            # Make API call
            response = await self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                max_tokens=request.max_tokens or self.max_tokens,
                temperature=0.7
            )
            
            # Extract response
            response_text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            # Create response object
            prompt_response = self.create_response(request, response_text, tokens_used)
            
            # Log the request
            self.log_request(request, prompt_response)
            
            return prompt_response
            
        except Exception as e:
            self.log_error(e, {"model": self.model_id, "request_id": request.id})
            raise 