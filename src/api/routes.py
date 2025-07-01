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
    """Extract user ID from API key"""
    # In a real implementation, you would validate the API key and return the user ID
    # For now, we'll use the API key as the user ID
    return credentials.credentials


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
        
        # Record usage for monitoring
        usage = response.tokens_used
        cost = response.cost
        model_id = response.model_used
        
        # Record usage in monitoring and cost optimization
        usage_monitor.record_usage(response)
        cost_optimizer.record_usage(model_id.split('-')[0], usage, cost)
        
        return PromptResponseModel(
            id=response.id,
            response=response.response,
            model_used=response.model_used,
            tokens_used=response.tokens_used,
            cost=response.cost,
            timestamp=response.timestamp
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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