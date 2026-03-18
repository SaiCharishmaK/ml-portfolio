# tests/test_aws_connections.py
import boto3
import psycopg2
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

def test_s3_connection():
    print("\n=== Testing S3 Connection ===")
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv(
                'AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv(
                'AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv(
                'AWS_DEFAULT_REGION')
        )

        # List buckets
        response  = s3.list_buckets()
        buckets   = [b['Name'] for b in
                     response['Buckets']]
        print(f"✅ S3 connected!")
        print(f"   Your buckets: {buckets}")

        # Test upload
        bucket = os.getenv('S3_BUCKET_DATA')
        s3.put_object(
            Bucket=bucket,
            Key='test/connection_test.txt',
            Body=b'AWS S3 connection successful'
        )
        print(f"✅ Test file uploaded to S3")

        # Test download
        obj = s3.get_object(
            Bucket=bucket,
            Key='test/connection_test.txt'
        )
        content = obj['Body'].read().decode()
        print(f"✅ Downloaded: {content}")

        # Cleanup
        s3.delete_object(
            Bucket=bucket,
            Key='test/connection_test.txt'
        )
        print(f"✅ Test file cleaned up")
        return True

    except Exception as e:
        print(f"❌ S3 failed: {e}")
        return False


def test_rds_connection():
    print("\n=== Testing RDS Connection ===")
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT'),
            dbname=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            connect_timeout=10
        )

        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        version = cursor.fetchone()
        print(f"✅ RDS PostgreSQL connected!")
        print(f"   {version[0][:60]}")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ RDS failed: {e}")
        print("\n  Possible reasons:")
        print("  1. RDS not set to Publicly accessible")
        print("  2. Security group missing inbound rule")
        print("  3. Wrong password or endpoint in .env")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("   AWS CONNECTION TESTS")
    print("=" * 50)

    s3_ok  = test_s3_connection()
    rds_ok = test_rds_connection()

    print("\n" + "=" * 50)
    print(f"  S3  : {'✅ PASS' if s3_ok  else '❌ FAIL'}")
    print(f"  RDS : {'✅ PASS' if rds_ok else '❌ FAIL'}")
    print("=" * 50)

    if s3_ok and rds_ok:
        print("\n🎉 All connections working!")
        print("   Ready for Phase 1")
    else:
        print("\n⚠️  Fix failing connections first")
        print("   Paste the error above and I will help")