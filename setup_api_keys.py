#!/usr/bin/env python3
"""
Setup script for Hapivet Prompt Library API keys
"""

import os
import sys
from pathlib import Path

def setup_api_keys():
    """Interactive setup for API keys"""
    print("🔑 Hapivet Prompt Library - API Key Setup")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
        # Read existing values
        existing_keys = {}
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    existing_keys[key] = value
    else:
        print("📝 Creating new .env file")
        existing_keys = {}
    
    print("\nEnter your API keys (press Enter to skip if you don't have one):")
    print()
    
    # Collect API keys
    api_keys = {}
    
    # DeepSeek API Key
    current_deepseek = existing_keys.get('DEEPSEEK_API_KEY', '')
    if current_deepseek and current_deepseek != 'your_deepseek_key':
        print(f"Current DeepSeek API key: {current_deepseek[:8]}...")
        use_existing = input("Use existing DeepSeek API key? (y/n): ").lower().strip()
        if use_existing == 'y':
            api_keys['DEEPSEEK_API_KEY'] = current_deepseek
        else:
            deepseek_key = input("Enter your DeepSeek API key: ").strip()
            if deepseek_key:
                api_keys['DEEPSEEK_API_KEY'] = deepseek_key
    else:
        deepseek_key = input("Enter your DeepSeek API key: ").strip()
        if deepseek_key:
            api_keys['DEEPSEEK_API_KEY'] = deepseek_key
    
    print()
    
    # Google API Key
    current_google = existing_keys.get('GOOGLE_API_KEY', '')
    if current_google and current_google != 'your_google_key':
        print(f"Current Google API key: {current_google[:8]}...")
        use_existing = input("Use existing Google API key? (y/n): ").lower().strip()
        if use_existing == 'y':
            api_keys['GOOGLE_API_KEY'] = current_google
        else:
            google_key = input("Enter your Google API key: ").strip()
            if google_key:
                api_keys['GOOGLE_API_KEY'] = google_key
    else:
        google_key = input("Enter your Google API key: ").strip()
        if google_key:
            api_keys['GOOGLE_API_KEY'] = google_key
    
    print()
    
    # OpenAI API Key (optional)
    current_openai = existing_keys.get('OPENAI_API_KEY', '')
    if current_openai and current_openai != 'your_openai_key':
        print(f"Current OpenAI API key: {current_openai[:8]}...")
        use_existing = input("Use existing OpenAI API key? (y/n): ").lower().strip()
        if use_existing == 'y':
            api_keys['OPENAI_API_KEY'] = current_openai
        else:
            openai_key = input("Enter your OpenAI API key (optional): ").strip()
            if openai_key:
                api_keys['OPENAI_API_KEY'] = openai_key
    else:
        openai_key = input("Enter your OpenAI API key (optional): ").strip()
        if openai_key:
            api_keys['OPENAI_API_KEY'] = openai_key
    
    print()
    
    # Anthropic API Key (optional)
    current_anthropic = existing_keys.get('ANTHROPIC_API_KEY', '')
    if current_anthropic and current_anthropic != 'your_anthropic_key':
        print(f"Current Anthropic API key: {current_anthropic[:8]}...")
        use_existing = input("Use existing Anthropic API key? (y/n): ").lower().strip()
        if use_existing == 'y':
            api_keys['ANTHROPIC_API_KEY'] = current_anthropic
        else:
            anthropic_key = input("Enter your Anthropic API key (optional): ").strip()
            if anthropic_key:
                api_keys['ANTHROPIC_API_KEY'] = anthropic_key
    else:
        anthropic_key = input("Enter your Anthropic API key (optional): ").strip()
        if anthropic_key:
            api_keys['ANTHROPIC_API_KEY'] = anthropic_key
    
    print()
    
    # Other required settings
    api_keys['DATABASE_URL'] = existing_keys.get('DATABASE_URL', 'sqlite:///hapivet.db')
    api_keys['REDIS_URL'] = existing_keys.get('REDIS_URL', 'redis://localhost:6379')
    api_keys['SENTRY_DSN'] = existing_keys.get('SENTRY_DSN', '')
    api_keys['SECRET_KEY'] = existing_keys.get('SECRET_KEY', 'your-secret-key-change-this')
    api_keys['ENVIRONMENT'] = existing_keys.get('ENVIRONMENT', 'development')
    
    # Write to .env file
    print("📝 Writing configuration to .env file...")
    with open(env_file, 'w') as f:
        for key, value in api_keys.items():
            f.write(f"{key}={value}\n")
    
    print("✅ Configuration saved!")
    
    # Show summary
    print("\n📊 Configuration Summary:")
    print("-" * 30)
    configured_providers = []
    if api_keys.get('DEEPSEEK_API_KEY'):
        configured_providers.append("DeepSeek ✅")
    if api_keys.get('GOOGLE_API_KEY'):
        configured_providers.append("Google Gemini ✅")
    if api_keys.get('OPENAI_API_KEY'):
        configured_providers.append("OpenAI ✅")
    if api_keys.get('ANTHROPIC_API_KEY'):
        configured_providers.append("Anthropic ✅")
    
    if configured_providers:
        print("Configured providers:")
        for provider in configured_providers:
            print(f"  - {provider}")
    else:
        print("⚠️  No API keys configured!")
        print("   You need at least one API key to use the AI models.")
    
    print(f"\nDatabase: {api_keys['DATABASE_URL']}")
    print(f"Environment: {api_keys['ENVIRONMENT']}")
    
    print("\n🚀 Next steps:")
    print("1. Start the server: python run.py")
    print("2. Visit: http://localhost:8000/examples")
    print("3. Test the AI models!")

if __name__ == "__main__":
    setup_api_keys() 