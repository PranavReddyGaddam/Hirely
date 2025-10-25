"""
Test AWS S3 Connection
Run this to verify S3 credentials and bucket access are working correctly.
"""
import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# AWS Credentials (from environment variables)
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")

def test_s3_connection():
    """Test S3 connection and bucket access"""
    
    print("=" * 60)
    print("AWS S3 Connection Test")
    print("=" * 60)
    
    # Check environment variables
    print("\n📋 Checking environment variables...")
    required_vars = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_S3_BUCKET"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("\nPlease set these in your .env file:")
        for var in missing_vars:
            print(f"  {var}=your_value_here")
        return False
    
    print("✅ All required environment variables found")
    print(f"   Region: {AWS_REGION}")
    print(f"   Bucket: {AWS_S3_BUCKET}")
    
    # Test S3 client creation
    print("\n🔌 Creating S3 client...")
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        print("✅ S3 client created successfully")
    except Exception as e:
        print(f"❌ Failed to create S3 client: {e}")
        return False
    
    # Test bucket access
    print("\n🪣 Testing bucket access...")
    try:
        response = s3_client.head_bucket(Bucket=AWS_S3_BUCKET)
        print(f"✅ Successfully connected to bucket: {AWS_S3_BUCKET}")
        print(f"   Metadata: {response.get('ResponseMetadata', {}).get('HTTPStatusCode')}")
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', '')
        if error_code == '404':
            print(f"❌ Bucket '{AWS_S3_BUCKET}' not found")
            print("   Please create the bucket in AWS S3 Console")
        elif error_code == '403':
            print(f"❌ Access denied to bucket '{AWS_S3_BUCKET}'")
            print("   Please check IAM permissions")
        else:
            print(f"❌ Error accessing bucket: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    # Test upload
    print("\n📤 Testing upload capability...")
    test_key = "test-upload.txt"
    test_content = b"This is a test file to verify S3 upload works correctly"
    
    try:
        s3_client.put_object(
            Bucket=AWS_S3_BUCKET,
            Key=test_key,
            Body=test_content,
            ContentType='text/plain'
        )
        print(f"✅ Test file uploaded successfully: {test_key}")
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False
    
    # Test download
    print("\n📥 Testing download capability...")
    try:
        response = s3_client.get_object(Bucket=AWS_S3_BUCKET, Key=test_key)
        content = response['Body'].read()
        if content == test_content:
            print(f"✅ Test file downloaded successfully")
        else:
            print(f"⚠️  Downloaded content doesn't match")
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False
    
    # Cleanup test file
    print("\n🧹 Cleaning up test file...")
    try:
        s3_client.delete_object(Bucket=AWS_S3_BUCKET, Key=test_key)
        print(f"✅ Test file deleted successfully")
    except Exception as e:
        print(f"⚠️  Failed to delete test file: {e}")
    
    print("\n" + "=" * 60)
    print("✅ S3 Connection Test PASSED!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = test_s3_connection()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        exit(1)
