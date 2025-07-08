from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
import uuid
from src.utils.database import db_manager, User
from src.utils.logger import get_logger

logger = get_logger("auth_service")

class MockAuthService:
    """Mock authentication service for testing purposes"""
    
    def __init__(self):
        self.secret_key = "mock-secret-key-for-testing-only"
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self._mock_users = {
            "admin": {
                "id": 1,
                "username": "admin",
                "api_key": "admin-mock-key-123",
                "role": "admin",
                "created_at": datetime.now()
            },
            "user1": {
                "id": 2,
                "username": "user1",
                "api_key": "user1-mock-key-456",
                "role": "user",
                "created_at": datetime.now()
            },
            "user2": {
                "id": 3,
                "username": "user2",
                "api_key": "user2-mock-key-789",
                "role": "user",
                "created_at": datetime.now()
            },
            "developer": {
                "id": 4,
                "username": "developer",
                "api_key": "dev-mock-key-101",
                "role": "developer",
                "created_at": datetime.now()
            }
        }
        self._ensure_users_in_db()
    
    def _ensure_users_in_db(self):
        """Ensure mock users exist in the database"""
        try:
            session = db_manager.get_session()
            for username, user_data in self._mock_users.items():
                existing_user = session.query(User).filter(User.username == username).first()
                if not existing_user:
                    new_user = User(
                        id=user_data["id"],
                        username=user_data["username"],
                        api_key=user_data["api_key"]
                    )
                    session.add(new_user)
                    session.commit()
                    logger.info(f"Created mock user: {username}")
        except Exception as e:
            logger.error(f"Error ensuring users in DB: {e}")
        finally:
            db_manager.close_session(session)
    
    def authenticate_user(self, username: str, password: str = None) -> Optional[Dict[str, Any]]:
        """Mock authentication - accepts any username with any password"""
        if username in self._mock_users:
            user_data = self._mock_users[username].copy()
            user_data["password"] = "mock-password"  # Mock password
            return user_data
        else:
            # Create a new mock user if username doesn't exist
            new_user_id = len(self._mock_users) + 1
            new_user = {
                "id": new_user_id,
                "username": username,
                "api_key": f"{username}-mock-key-{uuid.uuid4().hex[:8]}",
                "role": "user",
                "created_at": datetime.now(),
                "password": "mock-password"
            }
            self._mock_users[username] = new_user
            
            # Add to database
            try:
                session = db_manager.get_session()
                db_user = User(
                    id=new_user["id"],
                    username=new_user["username"],
                    api_key=new_user["api_key"]
                )
                session.add(db_user)
                session.commit()
                logger.info(f"Created new mock user: {username}")
            except Exception as e:
                logger.error(f"Error creating user in DB: {e}")
            finally:
                db_manager.close_session(session)
            
            return new_user
    
    def create_access_token(self, data: dict) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username = payload.get("sub")
            if username is None:
                return None
            return self._mock_users.get(username)
        except jwt.PyJWTError:
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        return self._mock_users.get(username)
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        for user in self._mock_users.values():
            if user["id"] == user_id:
                return user
        return None
    
    def get_all_users(self) -> list:
        """Get all mock users"""
        return list(self._mock_users.values())
    
    def create_user(self, username: str, role: str = "user") -> Dict[str, Any]:
        """Create a new mock user"""
        new_user_id = len(self._mock_users) + 1
        new_user = {
            "id": new_user_id,
            "username": username,
            "api_key": f"{username}-mock-key-{uuid.uuid4().hex[:8]}",
            "role": role,
            "created_at": datetime.now()
        }
        self._mock_users[username] = new_user
        
        # Add to database
        try:
            session = db_manager.get_session()
            db_user = User(
                id=new_user["id"],
                username=new_user["username"],
                api_key=new_user["api_key"]
            )
            session.add(db_user)
            session.commit()
            logger.info(f"Created new user: {username}")
        except Exception as e:
            logger.error(f"Error creating user in DB: {e}")
        finally:
            db_manager.close_session(session)
        
        return new_user

# Global auth service instance
auth_service = MockAuthService() 