from fastapi import APIRouter, HTTPException, Depends, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from typing import Optional
from src.services.auth_service import auth_service
from src.utils.logger import get_logger

logger = get_logger("auth_routes")

router = APIRouter()
security = HTTPBearer(auto_error=False)


class LoginRequest(BaseModel):
    username: str
    password: str = "mock-password"  # Default mock password


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    username: str
    user_id: int
    role: str


class UserInfo(BaseModel):
    id: int
    username: str
    role: str
    api_key: str
    created_at: str


def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Get current user from token"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = auth_service.verify_token(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return user


@router.get("/login", response_class=HTMLResponse)
async def login_page():
    """Login page HTML"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Hapivet Prompt Library - Login</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .login-container {
                background: white;
                padding: 2rem;
                border-radius: 10px;
                box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
                width: 100%;
                max-width: 400px;
            }
            
            .logo {
                text-align: center;
                margin-bottom: 2rem;
            }
            
            .logo h1 {
                color: #333;
                font-size: 1.8rem;
                margin-bottom: 0.5rem;
            }
            
            .logo p {
                color: #666;
                font-size: 0.9rem;
            }
            
            .form-group {
                margin-bottom: 1.5rem;
            }
            
            label {
                display: block;
                margin-bottom: 0.5rem;
                color: #333;
                font-weight: 500;
            }
            
            input {
                width: 100%;
                padding: 0.75rem;
                border: 2px solid #e1e5e9;
                border-radius: 5px;
                font-size: 1rem;
                transition: border-color 0.3s ease;
            }
            
            input:focus {
                outline: none;
                border-color: #667eea;
            }
            
            .login-btn {
                width: 100%;
                padding: 0.75rem;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s ease;
            }
            
            .login-btn:hover {
                transform: translateY(-2px);
            }
            
            .demo-users {
                margin-top: 1.5rem;
                padding: 1rem;
                background: #f8f9fa;
                border-radius: 5px;
            }
            
            .demo-users h3 {
                color: #333;
                margin-bottom: 0.5rem;
                font-size: 0.9rem;
            }
            
            .demo-users ul {
                list-style: none;
                font-size: 0.8rem;
                color: #666;
            }
            
            .demo-users li {
                margin-bottom: 0.25rem;
            }
            
            .error {
                color: #dc3545;
                background: #f8d7da;
                padding: 0.75rem;
                border-radius: 5px;
                margin-bottom: 1rem;
                display: none;
            }
            
            .success {
                color: #155724;
                background: #d4edda;
                padding: 0.75rem;
                border-radius: 5px;
                margin-bottom: 1rem;
                display: none;
            }
        </style>
    </head>
    <body>
        <div class="login-container">
            <div class="logo">
                <h1>🚀 Hapivet</h1>
                <p>Prompt Library & AI Model Router</p>
            </div>
            
            <div id="error" class="error"></div>
            <div id="success" class="success"></div>
            
            <form id="loginForm">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" required placeholder="Enter any username">
                </div>
                
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" value="mock-password" readonly>
                </div>
                
                <button type="submit" class="login-btn">Login</button>
            </form>
            
            <div class="demo-users">
                <h3>💡 Demo Users (any password works):</h3>
                <ul>
                    <li>• <strong>admin</strong> - Administrator access</li>
                    <li>• <strong>user1</strong> - Regular user</li>
                    <li>• <strong>user2</strong> - Regular user</li>
                    <li>• <strong>developer</strong> - Developer access</li>
                    <li>• <strong>any-username</strong> - Creates new user automatically</li>
                </ul>
            </div>
        </div>
        
        <script>
            document.getElementById('loginForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                
                try {
                    const response = await fetch('/api/v1/auth/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ username, password })
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        localStorage.setItem('access_token', data.access_token);
                        localStorage.setItem('username', data.username);
                        localStorage.setItem('user_id', data.user_id);
                        
                        showMessage('Login successful! Redirecting...', 'success');
                        setTimeout(() => {
                            window.location.href = '/dashboard';
                        }, 1000);
                    } else {
                        const error = await response.json();
                        showMessage(error.detail || 'Login failed', 'error');
                    }
                } catch (error) {
                    showMessage('Network error. Please try again.', 'error');
                }
            });
            
            function showMessage(message, type) {
                const errorDiv = document.getElementById('error');
                const successDiv = document.getElementById('success');
                
                errorDiv.style.display = 'none';
                successDiv.style.display = 'none';
                
                if (type === 'error') {
                    errorDiv.textContent = message;
                    errorDiv.style.display = 'block';
                } else {
                    successDiv.textContent = message;
                    successDiv.style.display = 'block';
                }
            }
        </script>
    </body>
    </html>
    """


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Login endpoint"""
    user = auth_service.authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = auth_service.create_access_token(data={"sub": user["username"]})
    
    logger.info(f"User logged in: {user['username']}")
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        username=user["username"],
        user_id=user["id"],
        role=user["role"]
    )


@router.post("/logout")
async def logout(response: Response):
    """Logout endpoint"""
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserInfo)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return UserInfo(
        id=current_user["id"],
        username=current_user["username"],
        role=current_user["role"],
        api_key=current_user["api_key"],
        created_at=current_user["created_at"].isoformat()
    )


@router.get("/users")
async def get_all_users(current_user: dict = Depends(get_current_user)):
    """Get all users (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    users = auth_service.get_all_users()
    return {"users": users}


@router.post("/users")
async def create_user(username: str, role: str = "user", current_user: dict = Depends(get_current_user)):
    """Create a new user (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if auth_service.get_user_by_username(username):
        raise HTTPException(status_code=400, detail="Username already exists")
    
    new_user = auth_service.create_user(username, role)
    return {"message": "User created successfully", "user": new_user} 