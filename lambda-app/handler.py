"""
Lambda handler for Employee Directory Application
Uses Mangum to adapt Flask app for AWS Lambda
"""
import json
import os
from mangum import Mangum
from app import create_app

# Create Flask app once (singleton pattern for cold start optimization)
app = create_app()

# Create Mangum handler for Lambda
handler = Mangum(app, lifespan="off")

def lambda_handler(event, context):
    """Lambda function handler"""
    try:
        # Process the request through Flask app
        response = handler(event, context)
        
        # Add custom headers for performance
        if 'headers' not in response:
            response['headers'] = {}
        
        # Add cache headers for static content
        if 'path' in event and event.get('path', '').startswith('/static/'):
            response['headers']['Cache-Control'] = 'public, max-age=31536000'
        
        # Add CORS headers - restrict to specific origins in production
        allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:8080').split(',')
        origin = event.get('headers', {}).get('origin', '')
        
        if origin in allowed_origins or os.getenv('ENVIRONMENT') == 'development':
            response['headers']['Access-Control-Allow-Origin'] = origin
        else:
            response['headers']['Access-Control-Allow-Origin'] = allowed_origins[0] if allowed_origins else ''
            
        response['headers']['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response['headers']['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response['headers']['Access-Control-Allow-Credentials'] = 'true'
        
        # Add security headers
        response['headers']['X-Content-Type-Options'] = 'nosniff'
        response['headers']['X-Frame-Options'] = 'DENY'
        response['headers']['X-XSS-Protection'] = '1; mode=block'
        response['headers']['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['headers']['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response
        
    except Exception as e:
        # Error handling for Lambda
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')[0]
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': 'An unexpected error occurred' if os.getenv('ENVIRONMENT') != 'development' else str(e)
            })
        }
