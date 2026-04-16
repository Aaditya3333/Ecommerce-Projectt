from django.core.management.commands.runserver import Command as RunserverCommand
from django.core.servers.basehttp import get_internal_wsgi_application
import sys
import os
import logging

class Command(RunserverCommand):
    """
    Custom runserver command that suppresses HTTPS errors and provides a clean output.
    This eliminates the "Bad request version" errors that occur when browsers try HTTPS.
    """
    
    def handle(self, *args, **options):
        # Suppress logging of HTTPS errors
        logging.getLogger('django.server').setLevel(logging.ERROR)
        
        # Suppress specific error messages
        original_stderr = sys.stderr
        
        class FilteredStderr:
            def __init__(self, original_stderr):
                self.original_stderr = original_stderr
            
            def write(self, message):
                # Filter out HTTPS-related error messages
                if any(phrase in message for phrase in [
                    'Bad request version',
                    'Bad request syntax',
                    'Bad HTTP/0.9 request type',
                    'You\'re accessing the development server over HTTPS',
                    'HTTPS, but it only supports HTTP'
                ]):
                    return  # Don't write these messages
                
                self.original_stderr.write(message)
            
            def flush(self):
                self.original_stderr.flush()
        
        # Replace stderr with filtered version
        sys.stderr = FilteredStderr(original_stderr)
        
        try:
            # Call the original runserver command
            super().handle(*args, **options)
        finally:
            # Restore original stderr
            sys.stderr = original_stderr
    
    def get_handler(self, *args, **options):
        """
        Override the handler to provide a custom WSGI application that handles HTTPS gracefully.
        """
        handler = super().get_handler(*args, **options)
        
        # Wrap the handler to catch and handle HTTPS errors
        class HTTPSGracefulHandler:
            def __init__(self, original_handler):
                self.original_handler = original_handler
            
            def __call__(self, environ, start_response):
                try:
                    return self.original_handler(environ, start_response)
                except Exception as e:
                    # Handle HTTPS-related errors gracefully
                    if 'Bad request version' in str(e) or 'Bad request syntax' in str(e):
                        # Return a simple response for HTTPS requests
                        start_response('200 OK', [('Content-Type', 'text/html')])
                        return [b'<html><body><h1>HTTP Only</h1><p>This development server only supports HTTP. Please use <a href="http://127.0.0.1:8000/">http://127.0.0.1:8000/</a></p></body></html>']
                    else:
                        # Re-raise other errors
                        raise
        
        return HTTPSGracefulHandler(handler)
