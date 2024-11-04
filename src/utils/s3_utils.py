from typing import Any
import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError

def create_s3_client(aws_access_key_id: str, 
                    aws_secret_access_key: str, 
                    region: str) -> Any:
    """Create and configure S3 client."""
    boto_config = BotoConfig(
        region_name=region,
        signature_version='s3v4'
    )
    
    return boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        config=boto_config
    )

def generate_presigned_url(s3_client: Any, 
                          bucket_name: str, 
                          object_name: str, 
                          expiration: int) -> str:
    """Generate a presigned URL using Signature Version 4."""
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_name},
            ExpiresIn=expiration,
            HttpMethod='GET'
        )
        return url
    except ClientError as e:
        raise e