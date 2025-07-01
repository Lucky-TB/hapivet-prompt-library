from typing import Dict, List, Optional, Any
from src.utils.types import PromptRequest, ModelCapability
from src.utils.config import config_manager
from src.utils.logger import LoggerMixin
import re


class PromptOptimizer(LoggerMixin):
    """Optimizes prompts for different AI models"""
    
    def __init__(self):
        self.model_templates = self._load_model_templates()
        self.optimization_rules = self._load_optimization_rules()
    
    def _load_model_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load model-specific prompt templates"""
        return {
            'openai': {
                'system_prefix': "You are a helpful AI assistant.",
                'user_format': "User: {prompt}\nAssistant:",
                'context_format': "Context: {context}\n\nUser: {prompt}\nAssistant:",
                'coding_prefix': "You are an expert programmer. Write clean, efficient code with explanations.",
                'reasoning_prefix': "You are a logical reasoning expert. Think step by step and explain your reasoning."
            },
            'anthropic': {
                'system_prefix': "You are a helpful AI assistant.",
                'user_format': "Human: {prompt}\n\nAssistant:",
                'context_format': "Context: {context}\n\nHuman: {prompt}\n\nAssistant:",
                'coding_prefix': "You are an expert programmer. Write clean, efficient code with explanations.",
                'reasoning_prefix': "You are a logical reasoning expert. Think step by step and explain your reasoning."
            },
            'google': {
                'system_prefix': "You are a helpful AI assistant.",
                'user_format': "{prompt}",
                'context_format': "Context: {context}\n\n{prompt}",
                'coding_prefix': "You are an expert programmer. Write clean, efficient code with explanations.",
                'reasoning_prefix': "You are a logical reasoning expert. Think step by step and explain your reasoning."
            },
            'deepseek': {
                'system_prefix': "You are a helpful AI assistant.",
                'user_format': "User: {prompt}\nAssistant:",
                'context_format': "Context: {context}\n\nUser: {prompt}\nAssistant:",
                'coding_prefix': "You are an expert programmer. Write clean, efficient code with explanations.",
                'reasoning_prefix': "You are a logical reasoning expert. Think step by step and explain your reasoning."
            }
        }
    
    def _load_optimization_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load prompt optimization rules"""
        return {
            'coding': [
                {
                    'pattern': r'\b(write|create|build|develop|code|program)\b',
                    'enhancement': 'Please provide the code with detailed comments and explanations.',
                    'priority': 'high'
                },
                {
                    'pattern': r'\b(debug|fix|error|bug)\b',
                    'enhancement': 'Please analyze the issue step by step and provide a solution.',
                    'priority': 'high'
                },
                {
                    'pattern': r'\b(algorithm|data structure|optimization)\b',
                    'enhancement': 'Please explain the algorithm complexity and provide an efficient solution.',
                    'priority': 'medium'
                }
            ],
            'reasoning': [
                {
                    'pattern': r'\b(explain|analyze|compare|why|how)\b',
                    'enhancement': 'Please provide a detailed analysis with step-by-step reasoning.',
                    'priority': 'high'
                },
                {
                    'pattern': r'\b(logic|reasoning|argument)\b',
                    'enhancement': 'Please present your reasoning clearly and logically.',
                    'priority': 'medium'
                }
            ],
            'text-generation': [
                {
                    'pattern': r'\b(write|create|generate|compose)\b',
                    'enhancement': 'Please create engaging and well-structured content.',
                    'priority': 'medium'
                }
            ]
        }
    
    def optimize_prompt(self, request: PromptRequest, model_provider: str, capabilities: List[str]) -> str:
        """Optimize prompt for a specific model"""
        try:
            original_prompt = request.prompt
            context = request.context
            
            # Detect prompt type and apply optimizations
            prompt_type = self._detect_prompt_type(original_prompt)
            optimized_prompt = self._apply_optimizations(original_prompt, prompt_type)
            
            # Apply model-specific formatting
            formatted_prompt = self._apply_model_formatting(
                optimized_prompt, context, model_provider, prompt_type
            )
            
            self.logger.info(
                "Prompt optimized",
                original_length=len(original_prompt),
                optimized_length=len(formatted_prompt),
                model_provider=model_provider,
                prompt_type=prompt_type
            )
            
            return formatted_prompt
            
        except Exception as e:
            self.log_error(e, {"model_provider": model_provider, "capabilities": capabilities})
            return request.prompt
    
    def _detect_prompt_type(self, prompt: str) -> str:
        """Detect the type of prompt based on content"""
        prompt_lower = prompt.lower()
        
        # Check for coding-related keywords
        coding_keywords = ['code', 'program', 'function', 'class', 'debug', 'algorithm', 'api', 'database', 'sql']
        if any(keyword in prompt_lower for keyword in coding_keywords):
            return 'coding'
        
        # Check for reasoning-related keywords
        reasoning_keywords = ['explain', 'analyze', 'compare', 'why', 'how', 'reason', 'logic', 'argument']
        if any(keyword in prompt_lower for keyword in reasoning_keywords):
            return 'reasoning'
        
        # Default to text generation
        return 'text-generation'
    
    def _apply_optimizations(self, prompt: str, prompt_type: str) -> str:
        """Apply optimizations based on prompt type"""
        optimized_prompt = prompt
        
        if prompt_type in self.optimization_rules:
            rules = self.optimization_rules[prompt_type]
            
            for rule in rules:
                if re.search(rule['pattern'], prompt, re.IGNORECASE):
                    if rule['priority'] == 'high':
                        optimized_prompt = f"{optimized_prompt}\n\n{rule['enhancement']}"
                    else:
                        optimized_prompt = f"{optimized_prompt}\n{rule['enhancement']}"
        
        return optimized_prompt
    
    def _apply_model_formatting(self, prompt: str, context: str, model_provider: str, prompt_type: str) -> str:
        """Apply model-specific formatting"""
        if model_provider not in self.model_templates:
            return prompt
        
        template = self.model_templates[model_provider]
        
        # Add type-specific prefix
        if prompt_type == 'coding' and 'coding_prefix' in template:
            prefix = template['coding_prefix']
        elif prompt_type == 'reasoning' and 'reasoning_prefix' in template:
            prefix = template['reasoning_prefix']
        else:
            prefix = template.get('system_prefix', '')
        
        # Format based on whether context is provided
        if context:
            if 'context_format' in template:
                return f"{prefix}\n\n{template['context_format'].format(context=context, prompt=prompt)}"
            else:
                return f"{prefix}\n\nContext: {context}\n\n{prompt}"
        else:
            if 'user_format' in template:
                return f"{prefix}\n\n{template['user_format'].format(prompt=prompt)}"
            else:
                return f"{prefix}\n\n{prompt}"
    
    def get_prompt_statistics(self, prompt: str) -> Dict[str, Any]:
        """Get statistics about a prompt"""
        try:
            words = prompt.split()
            sentences = re.split(r'[.!?]+', prompt)
            paragraphs = prompt.split('\n\n')
            
            # Count code blocks
            code_blocks = len(re.findall(r'```[\s\S]*?```', prompt))
            
            # Count URLs
            urls = len(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', prompt))
            
            return {
                'word_count': len(words),
                'character_count': len(prompt),
                'sentence_count': len([s for s in sentences if s.strip()]),
                'paragraph_count': len([p for p in paragraphs if p.strip()]),
                'code_blocks': code_blocks,
                'urls': urls,
                'estimated_tokens': len(words) * 1.3  # Rough estimation
            }
            
        except Exception as e:
            self.log_error(e, {"prompt_length": len(prompt)})
            return {}
    
    def suggest_improvements(self, prompt: str) -> List[str]:
        """Suggest improvements for a prompt"""
        suggestions = []
        
        try:
            # Check prompt length
            if len(prompt) < 10:
                suggestions.append("Consider providing more context or details in your prompt.")
            elif len(prompt) > 1000:
                suggestions.append("Consider breaking down your prompt into smaller, more focused requests.")
            
            # Check for clarity
            if not re.search(r'\?$', prompt.strip()):
                suggestions.append("Consider ending your prompt with a question to get more specific responses.")
            
            # Check for specificity
            vague_words = ['good', 'better', 'nice', 'help', 'something']
            if any(word in prompt.lower() for word in vague_words):
                suggestions.append("Consider using more specific terms to get better results.")
            
            # Check for context
            if len(prompt.split()) < 5:
                suggestions.append("Consider providing more context to help the AI understand your request better.")
            
            return suggestions
            
        except Exception as e:
            self.log_error(e, {"prompt_length": len(prompt)})
            return ["Unable to analyze prompt for improvements."]
    
    def create_prompt_template(self, task_type: str, model_provider: str) -> str:
        """Create a template prompt for a specific task type and model"""
        try:
            templates = {
                'coding': {
                    'openai': "Write a Python function that {description}. Include error handling and documentation.",
                    'anthropic': "Create a Python function that {description}. Provide clear explanations and error handling.",
                    'google': "Develop a Python function for {description}. Include comments and error handling.",
                    'deepseek': "Code a Python function that {description}. Add proper documentation and error handling."
                },
                'reasoning': {
                    'openai': "Analyze the following problem step by step: {description}. Explain your reasoning process.",
                    'anthropic': "Let's think through this problem: {description}. Provide a detailed analysis with reasoning.",
                    'google': "Consider this problem: {description}. Break it down and explain your approach.",
                    'deepseek': "Examine this problem: {description}. Provide a logical analysis with step-by-step reasoning."
                },
                'text-generation': {
                    'openai': "Write a {style} text about {topic}. Make it engaging and informative.",
                    'anthropic': "Create {style} content about {topic}. Ensure it's well-structured and engaging.",
                    'google': "Generate {style} text on {topic}. Make it compelling and informative.",
                    'deepseek': "Compose {style} content about {topic}. Ensure clarity and engagement."
                }
            }
            
            if task_type in templates and model_provider in templates[task_type]:
                return templates[task_type][model_provider]
            else:
                return "Please provide a {description} for {topic}."
                
        except Exception as e:
            self.log_error(e, {"task_type": task_type, "model_provider": model_provider})
            return "Please provide a detailed request." 