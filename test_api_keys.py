#!/usr/bin/env python3
"""
Test script for Hapivet Prompt Library API keys
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.model_manager import ModelManager
from src.utils.types import PromptRequest
from datetime import datetime

async def test_api_keys():
    """Test all configured API keys"""
    print("🧪 Testing API Keys")
    print("=" * 40)
    
    try:
        # Initialize model manager
        model_manager = ModelManager()
        
        # Get available models
        available_models = model_manager.get_available_models()
        
        if not available_models:
            print("❌ No models available. Please check your API keys.")
            return
        
        print(f"✅ Found {len(available_models)} models")
        
        # Test each available model
        test_prompt = "Hello! Please respond with a short greeting and tell me which AI model you are."
        
        for model_info in available_models:
            if not model_info.is_available:
                print(f"⚠️  {model_info.id}: Not available (no API key)")
                continue
            
            print(f"\n🧪 Testing {model_info.id}...")
            
            try:
                # Create test request
                request = PromptRequest(
                    id="test-request",
                    user_id="test-user",
                    prompt=test_prompt,
                    model_preference=model_info.id,
                    max_tokens=100,
                    timestamp=datetime.utcnow()
                )
                
                # Process request
                response = await model_manager.process_request(request)
                
                print(f"✅ {model_info.id}: Success!")
                print(f"   Response: {response.response[:100]}...")
                print(f"   Tokens: {response.tokens_used}")
                print(f"   Cost: ${response.cost:.6f}")
                
            except Exception as e:
                print(f"❌ {model_info.id}: Failed - {str(e)}")
        
        # Test auto-selection
        print(f"\n🧪 Testing auto-selection...")
        try:
            request = PromptRequest(
                id="test-auto",
                user_id="test-user",
                prompt=test_prompt,
                model_preference="auto",
                max_tokens=100,
                timestamp=datetime.utcnow()
            )
            
            response = await model_manager.process_request(request)
            
            print(f"✅ Auto-selection: Success!")
            print(f"   Selected model: {response.model_used}")
            print(f"   Response: {response.response[:100]}...")
            print(f"   Tokens: {response.tokens_used}")
            print(f"   Cost: ${response.cost:.6f}")
            
        except Exception as e:
            print(f"❌ Auto-selection: Failed - {str(e)}")
        
        print(f"\n🎉 API key testing completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    asyncio.run(test_api_keys()) 