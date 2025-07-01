import structlog
import logging
from typing import Any, Dict
import sys


def setup_logging(level: str = "INFO") -> None:
    """Setup structured logging"""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Set the root logger level
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper())
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance"""
    return structlog.get_logger(name)


class LoggerMixin:
    """Mixin to add logging capabilities to classes"""
    
    @property
    def logger(self) -> structlog.BoundLogger:
        """Get logger for this class"""
        return get_logger(self.__class__.__name__)
    
    def log_request(self, request_id: str, user_id: str, model: str, tokens: int, cost: float) -> None:
        """Log a prompt request"""
        self.logger.info(
            "Prompt request processed",
            request_id=request_id,
            user_id=user_id,
            model=model,
            tokens=tokens,
            cost=cost
        )
    
    def log_alert(self, alert_type: str, user_id: str, message: str, severity: str) -> None:
        """Log an alert"""
        self.logger.warning(
            "Usage alert generated",
            alert_type=alert_type,
            user_id=user_id,
            message=message,
            severity=severity
        )
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None) -> None:
        """Log an error"""
        self.logger.error(
            "Error occurred",
            error=str(error),
            error_type=type(error).__name__,
            context=context or {}
        ) 