from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from src.services.auth_service import auth_service
from src.utils.logger import get_logger

logger = get_logger("dashboard_routes")

router = APIRouter()
security = HTTPBearer(auto_error=False)


def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Get current user from token"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = auth_service.verify_token(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return user


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page():
    """Dashboard page HTML"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Hapivet Dashboard</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #f5f7fa;
                color: #333;
            }
            
            .navbar {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 1rem 2rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            
            .navbar h1 {
                font-size: 1.5rem;
                font-weight: 600;
            }
            
            .user-info {
                display: flex;
                align-items: center;
                gap: 1rem;
            }
            
            .user-info span {
                font-weight: 500;
            }
            
            .logout-btn {
                background: rgba(255,255,255,0.2);
                border: 1px solid rgba(255,255,255,0.3);
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 5px;
                cursor: pointer;
                transition: background 0.3s ease;
            }
            
            .logout-btn:hover {
                background: rgba(255,255,255,0.3);
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 2rem;
            }
            
            .welcome-section {
                background: white;
                padding: 2rem;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin-bottom: 2rem;
            }
            
            .welcome-section h2 {
                color: #333;
                margin-bottom: 1rem;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1.5rem;
                margin-bottom: 2rem;
            }
            
            .stat-card {
                background: white;
                padding: 1.5rem;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                border-left: 4px solid #667eea;
            }
            
            .stat-card h3 {
                color: #667eea;
                margin-bottom: 0.5rem;
                font-size: 0.9rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .stat-card .value {
                font-size: 2rem;
                font-weight: 700;
                color: #333;
            }
            
            .actions-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 1.5rem;
            }
            
            .action-card {
                background: white;
                padding: 1.5rem;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                border: 1px solid #e1e5e9;
            }
            
            .action-card h3 {
                color: #333;
                margin-bottom: 1rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .action-card p {
                color: #666;
                margin-bottom: 1rem;
                line-height: 1.6;
            }
            
            .btn {
                display: inline-block;
                padding: 0.75rem 1.5rem;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-weight: 500;
                transition: transform 0.2s ease;
                border: none;
                cursor: pointer;
                font-size: 0.9rem;
            }
            
            .btn:hover {
                transform: translateY(-2px);
            }
            
            .btn-secondary {
                background: #6c757d;
            }
            
            .btn-success {
                background: #28a745;
            }
            
            .btn-warning {
                background: #ffc107;
                color: #333;
            }
            
            .hidden {
                display: none;
            }
            
            .loading {
                text-align: center;
                padding: 2rem;
                color: #666;
            }
            
            .error {
                background: #f8d7da;
                color: #721c24;
                padding: 1rem;
                border-radius: 5px;
                margin-bottom: 1rem;
            }
            
            .success {
                background: #d4edda;
                color: #155724;
                padding: 1rem;
                border-radius: 5px;
                margin-bottom: 1rem;
            }
            
            #promptModal {
                display: flex;
            }
            #promptModal.hidden {
                display: none;
            }
        </style>
    </head>
    <body>
        <nav class="navbar">
            <h1>🚀 Hapivet Dashboard</h1>
            <div class="user-info">
                <span id="username">Loading...</span>
                <button class="logout-btn" onclick="logout()">Logout</button>
            </div>
        </nav>
        
        <div class="container">
            <div id="error" class="error hidden"></div>
            <div id="success" class="success hidden"></div>
            
            <div class="welcome-section">
                <h2>Welcome back, <span id="welcomeUsername">User</span>! 👋</h2>
                <p>Manage your AI prompts, track usage, and optimize costs with Hapivet Prompt Library.</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Total Requests</h3>
                    <div class="value" id="totalRequests">-</div>
                </div>
                <div class="stat-card">
                    <h3>Total Cost</h3>
                    <div class="value" id="totalCost">-</div>
                </div>
                <div class="stat-card">
                    <h3>Tokens Used</h3>
                    <div class="value" id="totalTokens">-</div>
                </div>
                <div class="stat-card">
                    <h3>Active Alerts</h3>
                    <div class="value" id="activeAlerts">-</div>
                </div>
            </div>
            
            <div class="actions-grid">
                <div class="action-card">
                    <h3>🤖 Submit Prompt</h3>
                    <p>Send a prompt to the AI model router. The system will automatically select the best model based on your request.</p>
                    <button class="btn" onclick="openPromptModal()">Submit Prompt</button>
                </div>
                
                <div class="action-card">
                    <h3>📊 Usage Statistics</h3>
                    <p>View detailed usage statistics, cost analysis, and performance metrics for your account.</p>
                    <button class="btn btn-secondary" onclick="viewUsageStats()">View Stats</button>
                </div>
                
                <div class="action-card">
                    <h3>🔔 Alerts & Notifications</h3>
                    <p>Check for any usage alerts, cost warnings, or system notifications.</p>
                    <button class="btn btn-warning" onclick="viewAlerts()">View Alerts</button>
                </div>
                
                <div class="action-card">
                    <h3>💰 Cost Analysis</h3>
                    <p>Analyze your spending patterns and get recommendations for cost optimization.</p>
                    <button class="btn btn-success" onclick="viewCostAnalysis()">Cost Analysis</button>
                </div>
                
                <div class="action-card">
                    <h3>🔧 Available Models</h3>
                    <p>See all available AI models and their current status, pricing, and capabilities.</p>
                    <button class="btn btn-secondary" onclick="viewModels()">View Models</button>
                </div>
                
                <div class="action-card">
                    <h3>📚 API Documentation</h3>
                    <p>Access the complete API documentation with examples and integration guides.</p>
                    <a href="/docs" class="btn btn-secondary" target="_blank">API Docs</a>
                </div>
            </div>
        </div>
        
        <!-- Prompt Modal -->
        <div id="promptModal" class="hidden" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); align-items: center; justify-content: center; z-index: 1000;">
            <div style="background: white; padding: 2rem; border-radius: 10px; width: 90%; max-width: 600px; max-height: 80vh; overflow-y: auto;">
                <h3>Submit AI Prompt</h3>
                <div style="margin-bottom: 1rem;">
                    <label style="display: block; margin-bottom: 0.5rem; font-weight: 500;">Prompt:</label>
                    <textarea id="promptInput" style="width: 100%; height: 120px; padding: 0.75rem; border: 2px solid #e1e5e9; border-radius: 5px; font-size: 1rem; resize: vertical;" placeholder="Enter your prompt here..."></textarea>
                </div>
                <div style="margin-bottom: 1rem;">
                    <label style="display: block; margin-bottom: 0.5rem; font-weight: 500;">Model Preference (optional):</label>
                    <select id="modelSelect" style="width: 100%; padding: 0.75rem; border: 2px solid #e1e5e9; border-radius: 5px; font-size: 1rem;">
                        <option value="auto">Auto-select (recommended)</option>
                        <option value="openai-gpt-4">OpenAI GPT-4</option>
                        <option value="openai-gpt-3.5-turbo">OpenAI GPT-3.5 Turbo</option>
                        <option value="anthropic-claude-3">Anthropic Claude 3</option>
                        <option value="google-gemini-1.5-pro">Google Gemini 1.5 Pro</option>
                        <option value="deepseek-deepseek-chat">DeepSeek Chat</option>
                    </select>
                </div>
                <div style="display: flex; gap: 1rem; justify-content: flex-end;">
                    <button onclick="closePromptModal()" style="padding: 0.75rem 1.5rem; background: #6c757d; color: white; border: none; border-radius: 5px; cursor: pointer;">Cancel</button>
                    <button onclick="submitPrompt()" style="padding: 0.75rem 1.5rem; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer;">Submit</button>
                </div>
            </div>
        </div>
        
        <script>
            let currentUser = null;
            
            // Check authentication on page load
            window.addEventListener('load', async () => {
                const token = localStorage.getItem('access_token');
                if (!token) {
                    window.location.href = '/api/v1/auth/login';
                    return;
                }
                
                try {
                    const response = await fetch('/api/v1/auth/me', {
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    });
                    
                    if (response.ok) {
                        currentUser = await response.json();
                        document.getElementById('username').textContent = currentUser.username;
                        document.getElementById('welcomeUsername').textContent = currentUser.username;
                        loadDashboardData();
                    } else {
                        localStorage.removeItem('access_token');
                        window.location.href = '/api/v1/auth/login';
                    }
                } catch (error) {
                    console.error('Error loading user data:', error);
                    localStorage.removeItem('access_token');
                    window.location.href = '/api/v1/auth/login';
                }
            });
            
            async function loadDashboardData() {
                try {
                    const token = localStorage.getItem('access_token');
                    const userId = localStorage.getItem('user_id');
                    
                    // Load usage stats
                    const statsResponse = await fetch(`/api/v1/usage/${userId}`, {
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    });
                    
                    if (statsResponse.ok) {
                        const stats = await statsResponse.json();
                        document.getElementById('totalRequests').textContent = stats.usage_data.total_requests || 0;
                        document.getElementById('totalCost').textContent = `$${(stats.usage_data.total_cost || 0).toFixed(4)}`;
                        document.getElementById('totalTokens').textContent = stats.usage_data.total_tokens || 0;
                    }
                    
                    // Load alerts
                    const alertsResponse = await fetch('/api/v1/alerts', {
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    });
                    
                    if (alertsResponse.ok) {
                        const alerts = await alertsResponse.json();
                        document.getElementById('activeAlerts').textContent = alerts.length || 0;
                    }
                } catch (error) {
                    console.error('Error loading dashboard data:', error);
                }
            }
            
            function logout() {
                localStorage.removeItem('access_token');
                localStorage.removeItem('username');
                localStorage.removeItem('user_id');
                window.location.href = '/api/v1/auth/login';
            }
            
            function openPromptModal() {
                document.getElementById('promptModal').classList.remove('hidden');
            }
            
            function closePromptModal() {
                document.getElementById('promptModal').classList.add('hidden');
                document.getElementById('promptInput').value = '';
            }
            
            async function submitPrompt() {
                const prompt = document.getElementById('promptInput').value.trim();
                const model = document.getElementById('modelSelect').value;
                
                if (!prompt) {
                    showMessage('Please enter a prompt', 'error');
                    return;
                }
                
                try {
                    const token = localStorage.getItem('access_token');
                    const response = await fetch('/api/v1/prompt', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify({
                            prompt: prompt,
                            model_preference: model === 'auto' ? None : model
                        })
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        showMessage('Prompt submitted successfully!', 'success');
                        closePromptModal();
                        loadDashboardData(); // Refresh stats
                        
                        // Show response in a simple alert (you could make this more sophisticated)
                        alert(`AI Response:\\n\\n${result.response}`);
                    } else {
                        const error = await response.json();
                        showMessage(error.detail || 'Failed to submit prompt', 'error');
                    }
                } catch (error) {
                    showMessage('Network error. Please try again.', 'error');
                }
            }
            
            function viewUsageStats() {
                window.open('/docs#/default/get_usage_stats_api_v1_usage__user_id__get', '_blank');
            }
            
            function viewAlerts() {
                window.open('/docs#/default/get_alerts_api_v1_alerts_get', '_blank');
            }
            
            function viewCostAnalysis() {
                window.open('/docs#/default/get_cost_analysis_api_v1_cost_analysis_get', '_blank');
            }
            
            function viewModels() {
                window.open('/docs#/default/get_available_models_api_v1_models_get', '_blank');
            }
            
            function showMessage(message, type) {
                const errorDiv = document.getElementById('error');
                const successDiv = document.getElementById('success');
                
                errorDiv.classList.add('hidden');
                successDiv.classList.add('hidden');
                
                if (type === 'error') {
                    errorDiv.textContent = message;
                    errorDiv.classList.remove('hidden');
                } else {
                    successDiv.textContent = message;
                    successDiv.classList.remove('hidden');
                }
                
                setTimeout(() => {
                    errorDiv.classList.add('hidden');
                    successDiv.classList.add('hidden');
                }, 5000);
            }
        </script>
    </body>
    </html>
    """ 