"""
Static asset handler for S3 events
Handles file uploads and processing
"""
import json
import boto3
import os

s3 = boto3.client('s3')

def handler(event, context):
    """Handle S3 events for static assets"""
    try:
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']
            event_name = record['eventName']
            
            print(f"Processing {event_name} for {bucket}/{key}")
            
            if event_name.startswith('ObjectCreated'):
                # Handle new file upload
                process_new_file(bucket, key)
            elif event_name.startswith('ObjectRemoved'):
                # Handle file deletion
                process_file_deletion(bucket, key)
                
        return {
            'statusCode': 200,
            'body': json.dumps('Static asset processed successfully')
        }
        
    except Exception as e:
        print(f"Error processing static asset: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }

def process_new_file(bucket, key):
    """Process newly uploaded static file"""
    try:
        # Get file metadata
        response = s3.head_object(Bucket=bucket, Key=key)
        content_type = response.get('ContentType', 'application/octet-stream')
        
        # Set appropriate cache headers based on file type
        cache_control = get_cache_control(key, content_type)
        
        # Update object with cache headers
        s3.copy_object(
            Bucket=bucket,
            Key=key,
            CopySource={'Bucket': bucket, 'Key': key},
            MetadataDirective='REPLACE',
            CacheControl=cache_control,
            ContentType=content_type
        )
        
        print(f"Updated cache headers for {key}: {cache_control}")
        
    except Exception as e:
        print(f"Error processing new file {key}: {e}")

def process_file_deletion(bucket, key):
    """Process deleted static file"""
    print(f"File deleted: {bucket}/{key}")
    # Could implement cache invalidation here if needed

def get_cache_control(key, content_type):
    """Determine appropriate cache control headers"""
    if key.endswith('.css') or key.endswith('.js'):
        return 'public, max-age=31536000'  # 1 year for CSS/JS
    elif key.endswith('.png') or key.endswith('.jpg') or key.endswith('.gif'):
        return 'public, max-age=2592000'   # 30 days for images
    elif key.endswith('.ico'):
        return 'public, max-age=31536000'  # 1 year for favicon
    else:
        return 'public, max-age=3600'      # 1 hour default
