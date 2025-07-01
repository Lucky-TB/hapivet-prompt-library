import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from src.api.app import app
from src.utils.types import PromptRequest, PromptResponse


class TestAPIEndpoints:
    """Test all API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create a test client"""
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert "health" in data
    
    def test_health_endpoint(self, client):
        """Test the health check endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "models" in data
        assert "timestamp" in data
    
    def test_models_endpoint(self, client):
        """Test the models list endpoint"""
        response = client.get("/api/v1/models")
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        assert len(data["models"]) > 0
        
        # Check that expected models are present
        model_ids = [model["model_id"] for model in data["models"]]
        assert "openai-gpt-4" in model_ids
        assert "anthropic-claude-3" in model_ids
        assert "google-gemini-pro" in model_ids
        assert "deepseek-deepseek-chat" in model_ids
    
    @pytest.mark.asyncio
    async def test_generate_endpoint_success(self, client):
        """Test successful response generation"""
        with patch('src.services.model_manager.ModelManager.generate_response') as mock_generate:
            mock_response = ModelResponse(
                content="Test AI response",
                tokens_used=50,
                model_id="openai-gpt-4",
                cost=0.001
            )
            mock_generate.return_value = mock_response
            
            request_data = {
                "prompt": "Hello, how are you?",
                "model_preference": "openai-gpt-4",
                "max_tokens": 100
            }
            
            response = client.post("/api/v1/generate", json=request_data)
            assert response.status_code == 200
            data = response.json()
            assert data["response"] == "Test AI response"
            assert data["model_id"] == "openai-gpt-4"
            assert data["tokens_used"] == 50
            assert data["cost"] == 0.001
    
    def test_generate_endpoint_invalid_request(self, client):
        """Test generate endpoint with invalid request"""
        # Missing prompt
        request_data = {
            "model_preference": "openai-gpt-4"
        }
        response = client.post("/api/v1/generate", json=request_data)
        assert response.status_code == 422  # Validation error
        
        # Invalid model
        request_data = {
            "prompt": "Hello",
            "model_preference": "invalid-model"
        }
        response = client.post("/api/v1/generate", json=request_data)
        assert response.status_code == 400
    
    def test_generate_endpoint_empty_prompt(self, client):
        """Test generate endpoint with empty prompt"""
        request_data = {
            "prompt": "",
            "model_preference": "auto"
        }
        response = client.post("/api/v1/generate", json=request_data)
        assert response.status_code == 422
    
    def test_generate_endpoint_large_prompt(self, client):
        """Test generate endpoint with very large prompt"""
        large_prompt = "A" * 10000  # 10k character prompt
        request_data = {
            "prompt": large_prompt,
            "model_preference": "auto"
        }
        response = client.post("/api/v1/generate", json=request_data)
        assert response.status_code == 422  # Should be rejected for being too large
    
    def test_usage_endpoint(self, client):
        """Test the usage statistics endpoint"""
        response = client.get("/api/v1/usage")
        assert response.status_code == 200
        data = response.json()
        assert "total_requests" in data
        assert "total_tokens" in data
        assert "total_cost" in data
        assert "model_usage" in data
        assert isinstance(data["total_requests"], int)
        assert isinstance(data["total_tokens"], int)
        assert isinstance(data["total_cost"], float)
    
    def test_usage_by_user_endpoint(self, client):
        """Test user-specific usage endpoint"""
        user_id = "test_user_123"
        response = client.get(f"/api/v1/usage/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "total_requests" in data
        assert "total_tokens" in data
        assert "total_cost" in data
        assert "model_breakdown" in data
    
    def test_models_detail_endpoint(self, client):
        """Test detailed model information endpoint"""
        model_id = "openai-gpt-4"
        response = client.get(f"/api/v1/models/{model_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["model_id"] == model_id
        assert "provider" in data
        assert "capabilities" in data
        assert "max_tokens" in data
        assert "cost_per_1k_tokens" in data
    
    def test_models_detail_endpoint_invalid(self, client):
        """Test detailed model endpoint with invalid model ID"""
        response = client.get("/api/v1/models/invalid-model")
        assert response.status_code == 404
    
    def test_optimize_prompt_endpoint(self, client):
        """Test prompt optimization endpoint"""
        request_data = {
            "prompt": "Write a function to sort a list",
            "model_id": "openai-gpt-4"
        }
        response = client.post("/api/v1/optimize-prompt", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "original_prompt" in data
        assert "optimized_prompt" in data
        assert "model_id" in data
        assert data["original_prompt"] == "Write a function to sort a list"
        assert len(data["optimized_prompt"]) > 0
    
    def test_optimize_prompt_endpoint_invalid_model(self, client):
        """Test prompt optimization with invalid model"""
        request_data = {
            "prompt": "Write a function to sort a list",
            "model_id": "invalid-model"
        }
        response = client.post("/api/v1/optimize-prompt", json=request_data)
        assert response.status_code == 400
    
    def test_cost_estimate_endpoint(self, client):
        """Test cost estimation endpoint"""
        request_data = {
            "prompt": "Hello, how are you?",
            "model_id": "openai-gpt-4",
            "max_tokens": 100
        }
        response = client.post("/api/v1/estimate-cost", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "estimated_tokens" in data
        assert "estimated_cost" in data
        assert "model_id" in data
        assert isinstance(data["estimated_tokens"], int)
        assert isinstance(data["estimated_cost"], float)
        assert data["estimated_cost"] >= 0
    
    def test_fraud_check_endpoint(self, client):
        """Test fraud detection endpoint"""
        request_data = {
            "prompt": "Hello, how are you?",
            "user_id": "test_user"
        }
        response = client.post("/api/v1/check-fraud", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "is_suspicious" in data
        assert "reasons" in data
        assert "risk_score" in data
        assert isinstance(data["is_suspicious"], bool)
        assert isinstance(data["risk_score"], float)
    
    def test_fraud_check_suspicious_prompt(self, client):
        """Test fraud detection with suspicious prompt"""
        suspicious_prompt = "password" * 100  # Repeated pattern
        request_data = {
            "prompt": suspicious_prompt,
            "user_id": "test_user"
        }
        response = client.post("/api/v1/check-fraud", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["is_suspicious"] is True
        assert len(data["reasons"]) > 0


class TestAPIErrorHandling:
    """Test API error handling"""
    
    @pytest.fixture
    def client(self):
        """Create a test client"""
        return TestClient(app)
    
    def test_404_error(self, client):
        """Test 404 error handling"""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    def test_405_method_not_allowed(self, client):
        """Test method not allowed error"""
        response = client.put("/api/v1/health")  # PUT not allowed on health endpoint
        assert response.status_code == 405
    
    def test_422_validation_error(self, client):
        """Test validation error handling"""
        # Invalid JSON
        response = client.post("/api/v1/generate", data="invalid json")
        assert response.status_code == 422
    
    def test_500_internal_server_error(self, client):
        """Test internal server error handling"""
        with patch('src.services.model_manager.ModelManager.generate_response') as mock_generate:
            mock_generate.side_effect = Exception("Internal error")
            
            request_data = {
                "prompt": "Hello",
                "model_preference": "openai-gpt-4"
            }
            response = client.post("/api/v1/generate", json=request_data)
            assert response.status_code == 500


class TestAPIMiddleware:
    """Test API middleware functionality"""
    
    @pytest.fixture
    def client(self):
        """Create a test client"""
        return TestClient(app)
    
    def test_cors_headers(self, client):
        """Test CORS headers are present"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers
    
    def test_request_logging(self, client):
        """Test that requests are logged"""
        with patch('src.utils.logger.get_logger') as mock_logger:
            mock_log = Mock()
            mock_logger.return_value = mock_log
            
            response = client.get("/api/v1/health")
            assert response.status_code == 200
            
            # Verify logging was called
            mock_log.info.assert_called()


