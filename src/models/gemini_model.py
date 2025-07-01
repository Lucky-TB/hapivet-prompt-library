import google.generativeai as genai
from typing import Dict, Any
from src.models.base_model import BaseAIModel
from src.utils.types import PromptRequest, PromptResponse
from src.utils.config import config_manager


class GeminiModel(BaseAIModel):
    """Google Gemini model adapter with auto-detection of best available model"""
    
    def __init__(self, model_config: Dict[str, Any]):
        super().__init__(model_config)
        genai.configure(api_key=config_manager.settings.google_api_key)
        self.model_name = self._detect_best_model()
        self.model = genai.GenerativeModel(self.model_name)
    
    def _detect_best_model(self) -> str:
        """Detect the best available Gemini model for the API key"""
        try:
            available_models = [m.name for m in genai.list_models()]
            # Preferred order (most capable to least)
            preferred = [
                "models/gemini-1.5-flash",  # Freest model with highest limits
                "models/gemini-1.5-pro-latest",
                "models/gemini-1.5-pro",
                "models/gemini-1.0-pro-latest",
                "models/gemini-1.0-pro",
                "models/gemini-pro",
                "models/gemini-pro-vision",
            ]
            for name in preferred:
                if name in available_models:
                    return name
            # Fallback: use the first available model
            if available_models:
                return available_models[0]
            raise RuntimeError("No Gemini models available for this API key")
        except Exception as e:
            raise RuntimeError(f"Failed to detect Gemini model: {e}")
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate tokens for Gemini"""
        # Simple estimation: ~4 characters per token
        return len(text) // 4
    
    async def generate_response(self, request: PromptRequest) -> PromptResponse:
        """Generate response using Gemini API"""
        try:
            # Prepare prompt
            prompt = ""
            if request.context:
                prompt += f"{request.context}\n\n"
            prompt += request.prompt
            
            # Make API call
            response = await self.model.generate_content_async(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=request.max_tokens or self.max_tokens,
                    temperature=0.7
                )
            )
            
            # Extract response
            response_text = response.text
            # Gemini doesn't provide token count in response, so we estimate
            tokens_used = self.estimate_tokens(prompt) + self.estimate_tokens(response_text)
            
            # Create response object
            prompt_response = self.create_response(request, response_text, tokens_used)
            
            # Log the request
            self.log_request(request, prompt_response)
            
            return prompt_response
            
        except Exception as e:
            self.log_error(e, {"model": self.model_name, "request_id": request.id})
            raise 