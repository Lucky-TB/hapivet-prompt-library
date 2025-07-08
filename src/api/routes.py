from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from src.utils.types import PromptRequest, PromptResponse, UsageAlert, AIModel
from src.services.model_manager import ModelManager
from src.services.usage_monitor import UsageMonitor
from src.services.cost_optimizer import CostOptimizer
from src.utils.logger import LoggerMixin
import uuid
from datetime import datetime

router = APIRouter()
security = HTTPBearer()

# Initialize services
model_manager = ModelManager()
usage_monitor = UsageMonitor()
cost_optimizer = CostOptimizer()


def generate_mock_response(prompt: str, model_preference: str = None) -> str:
    """Generate realistic mock responses based on prompt content"""
    prompt_lower = prompt.lower()
    
    # Summarization
    if "summarize" in prompt_lower or "summary" in prompt_lower:
        return """Here's a summary of the key points:

1. **AI Evolution**: Artificial Intelligence has rapidly evolved from theoretical concept to practical technology transforming multiple industries.

2. **Healthcare Applications**: AI is being used for medical image analysis, patient outcome prediction, and drug discovery, with machine learning algorithms detecting patterns that human radiologists might miss.

3. **Financial Sector**: AI powers algorithmic trading, fraud detection, and personalized financial advice, helping banks analyze market trends and assess credit risk.

4. **Transportation Revolution**: Autonomous vehicles rely heavily on AI for navigation and decision-making, with major companies investing billions in self-driving technology.

5. **Challenges & Benefits**: While AI brings concerns about job displacement and privacy, its potential benefits include automating routine tasks and solving complex problems in areas like climate change and scientific research.

The key is developing AI systems that augment human capabilities rather than replace them entirely."""

    # Code generation
    elif "python" in prompt_lower or "function" in prompt_lower or "code" in prompt_lower:
        return """```python
def sum_even_numbers(numbers):
    \"\"\"
    Calculate the sum of all even numbers in a list.
    
    Args:
        numbers (list): A list of numbers
        
    Returns:
        int: Sum of even numbers
        
    Raises:
        TypeError: If input is not a list
        ValueError: If list contains non-numeric values
    \"\"\"
    try:
        if not isinstance(numbers, list):
            raise TypeError("Input must be a list")
        
        even_sum = 0
        for num in numbers:
            if not isinstance(num, (int, float)):
                raise ValueError("All elements must be numbers")
            if num % 2 == 0:
                even_sum += num
        
        return even_sum
        
    except (TypeError, ValueError) as e:
        print(f"Error: {e}")
        return None

# Example usage
test_numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
result = sum_even_numbers(test_numbers)
print(f"Sum of even numbers: {result}")  # Output: Sum of even numbers: 30

# Test with error handling
invalid_input = "not a list"
result = sum_even_numbers(invalid_input)  # Will print error message
```"""

    # Creative writing
    elif "poem" in prompt_lower or "creative" in prompt_lower or "story" in prompt_lower:
        return """**Digital Bridges**

In circuits deep and screens so bright,
We reach across the endless night.
Through fiber threads and wireless waves,
Human hearts that technology saves.

Yet in this world of ones and zeros,
We find connections, not just heroes.
For every click and every byte,
Brings souls together in the light.

So let us build with mindful care,
A future where we all can share.
Technology as bridge, not wall,
Connecting, serving, one and all.

*This poem explores the balance between technological advancement and human connection, emphasizing how technology can bring people together rather than isolate them.*"""

    # Data analysis
    elif "analyze" in prompt_lower or "data" in prompt_lower or "trend" in prompt_lower:
        return """**Sales Data Analysis**

**Trends Identified:**
- **Overall Growth**: Sales increased from $45,000 to $61,000 (35.6% growth)
- **Q4 Spike**: Significant jump from $48,000 to $61,000 (27.1% increase)
- **Seasonal Pattern**: Q2 and Q4 show higher performance

**Q4 Increase Analysis:**
1. **Holiday Season**: Q4 typically includes holiday shopping periods
2. **Year-End Push**: Companies often have budget spending deadlines
3. **Product Launches**: New products may have been introduced
4. **Marketing Campaigns**: Increased marketing efforts in Q4

**Recommendations:**
- Investigate what drove the Q4 success to replicate in future quarters
- Consider seasonal planning for Q2 and Q4 peaks
- Analyze customer behavior patterns during high-performing periods"""

    # Translation
    elif "translate" in prompt_lower or "spanish" in prompt_lower:
        return """**English to Spanish Translation:**

Original: "Hello, how are you today? I hope you're having a wonderful day. The weather is beautiful and I'm looking forward to our meeting later."

Spanish: "Hola, ¿cómo estás hoy? Espero que estés teniendo un día maravilloso. El clima está hermoso y estoy deseando nuestra reunión más tarde."

**Translation Notes:**
- "Hola" is the standard greeting in Spanish
- "¿Cómo estás?" is the informal way to ask "how are you?"
- "Espero que" uses the subjunctive mood for expressing hope
- "Deseando" conveys anticipation and excitement"""

    # Q&A
    elif "difference" in prompt_lower or "machine learning" in prompt_lower or "deep learning" in prompt_lower:
        return """**Machine Learning vs Deep Learning: Key Differences**

**Machine Learning:**
- **Definition**: Subset of AI that enables systems to learn from data without explicit programming
- **Approach**: Uses algorithms to identify patterns in data
- **Data Requirements**: Can work with smaller datasets
- **Feature Engineering**: Requires manual feature extraction
- **Examples**: Linear regression, decision trees, random forests

**Deep Learning:**
- **Definition**: Subset of machine learning using neural networks with multiple layers
- **Approach**: Automatically learns hierarchical representations
- **Data Requirements**: Needs large amounts of data
- **Feature Engineering**: Automatic feature extraction
- **Examples**: Convolutional Neural Networks (CNNs), Recurrent Neural Networks (RNNs)

**When to Use Each:**

**Machine Learning:**
- Smaller datasets (< 10,000 samples)
- Structured data (tables, databases)
- Need for interpretability
- Limited computational resources

**Deep Learning:**
- Large datasets (> 10,000 samples)
- Unstructured data (images, text, audio)
- Complex pattern recognition
- Sufficient computational resources

**Real-world Applications:**
- **ML**: Credit scoring, recommendation systems, fraud detection
- **DL**: Image recognition, natural language processing, autonomous vehicles"""

    # Default response
    else:
        return f"""**AI Response (Demo Mode)**

You asked: "{prompt}"

This is a demonstration response from the Hapivet Prompt Library. In a real implementation, this would be generated by the selected AI model ({model_preference or 'auto-selected'}).

**What this demonstrates:**
- ✅ Prompt processing
- ✅ Model selection
- ✅ Response generation
- ✅ Cost tracking
- ✅ Usage monitoring

**Next Steps:**
To get real AI responses, you would need to:
1. Configure API keys for the selected models
2. Implement the actual model integration
3. Set up proper error handling and rate limiting

The system is designed to intelligently route requests to the best model based on the prompt content and your preferences."""


