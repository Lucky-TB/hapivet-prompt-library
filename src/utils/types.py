from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class AlertType(str, Enum):
    SPIKE = "spike"
    ABNORMAL = "abnormal"
    FRAUD = "fraud"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AIModel(BaseModel):
    id: str
    name: str
    provider: str
    cost_per_1k_tokens: float
    max_tokens: int
    capabilities: List[str]
    is_available: bool = True


class PromptRequest(BaseModel):
    id: str
    user_id: str
    prompt: str
    context: str = ""
    model_preference: Optional[str] = None
    max_tokens: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PromptResponse(BaseModel):
    id: str
    request_id: str
    model_used: str
    response: str
    tokens_used: int
    cost: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TokenUsage(BaseModel):
    user_id: str
    model_id: str
    tokens_used: int
    cost: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: str


class UsageAlert(BaseModel):
    type: AlertType
    user_id: str
    message: str
    severity: Severity
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class User(BaseModel):
    id: str
    username: str
    api_key: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ModelCapability(str, Enum):
    TEXT_GENERATION = "text-generation"
    REASONING = "reasoning"
    CODING = "coding"
    CODE_GENERATION = "code-generation"
    DEBUGGING = "debugging" 