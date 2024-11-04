# 🚀 Secure File Upload API with Cloud Integration

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0.1-green.svg)](https://flask.palletsprojects.com/)
[![AWS S3](https://img.shields.io/badge/AWS-S3-orange.svg)](https://aws.amazon.com/s3/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

A secure and scalable RESTful API service that enables users to upload files to cloud storage (AWS S3) and retrieve them via presigned URLs. Built with Flask and integrated with AWS S3, this API handles various file types, implements security best practices, and provides easy file management.

## 📑 Table of Contents

- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [API Documentation](#-api-documentation)
- [Security](#-security)
- [Error Handling](#-error-handling)
- [Contributing](#-contributing)

## ✨ Features

- 📤 Secure file upload to AWS S3
- 🔗 Generated presigned URLs for file access
- 🛡️ API key authentication
- 📝 Comprehensive file metadata
- ⚡ Support for various file types
- 🔒 Security best practices
- 📊 File size validation
- 🎯 Filename sanitization
- 📋 Detailed error handling

## 🔧 Prerequisites

- Python 3.8 or higher
- AWS Account with S3 access
- pip (Python package manager)
- Virtual environment (recommended)

## 🚀 Installation

1. **Clone the repository**
```bash
git clone https://github.com/phostilite/file-upload-api.git
cd file-upload-api
```

2. **Create and activate virtual environment**
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/MacOS
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
Create a `.env` file in the root directory:
```env
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=your_aws_region
S3_BUCKET_NAME=your_bucket_name
API_KEY=your_secure_api_key
```

5. **Create required directories**
```bash
mkdir temp_uploads logs
```

## ⚙️ Configuration

The application uses a configuration class system that can be found in `config.py`. Key configurations include:

```python
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max file size
ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif',
    'doc', 'docx', 'xls', 'xlsx', 'mp3', 'mp4'
}
S3_URL_EXPIRATION = 7 * 24 * 60 * 60  # 7 days in seconds
```

## 📚 API Documentation

### Authentication

All API endpoints require authentication using an API key.

**Header Required:**
```
X-API-Key: your_api_key
```

### 1. Upload File

Upload a file to the system. The file will be stored in AWS S3, and a presigned URL will be generated for access.

**Endpoint:** `POST /upload`

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body:
  - `file`: File to upload (required)

**Success Response:**
```json
{
    "message": "File uploaded successfully",
    "file_id": "20240103_123456_abcd1234.jpg",
    "original_filename": "photo.jpg",
    "file_type": "image/jpeg",
    "file_size": 1048576,
    "upload_timestamp": "2024-01-03T12:34:56.789Z",
    "download_url": "https://your-bucket.s3.amazonaws.com/...",
    "url_expires_at": "2024-01-10T12:34:56.789Z"
}
```

**Error Responses:**

1. No File Provided
```json
{
    "error": "No file part in the request",
    "status_code": 400
}
```

2. File Too Large
```json
{
    "error": "File too large. Maximum size allowed is 10MB",
    "status_code": 413
}
```

3. Invalid File Type
```json
{
    "error": "File type not allowed",
    "status_code": 400
}
```

4. Invalid API Key
```json
{
    "error": "Invalid API key",
    "status_code": 401
}
```

### 2. Get File Information

Retrieve metadata about a previously uploaded file.

**Endpoint:** `GET /files/{file_id}`

**Parameters:**
- `file_id`: Unique identifier of the file (required)

**Success Response:**
```json
{
    "file_id": "20240103_123456_abcd1234.jpg",
    "file_type": "image/jpeg",
    "file_size": 1048576,
    "last_modified": "2024-01-03T12:34:56.789Z",
    "download_url": "https://your-bucket.s3.amazonaws.com/...",
    "url_expires_at": "2024-01-10T12:34:56.789Z"
}
```

**Error Responses:**

1. File Not Found
```json
{
    "error": "File not found",
    "status_code": 404
}
```

2. Invalid File ID Format
```json
{
    "error": "Invalid file ID format",
    "status_code": 400
}
```

## 🛡️ Security

The API implements several security measures:

1. **File Validation**
   - Size limit: 10MB
   - Allowed file types: Configured in `ALLOWED_EXTENSIONS`
   - Content type verification
   - Executable file blocking

2. **Input Sanitization**
   - Filename sanitization to prevent path traversal
   - XSS prevention in filenames
   - Maximum filename length enforcement

3. **Access Control**
   - API key authentication
   - Temporary presigned URLs
   - Private S3 bucket configuration

4. **Error Handling**
   - Secure error messages
   - Proper status codes
   - Detailed logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

For support, email ps4798214@gmail.com or create an issue in the repository.

---

Built with ❤️ by Priyanshu Sharma