import logging
import sys
from datetime import datetime
import json
from typing import Dict, Any

class ComplianceFormatter(logging.Formatter):
    """Custom formatter that adds compliance and audit information"""
    
    def format(self, record: logging.LogRecord) -> str:
        # Add timestamp
        record.timestamp = datetime.utcnow().isoformat()
        
        # Add compliance flag for medical-related logs
        if hasattr(record, 'medical_data'):
            record.compliance_flag = "MEDICAL_DATA"
        
        # Format as JSON for structured logging
        log_data = {
            "timestamp": record.timestamp,
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'compliance_flag'):
            log_data['compliance_flag'] = record.compliance_flag
            
        return json.dumps(log_data)

def setup_logging(log_level: str = "INFO"):
    """Configure logging for the application"""
    
    # Create formatters
    compliance_formatter = ComplianceFormatter()
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    
    # File handler for audit logs
    audit_handler = logging.FileHandler('audit.log')
    audit_handler.setFormatter(compliance_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    root_logger.addHandler(console_handler)
    root_logger.addHandler(audit_handler)
    
    # Configure specific loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    
    return root_logger