"""
Custom logging configuration to suppress HTTPS errors in Django development server.
This eliminates the "Bad request version" errors that occur with HTTPS requests.
"""

import logging

# Configure logging to suppress HTTPS errors
logging.getLogger('django.server').setLevel(logging.ERROR)

# Create a custom filter for HTTPS-related errors
class HTTPSRequestFilter(logging.Filter):
    def filter(self, record):
        # Filter out HTTPS-related error messages
        https_error_phrases = [
            'Bad request version',
            'Bad request syntax', 
            'Bad HTTP/0.9 request type',
            'You\'re accessing the development server over HTTPS',
            'HTTPS, but it only supports HTTP'
        ]
        
        # Don't log messages containing these phrases
        if record.getMessage():
            for phrase in https_error_phrases:
                if phrase in record.getMessage():
                    return False
        
        return True

# Apply the filter to the server logger
server_logger = logging.getLogger('django.server')
server_logger.addFilter(HTTPSRequestFilter())

# Also suppress these errors at the console level
console_logger = logging.getLogger('console')
console_logger.addFilter(HTTPSRequestFilter())
