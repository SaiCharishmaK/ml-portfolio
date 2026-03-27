import boto3
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

print("🚀 Starting S3 Upload Process")
print("="*55)

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
)

bucket = os.getenv('S3_BUCKET_DATA')

if not bucket:
    print("❌ ERROR: S3_BUCKET_DATA not found in .env")
    exit(1)

print(f"📦 Bucket: {bucket}")
print("="*55)

# Upload model files
print("\n📤 Uploading model files...")
model_dir = 'models/best_distilbert'

if not os.path.exists(model_dir):
    print(f"❌ ERROR: {model_dir} not found!")
    exit(1)

uploaded_count = 0
for filename in os.listdir(model_dir):
    local_path = os.path.join(model_dir, filename)
    
    if os.path.isfile(local_path):
        s3_key = f'models/best_distilbert/{filename}'
        try:
            s3_client.upload_file(local_path, bucket, s3_key)
            size = os.path.getsize(local_path) / (1024**2)
            print(f"   ✅ {s3_key} ({size:.1f} MB)")
            uploaded_count += 1
        except Exception as e:
            print(f"   ❌ {s3_key}: {str(e)}")

# Upload results
print("\n📤 Uploading results...")
if os.path.exists('models/bert_results.json'):
    s3_client.upload_file('models/bert_results.json', bucket, 'models/bert_results.json')
    print(f"   ✅ models/bert_results.json")
else:
    print(f"   ⚠️  models/bert_results.json not found (skipped)")

print("\n" + "="*55)
print(f"✅ Upload Complete! ({uploaded_count} files uploaded)")
print("="*55)