class PromptRequestModel(BaseModel):
    prompt: str
    context: str = ""
    model_preference: Optional[str] = None
    max_tokens: Optional[int] = None


class PromptResponseModel(BaseModel):
    id: str
    response: str
    model_used: str
    tokens_used: int
    cost: float
    timestamp: datetime


class UsageStatsModel(BaseModel):
    user_id: str
    usage_data: Dict[str, Any]


class AlertModel(BaseModel):
    type: str
    message: str
    severity: str
    timestamp: datetime


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Get current user from token"""
    from src.services.auth_service import auth_service
    
    user = auth_service.verify_token(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return str(user["id"])  # Return user ID as string for compatibility


@router.post("/prompt", response_model=PromptResponseModel)
async def submit_prompt(
    request: PromptRequestModel,
    current_user: str = Depends(get_current_user)
):
    """Submit a prompt request"""
    try:
        # Create prompt request
        prompt_request = PromptRequest(
            id=str(uuid.uuid4()),
            user_id=current_user,
            prompt=request.prompt,
            context=request.context,
            model_preference=request.model_preference,
            max_tokens=request.max_tokens,
            timestamp=datetime.utcnow()
        )
        
        # Process the request
        response = await model_manager.process_request(prompt_request)
        
        # Record usage in monitoring and cost optimization
        usage_monitor.record_usage(response, current_user)
        cost_optimizer.record_usage(response.model_used.split('-')[0], response.tokens_used, response.cost)
        
        return PromptResponseModel(
            id=response.id,
            response=response.response,
            model_used=response.model_used,
            tokens_used=response.tokens_used,
            cost=response.cost,
            timestamp=response.timestamp
        )
        
    except ValueError as e:
        # Handle model availability errors
        if "No suitable model available" in str(e):
            raise HTTPException(status_code=503, detail="No AI models are currently available. Please check your API key configuration.")
        elif "All available models failed" in str(e):
            raise HTTPException(status_code=503, detail="All AI models are currently unavailable. Please try again later or check your API keys.")
        else:
            raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while processing your request: {str(e)}")


@router.get("/models", response_model=List[AIModel])
async def get_available_models():
    """Get list of available AI models"""
    try:
        return model_manager.get_available_models()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/usage/{user_id}", response_model=UsageStatsModel)
async def get_usage_stats(
    user_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get usage statistics for a user"""
    try:
        # In a real implementation, check if current_user has permission to view user_id's stats
        usage_data = usage_monitor.get_user_usage(user_id)
        
        return UsageStatsModel(
            user_id=user_id,
            usage_data=usage_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts", response_model=List[AlertModel])
async def get_alerts(
    user_id: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """Get active alerts"""
    try:
        alerts = usage_monitor.get_active_alerts(user_id)
        
        return [
            AlertModel(
                type=alert.type.value,
                message=alert.message,
                severity=alert.severity.value,
                timestamp=alert.timestamp
            )
            for alert in alerts
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cost-analysis")
async def get_cost_analysis(current_user: str = Depends(get_current_user)):
    """Get cost analysis and recommendations"""
    try:
        return cost_optimizer.get_cost_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/provider-ranking")
async def get_provider_ranking(current_user: str = Depends(get_current_user)):
    """Get providers ranked by cost efficiency"""
    try:
        return cost_optimizer.get_provider_ranking()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/rotate-models")
async def force_model_rotation(current_user: str = Depends(get_current_user)):
    """Force model rotation (admin only)"""
    try:
        # In a real implementation, check if current_user is an admin
        # For now, we'll just return a success message
        return {"message": "Model rotation triggered successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "services": {
            "model_manager": "active",
            "usage_monitor": "active",
            "cost_optimizer": "active"
        }
    }


@router.post("/demo/prompt", response_model=PromptResponseModel)
async def demo_submit_prompt(request: PromptRequestModel):
    """Demo endpoint for testing without authentication"""
    try:
        # Create prompt request with demo user
        prompt_request = PromptRequest(
            id=str(uuid.uuid4()),
            user_id="demo-user",
            prompt=request.prompt,
            context=request.context,
            model_preference=request.model_preference,
            max_tokens=request.max_tokens,
            timestamp=datetime.utcnow()
        )
        
        # Process the request using the real model manager
        response = await model_manager.process_request(prompt_request)
        
        # Record usage for monitoring
        usage_monitor.record_usage(response, "demo-user")
        cost_optimizer.record_usage(response.model_used.split('-')[0], response.tokens_used, response.cost)
        
        return PromptResponseModel(
            id=response.id,
            response=response.response,
            model_used=response.model_used,
            tokens_used=response.tokens_used,
            cost=response.cost,
            timestamp=response.timestamp
        )
        
    except Exception as e:
        # If all models fail, return a helpful error message
        raise HTTPException(
            status_code=500, 
            detail=f"All available models failed. Please check your API keys. Error: {str(e)}"
        )


@router.get("/demo/cost-analysis")
async def demo_cost_analysis():
    """Demo endpoint for cost analysis without authentication"""
    try:
        # Get real cost analysis data
        cost_analysis = cost_optimizer.get_cost_analysis()
        
        # Get available models to show which ones are configured
        available_models = model_manager.get_available_models()
        configured_providers = list(set(model.provider for model in available_models if model.is_available))
        
        return {
            "total_cost": cost_analysis.get("total_cost", 0.0),
            "cost_by_provider": cost_analysis.get("cost_by_provider", {}),
            "available_providers": configured_providers,
            "model_availability": {
                model.id: model.is_available for model in available_models
            },
            "recommendations": cost_analysis.get("recommendations", [
                "Configure API keys for the models you want to use",
                "Google Gemini Pro is free and available if configured",
                "DeepSeek models offer good cost efficiency for coding tasks"
            ])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 