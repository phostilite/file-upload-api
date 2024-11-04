import os
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from botocore.exceptions import ClientError
import re

from src.config import Config, configure_logging
from src.exceptions import APIError
from src.utils.file_utils import (
    allowed_file, sanitize_filename, get_file_metadata,
    generate_unique_filename, validate_file_content
)
from src.utils.s3_utils import create_s3_client, generate_presigned_url
from src.utils.security import require_api_key

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Configure logging
configure_logging(app)

# Configure Flask to handle trailing slashes
app.url_map.strict_slashes = False

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize S3 client
s3_client = create_s3_client(
    app.config['AWS_ACCESS_KEY_ID'],
    app.config['AWS_SECRET_ACCESS_KEY'],
    app.config['AWS_REGION']
)

# Add index route
@app.route('/')
def index():
    """Return API information."""
    return jsonify({
        'name': 'File Upload API',
        'version': '1.0',
        'endpoints': {
            'POST /upload': 'Upload a file',
            'GET /files/{file_id}': 'Get file information'
        }
    })

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors with JSON response."""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested URL was not found on the server.',
        'status_code': 404
    }), 404

# Error handlers
@app.errorhandler(APIError)
def handle_api_error(error):
    """Handle custom API errors."""
    response = jsonify({'error': error.message})
    response.status_code = error.status_code
    return response

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error."""
    return jsonify({
        'error': f'File too large. Maximum size allowed is '
                f'{app.config["MAX_CONTENT_LENGTH"] // (1024 * 1024)}MB'
    }), 413

# API Endpoints
@app.route('/upload', methods=['POST'])
@require_api_key
def upload_file():
    """Endpoint to upload a file."""
    try:
        if 'file' not in request.files:
            raise APIError('No file part in the request', 400)
        
        file = request.files['file']
        if file.filename == '':
            raise APIError('No file selected', 400)
        
        if not allowed_file(file.filename, app.config['ALLOWED_EXTENSIONS']):
            raise APIError('File type not allowed', 400)
        
        original_filename = sanitize_filename(file.filename)
        unique_filename = generate_unique_filename(original_filename)
        
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(temp_path)
        
        try:
            is_valid, file_type = validate_file_content(temp_path)
            if not is_valid:
                raise APIError(file_type, 400)
            
            metadata = get_file_metadata(temp_path)
            
            # Upload to S3 with string values
            s3_client.upload_file(
                str(temp_path),
                str(app.config['S3_BUCKET_NAME']),
                str(unique_filename),
                ExtraArgs={'ContentType': str(metadata['type']), 'ACL': 'private'}
            )
            
            # Generate URL
            url = str(generate_presigned_url(
                s3_client,
                app.config['S3_BUCKET_NAME'],
                unique_filename,
                app.config['S3_URL_EXPIRATION']
            ))
            
            response = {
                'message': 'File uploaded successfully',
                'file_id': str(unique_filename),
                'original_filename': str(original_filename),
                'file_type': str(metadata['type']),
                'file_size': int(metadata['size']),
                'upload_timestamp': datetime.now().isoformat(),
                'download_url': url,
                'url_expires_at': (
                    datetime.now() + timedelta(seconds=app.config['S3_URL_EXPIRATION'])
                ).isoformat()
            }
            
            app.logger.info("File uploaded successfully: %s", unique_filename)
            return jsonify(response), 201
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except APIError as e:
        return jsonify({'error': e.message}), e.status_code
    except Exception as e:
        app.logger.error("Upload error: %s", str(e))
        if '413' in str(e):
            return jsonify({'error': 'File too large'}), 413
        return jsonify({'error': str(e)}), 500

@app.route('/files/<file_id>', methods=['GET'])
@require_api_key
def get_file_info(file_id):
    """Endpoint to get file information."""
    try:
        # First validate file_id format
        if not re.match(r'^[\w.-]+$', file_id):
            raise APIError('Invalid file ID format', 400)
        
        try:
            response = s3_client.head_object(
                Bucket=app.config['S3_BUCKET_NAME'],
                Key=file_id
            )
            
            url = generate_presigned_url(
                s3_client,
                app.config['S3_BUCKET_NAME'],
                file_id,
                app.config['S3_URL_EXPIRATION']
            )
            
            # Convert datetime to string to ensure JSON serialization
            last_modified = response['LastModified'].isoformat() if isinstance(response['LastModified'], datetime) else str(response['LastModified'])
            
            file_info = {
                'file_id': file_id,
                'file_type': str(response['ContentType']),
                'file_size': int(response['ContentLength']),
                'last_modified': last_modified,
                'download_url': str(url),
                'url_expires_at': (
                    datetime.now() + timedelta(seconds=app.config['S3_URL_EXPIRATION'])
                ).isoformat()
            }
            
            return jsonify(file_info), 200
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                raise APIError('File not found', 404)
            # For other S3 errors, return 500
            app.logger.error("S3 error: %s", str(e))
            raise APIError('Error accessing file information', 500)
                
    except APIError as e:
        return jsonify({'error': e.message}), e.status_code
    except Exception as e:
        app.logger.error("File info error: %s", str(e))
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)