class TestAPIIntegration:
    """Integration tests for API functionality"""
    
    @pytest.fixture
    def client(self):
        """Create a test client"""
        return TestClient(app)
    
    def test_full_workflow(self, client):
        """Test a complete workflow from prompt to response"""
        # 1. Check health
        health_response = client.get("/api/v1/health")
        assert health_response.status_code == 200
        
        # 2. Get available models
        models_response = client.get("/api/v1/models")
        assert models_response.status_code == 200
        
        # 3. Estimate cost
        cost_request = {
            "prompt": "Write a short poem",
            "model_id": "openai-gpt-4",
            "max_tokens": 50
        }
        cost_response = client.post("/api/v1/estimate-cost", json=cost_request)
        assert cost_response.status_code == 200
        
        # 4. Check for fraud
        fraud_request = {
            "prompt": "Write a short poem",
            "user_id": "test_user"
        }
        fraud_response = client.post("/api/v1/check-fraud", json=fraud_request)
        assert fraud_response.status_code == 200
        
        # 5. Optimize prompt
        optimize_request = {
            "prompt": "Write a short poem",
            "model_id": "openai-gpt-4"
        }
        optimize_response = client.post("/api/v1/optimize-prompt", json=optimize_request)
        assert optimize_response.status_code == 200
        
        # 6. Generate response (with mocked AI)
        with patch('src.services.model_manager.ModelManager.generate_response') as mock_generate:
            mock_response = ModelResponse(
                content="Roses are red, violets are blue...",
                tokens_used=25,
                model_id="openai-gpt-4",
                cost=0.0005
            )
            mock_generate.return_value = mock_response
            
            generate_request = {
                "prompt": "Write a short poem",
                "model_preference": "openai-gpt-4",
                "max_tokens": 50
            }
            generate_response = client.post("/api/v1/generate", json=generate_request)
            assert generate_response.status_code == 200
            
            data = generate_response.json()
            assert data["response"] == "Roses are red, violets are blue..."
            assert data["model_id"] == "openai-gpt-4"
        
        # 7. Check usage
        usage_response = client.get("/api/v1/usage")
        assert usage_response.status_code == 200 