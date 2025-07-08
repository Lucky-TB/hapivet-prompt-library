from typing import Dict, List, Optional, Any, Tuple
from src.models.base_model import BaseAIModel
from src.models.openai_model import OpenAIModel
from src.models.anthropic_model import AnthropicModel
from src.models.gemini_model import GeminiModel
from src.models.deepseek_model import DeepSeekModel
from src.utils.types import PromptRequest, PromptResponse, AIModel
from src.utils.config import config_manager
from src.utils.logger import LoggerMixin
import uuid
from datetime import datetime
import re


class ModelManager(LoggerMixin):
    """Manages AI models and routes requests to appropriate models with intelligent auto-selection"""
    
    def __init__(self):
        self.models: Dict[str, BaseAIModel] = {}
        self._initialize_models()
        self._initialize_model_strengths()
    
    def _initialize_model_strengths(self):
        """Initialize model-specific strengths and capabilities"""
        self.model_strengths = {
            'openai': {
                'primary_strengths': [
                    'conversation', 'natural_language', 'multimodal_reasoning', 
                    'tool_integration', 'coding_reliability', 'general_purpose'
                ],
                'secondary_strengths': [
                    'python', 'javascript', 'typescript', 'api_calling', 
                    'file_reading', 'code_interpreter', 'plugins'
                ],
                'best_for': [
                    'all_around_use', 'product_integrations', 'developers', 
                    'teams', 'apps', 'agents', 'ux_design', 'tutoring'
                ],
                'keywords': [
                    'conversation', 'chat', 'natural', 'human-like', 'intuition',
                    'emotional', 'nuance', 'vision', 'image', 'diagram', 'tool',
                    'plugin', 'api', 'file', 'interpreter', 'python', 'javascript',
                    'typescript', 'comment', 'debug', 'general', 'diverse'
                ]
            },
            'anthropic': {
                'primary_strengths': [
                    'structured_reasoning', 'long_context', 'document_understanding',
                    'ethical_alignment', 'safety', 'professional_writing'
                ],
                'secondary_strengths': [
                    'summaries', 'outlines', 'logical_writing', 'policy', 'essays',
                    'technical_specs', 'politeness', 'restraint', 'conservative'
                ],
                'best_for': [
                    'legal', 'enterprise', 'document_heavy', 'ai_tutors', 
                    'professional_writing', 'long_docs', 'regulated_industries',
                    'education', 'healthcare', 'safety_sensitive'
                ],
                'keywords': [
                    'document', 'pdf', 'research', 'paper', 'legal', 'policy',
                    'essay', 'technical', 'spec', 'summary', 'outline', 'structured',
                    'logical', 'ethical', 'safety', 'regulated', 'enterprise',
                    'professional', 'long', 'context', '200k', 'tokens'
                ]
            },
            'google': {
                'primary_strengths': [
                    'multimodal', 'research_retrieval', 'technical_tasks',
                    'google_integration', 'visual_reasoning'
                ],
                'secondary_strengths': [
                    'web_parsing', 'pdf_parsing', 'spreadsheet_parsing',
                    'mixed_media', 'charts', 'tables', 'gmail', 'docs', 'sheets',
                    'search', 'colab', 'science', 'math'
                ],
                'best_for': [
                    'visually_rich', 'science', 'math_problems', 'google_workspace',
                    'research', 'business_docs', 'charts_tables', 'plots',
                    'scanned_notes', 'handwritten', 'diagrams'
                ],
                'keywords': [
                    'multimodal', 'visual', 'image', 'chart', 'table', 'plot',
                    'diagram', 'scanned', 'handwritten', 'google', 'gmail', 'docs',
                    'sheets', 'colab', 'science', 'math', 'research', 'business',
                    'spreadsheet', 'web', 'pdf', 'mixed', 'media'
                ]
            },
            'deepseek': {
                'primary_strengths': [
                    'open_source_coding', 'vision_language', 'math_problems',
                    'low_level_coding', 'transparency'
                ],
                'secondary_strengths': [
                    'c++', 'java', 'rust', 'community', 'adaptable', 'visual',
                    'reasoning', 'precision', 'competition', 'experiments'
                ],
                'best_for': [
                    'open_source', 'development', 'low_level', 'coding_competitions',
                    'ai_experiments', 'visual_problem_solving', 'math_focused',
                    'c++', 'java', 'rust', 'community_projects'
                ],
                'keywords': [
                    'open_source', 'c++', 'java', 'rust', 'low_level', 'community',
                    'transparent', 'adaptable', 'competition', 'experiment',
                    'visual', 'vision', 'language', 'math', 'gsm8k', 'precision'
                ]
            }
        }
    
    def _initialize_models(self):
        """Initialize all available models"""
        models_config = config_manager.get_models()
        
        for provider, provider_models in models_config.items():
            for model_name, model_config in provider_models.items():
                model_id = f"{provider}-{model_name}"
                model_config['id'] = model_id
                model_config['name'] = model_name
                model_config['provider'] = provider
                
                try:
                    if provider == 'openai':
                        self.models[model_id] = OpenAIModel(model_config)
                    elif provider == 'anthropic':
                        self.models[model_id] = AnthropicModel(model_config)
                    elif provider == 'google':
                        self.models[model_id] = GeminiModel(model_config)
                    elif provider == 'deepseek':
                        self.models[model_id] = DeepSeekModel(model_config)
                    
                    self.logger.info(f"Initialized model: {model_id}")
                except Exception as e:
                    self.logger.error(f"Failed to initialize model {model_id}: {e}")
    
    def _check_api_key_availability(self, model: BaseAIModel) -> bool:
        """Check if a model has a valid API key"""
        if model.provider == 'openai':
            return bool(config_manager.settings.openai_api_key and 
                       config_manager.settings.openai_api_key.strip() and
                       config_manager.settings.openai_api_key != "your_openai_key")
        elif model.provider == 'anthropic':
            return bool(config_manager.settings.anthropic_api_key and 
                       config_manager.settings.anthropic_api_key.strip() and
                       config_manager.settings.anthropic_api_key != "your_anthropic_key")
        elif model.provider == 'google':
            return bool(config_manager.settings.google_api_key and 
                       config_manager.settings.google_api_key.strip() and
                       config_manager.settings.google_api_key != "your_google_key")
        elif model.provider == 'deepseek':
            return bool(config_manager.settings.deepseek_api_key and 
                       config_manager.settings.deepseek_api_key.strip() and
                       config_manager.settings.deepseek_api_key != "your_deepseek_key")
        return False
    
    def _is_model_working(self, model: BaseAIModel) -> bool:
        """Check if a model is actually working (has valid API key and can make requests)"""
        # For now, we'll use the API key availability check
        # In a real implementation, you might want to do a quick test request
        return self._check_api_key_availability(model)
    
    def get_available_models(self) -> List[AIModel]:
        """Get list of all available models with API keys"""
        available_models = []
        for model in self.models.values():
            if self._check_api_key_availability(model):
                model_info = model.get_model_info()
                model_info.is_available = True
                available_models.append(model_info)
            else:
                # Mark as unavailable if no API key
                model_info = model.get_model_info()
                model_info.is_available = False
                available_models.append(model_info)
        return available_models
    
    def get_model_by_id(self, model_id: str) -> Optional[BaseAIModel]:
        """Get a specific model by ID"""
        return self.models.get(model_id)
    
    def select_best_model(self, request: PromptRequest, required_capabilities: List[str] = None) -> Optional[BaseAIModel]:
        """Select the best model for the request based on capabilities and cost"""
        available_models = []
        
        for model in self.models.values():
            if not self._check_api_key_availability(model):
                continue
                
            if not model.is_available_for_request(request):
                continue
            
            # Check if model has required capabilities
            if required_capabilities:
                if not all(model.can_handle_capability(cap) for cap in required_capabilities):
                    continue
            
            available_models.append(model)
        
        if not available_models:
            return None
        
        # Sort by cost (cheapest first)
        available_models.sort(key=lambda m: m.cost_per_1k_tokens)
        
        return available_models[0]
    
    def detect_capabilities(self, prompt: str) -> Dict[str, Any]:
        """Enhanced capability detection with detailed task analysis"""
        prompt_lower = prompt.lower()
        capabilities = {
            'primary_task': None,
            'secondary_tasks': [],
            'context_length': 'short',
            'complexity': 'simple',
            'domain': 'general',
            'specific_requirements': []
        }
        
        # Detect primary task types with enhanced keywords
        task_patterns = {
            'coding': {
                'keywords': [
                    'code', 'program', 'function', 'class', 'debug', 'algorithm', 
                    'api', 'database', 'python', 'javascript', 'java', 'html', 'css', 
                    'sql', 'typescript', 'rust', 'c++', 'compile', 'syntax', 'error',
                    'bug', 'fix', 'implement', 'develop', 'build', 'deploy', 'test',
                    'unit test', 'integration', 'framework', 'library', 'package',
                    'repository', 'git', 'version control', 'refactor', 'optimize'
                ],
                'weight': 10
            },
            'conversation': {
                'keywords': [
                    'chat', 'conversation', 'talk', 'discuss', 'converse', 'dialogue',
                    'casual', 'informal', 'friendly', 'helpful', 'assistant', 'chatbot',
                    'natural', 'human-like', 'personality', 'tone', 'style'
                ],
                'weight': 8
            },
            'document_analysis': {
                'keywords': [
                    'document', 'pdf', 'text', 'extract', 'parse', 'analyze', 'summarize',
                    'outline', 'structure', 'organize', 'categorize', 'classify',
                    'research', 'paper', 'article', 'report', 'review', 'synthesis',
                    'long', 'extensive', 'comprehensive', 'detailed', 'thorough'
                ],
                'weight': 9
            },
            'visual_analysis': {
                'keywords': [
                    'image', 'picture', 'photo', 'visual', 'chart', 'graph', 'diagram',
                    'plot', 'figure', 'illustration', 'drawing', 'sketch', 'design',
                    'layout', 'ui', 'ux', 'interface', 'screenshot', 'screenshot',
                    'multimodal', 'vision', 'optical', 'recognition', 'detect',
                    'identify', 'describe', 'caption', 'annotate'
                ],
                'weight': 9
            },
            'mathematical_reasoning': {
                'keywords': [
                    'math', 'mathematical', 'calculation', 'equation', 'formula',
                    'solve', 'compute', 'calculate', 'statistics', 'probability',
                    'algebra', 'calculus', 'geometry', 'trigonometry', 'arithmetic',
                    'number', 'numeric', 'quantitative', 'analysis', 'modeling',
                    'prediction', 'forecast', 'trend', 'pattern', 'correlation'
                ],
                'weight': 8
            },
            'creative_writing': {
                'keywords': [
                    'write', 'create', 'generate', 'compose', 'craft', 'story',
                    'poem', 'essay', 'article', 'blog', 'content', 'creative',
                    'imaginative', 'fictional', 'narrative', 'descriptive',
                    'persuasive', 'informative', 'entertaining', 'engaging'
                ],
                'weight': 7
            },
            'logical_reasoning': {
                'keywords': [
                    'explain', 'analyze', 'compare', 'why', 'how', 'reason', 'logic',
                    'think', 'consider', 'evaluate', 'assess', 'examine', 'investigate',
                    'deduce', 'infer', 'conclude', 'argument', 'premise', 'conclusion',
                    'valid', 'sound', 'rational', 'systematic', 'methodical'
                ],
                'weight': 8
            },
            'business_analysis': {
                'keywords': [
                    'business', 'market', 'strategy', 'planning', 'analysis',
                    'report', 'presentation', 'proposal', 'recommendation',
                    'financial', 'budget', 'cost', 'revenue', 'profit', 'loss',
                    'investment', 'risk', 'opportunity', 'competitive', 'industry'
                ],
                'weight': 7
            },
            'educational_content': {
                'keywords': [
                    'teach', 'learn', 'education', 'tutorial', 'lesson', 'course',
                    'explain', 'instruct', 'guide', 'help', 'student', 'teacher',
                    'academic', 'scholarly', 'pedagogical', 'curriculum', 'syllabus',
                    'assignment', 'homework', 'exam', 'quiz', 'assessment'
                ],
                'weight': 7
            }
        }
        
        # Score each task type
        task_scores = {}
        for task, pattern in task_patterns.items():
            score = 0
            for keyword in pattern['keywords']:
                if keyword in prompt_lower:
                    score += pattern['weight']
            if score > 0:
                task_scores[task] = score
        
        # Determine primary and secondary tasks
        if task_scores:
            sorted_tasks = sorted(task_scores.items(), key=lambda x: x[1], reverse=True)
            capabilities['primary_task'] = sorted_tasks[0][0]
            capabilities['secondary_tasks'] = [task for task, score in sorted_tasks[1:3] if score > 5]
        
        # Detect context length requirements
        length_indicators = {
            'long': ['long', 'extensive', 'comprehensive', 'detailed', 'thorough', '200k', 'large', 'full'],
            'medium': ['moderate', 'standard', 'normal', 'typical', 'average'],
            'short': ['brief', 'concise', 'quick', 'short', 'summary', 'outline']
        }
        
        for length, indicators in length_indicators.items():
            if any(indicator in prompt_lower for indicator in indicators):
                capabilities['context_length'] = length
                break
        
        # Detect complexity level
        complexity_indicators = {
            'complex': ['complex', 'advanced', 'sophisticated', 'intricate', 'detailed', 'comprehensive'],
            'moderate': ['moderate', 'intermediate', 'standard', 'normal'],
            'simple': ['simple', 'basic', 'elementary', 'straightforward', 'quick']
        }
        
        for complexity, indicators in complexity_indicators.items():
            if any(indicator in prompt_lower for indicator in indicators):
                capabilities['complexity'] = complexity
                break
        
        # Detect domain-specific requirements
        domain_indicators = {
            'legal': ['legal', 'law', 'contract', 'compliance', 'regulation', 'policy'],
            'medical': ['medical', 'health', 'clinical', 'diagnosis', 'treatment', 'patient'],
            'financial': ['financial', 'banking', 'investment', 'trading', 'accounting'],
            'scientific': ['scientific', 'research', 'experiment', 'hypothesis', 'methodology'],
            'technical': ['technical', 'engineering', 'architecture', 'system', 'infrastructure']
        }
        
        for domain, indicators in domain_indicators.items():
            if any(indicator in prompt_lower for indicator in indicators):
                capabilities['domain'] = domain
                break
        
        # Detect specific requirements
        specific_requirements = []
        if any(word in prompt_lower for word in ['free', 'open source', 'transparent']):
            specific_requirements.append('open_source')
        if any(word in prompt_lower for word in ['safe', 'ethical', 'responsible', 'aligned']):
            specific_requirements.append('safety_focused')
        if any(word in prompt_lower for word in ['google', 'gmail', 'docs', 'sheets', 'colab']):
            specific_requirements.append('google_ecosystem')
        if any(word in prompt_lower for word in ['multimodal', 'vision', 'image', 'visual']):
            specific_requirements.append('multimodal')
        if any(word in prompt_lower for word in ['conversation', 'chat', 'natural']):
            specific_requirements.append('conversational')
        
        capabilities['specific_requirements'] = specific_requirements
        
        # Default to general text generation if no specific task detected
        if not capabilities['primary_task']:
            capabilities['primary_task'] = 'text_generation'
        
        return capabilities

    def calculate_model_score(self, model: BaseAIModel, capabilities: Dict[str, Any]) -> float:
        """Calculate a score for how well a model matches the required capabilities"""
        score = 0.0
        provider = model.provider
        
        if provider not in self.model_strengths:
            return score
        
        strengths = self.model_strengths[provider]
        
        # Score based on primary task
        primary_task = capabilities['primary_task']
        if primary_task == 'coding':
            if provider == 'deepseek':
                score += 15  # Best for open-source coding
            elif provider == 'openai':
                score += 12  # Very reliable coding
            elif provider == 'google':
                score += 8   # Solid coding
            elif provider == 'anthropic':
                score += 6   # Good but not specialized
        elif primary_task == 'conversation':
            if provider == 'openai':
                score += 15  # Best natural conversation
            elif provider == 'anthropic':
                score += 10  # Good but more formal
            elif provider == 'google':
                score += 8   # Decent conversation
            elif provider == 'deepseek':
                score += 6   # Basic conversation
        elif primary_task == 'document_analysis':
            if provider == 'anthropic':
                score += 15  # Best for long documents
            elif provider == 'openai':
                score += 10  # Good document handling
            elif provider == 'google':
                score += 12  # Good with mixed media
            elif provider == 'deepseek':
                score += 6   # Basic document handling
        elif primary_task == 'visual_analysis':
            if provider == 'google':
                score += 15  # Best multimodal
            elif provider == 'openai':
                score += 12  # Strong vision
            elif provider == 'deepseek':
                score += 10  # Good vision-language
            elif provider == 'anthropic':
                score += 6   # Basic vision
        elif primary_task == 'mathematical_reasoning':
            if provider == 'deepseek':
                score += 12  # Strong math performance
            elif provider == 'google':
                score += 10  # Good math/science
            elif provider == 'openai':
                score += 8   # Decent math
            elif provider == 'anthropic':
                score += 8   # Decent math
        elif primary_task == 'logical_reasoning':
            if provider == 'anthropic':
                score += 15  # Best structured reasoning
            elif provider == 'openai':
                score += 12  # Good reasoning
            elif provider == 'google':
                score += 8   # Decent reasoning
            elif provider == 'deepseek':
                score += 8   # Decent reasoning
        
        # Score based on context length
        context_length = capabilities['context_length']
        if context_length == 'long':
            if provider == 'anthropic':
                score += 8   # 200K+ tokens
            elif provider == 'google':
                score += 6   # Good context
            elif provider == 'openai':
                score += 4   # Standard context
            elif provider == 'deepseek':
                score += 4   # Standard context
        
        # Score based on specific requirements
        for requirement in capabilities['specific_requirements']:
            if requirement == 'open_source' and provider == 'deepseek':
                score += 10
            elif requirement == 'safety_focused' and provider == 'anthropic':
                score += 10
            elif requirement == 'google_ecosystem' and provider == 'google':
                score += 10
            elif requirement == 'multimodal' and provider == 'google':
                score += 8
            elif requirement == 'conversational' and provider == 'openai':
                score += 8
        
        # Score based on domain
        domain = capabilities['domain']
        if domain == 'legal' and provider == 'anthropic':
            score += 8
        elif domain == 'medical' and provider == 'anthropic':
            score += 8
        elif domain == 'scientific' and provider == 'google':
            score += 8
        elif domain == 'technical' and provider == 'openai':
            score += 6
        
        # Cost adjustment (prefer cheaper models for similar capabilities)
        cost_penalty = model.cost_per_1k_tokens * 1000  # Penalize expensive models
        score -= cost_penalty
        
        return score

    def get_model_fallback_order(self, request: PromptRequest, capabilities: Dict[str, Any] = None) -> List[BaseAIModel]:
        """Get models in fallback order based on intelligent scoring"""
        available_models = []
        
        for model in self.models.values():
            if not self._check_api_key_availability(model):
                continue
                
            if not model.is_available_for_request(request):
                continue
            
            available_models.append(model)
        
        if not available_models:
            return []
        
        # Score each model based on capabilities
        scored_models = []
        for model in available_models:
            score = self.calculate_model_score(model, capabilities or {})
            scored_models.append((model, score))
        
        # Sort by score (highest first)
        scored_models.sort(key=lambda x: x[1], reverse=True)
        
        # Return just the models in order
        return [model for model, score in scored_models]
    
    async def process_request(self, request: PromptRequest) -> PromptResponse:
        """Process a prompt request with enhanced model selection"""
        # Generate request ID if not provided
        if not hasattr(request, 'id') or not request.id:
            request.id = str(uuid.uuid4())
        
        # Detect required capabilities with enhanced analysis
        capabilities = self.detect_capabilities(request.prompt)
        
        # Log detected capabilities for debugging
        self.logger.info(f"Detected capabilities: {capabilities}")
        
        # If specific model is requested, try that first
        if request.model_preference and request.model_preference != 'auto':
            specific_model = self.get_model_by_id(request.model_preference)
            if specific_model and self._check_api_key_availability(specific_model):
                try:
                    self.logger.info(f"Using requested model: {specific_model.model_id}")
                    response = await specific_model.generate_response(request)
                    return response
                except Exception as e:
                    self.logger.warning(f"Requested model {specific_model.model_id} failed: {e}")
                    # Continue to fallback models
        
        # Get models in intelligent fallback order
        fallback_models = self.get_model_fallback_order(request, capabilities)
        
        if not fallback_models:
            raise ValueError("No suitable model available for this request")
        
        # Log the intelligent fallback order for debugging
        model_order = [model.model_id for model in fallback_models]
        self.logger.info(f"Intelligent model selection order: {model_order}")
        self.logger.info(f"Primary task: {capabilities['primary_task']}")
        self.logger.info(f"Context length: {capabilities['context_length']}")
        self.logger.info(f"Complexity: {capabilities['complexity']}")
        
        # Try each model in order until one works
        last_error = None
        for i, model in enumerate(fallback_models):
            try:
                self.logger.info(f"Trying model {i+1}/{len(fallback_models)}: {model.model_id}")
                response = await model.generate_response(request)
                self.logger.info(f"Successfully used model: {model.model_id}")
                return response
            except Exception as e:
                last_error = e
                self.logger.warning(f"Model {model.model_id} failed: {e}")
                # Continue to next model
                continue
        
        # If we get here, all models failed
        error_msg = f"All {len(fallback_models)} available models failed. Last error: {last_error}"
        self.logger.error(error_msg)
        raise ValueError(error_msg)
    
    def get_model_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics for all models"""
        stats = {}
        for model_id, model in self.models.items():
            stats[model_id] = {
                'name': model.name,
                'provider': model.provider,
                'cost_per_1k_tokens': model.cost_per_1k_tokens,
                'max_tokens': model.max_tokens,
                'capabilities': model.capabilities,
                'is_available': self._check_api_key_availability(model)
            }
        return stats 