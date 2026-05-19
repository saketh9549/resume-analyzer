"""
Logging configuration
"""
import logging

logger = logging.getLogger(__name__)

def setup_logger():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
