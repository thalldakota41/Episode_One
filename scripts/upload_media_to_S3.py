import boto3
import os
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Retrieve the bucket name from environment variables
BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
if not BUCKET_NAME:
    print("Bucket name is not set. Please check your environment variables.")
    exit(1)

# Define the local file path and the S3 file path
local_file_path = '../media/screenplays/creators/Adrian_Cruz.jpg'  # Use relative path from the 'scripts' directory
s3_file_path = 'media/screenplays/creators/Adrian_Cruz.jpg'

def upload_file_to_s3(local_file_path, s3_file_path, bucket_name):
    s3 = boto3.client('s3')

    # Print out the absolute path for debugging
    abs_local_file_path = os.path.abspath(local_file_path)
    print(f"Absolute path of the local file: {abs_local_file_path}")
    
    # Check if the file exists
    if not os.path.isfile(local_file_path):
        print(f"The file {local_file_path} was not found.")
        return

    try:
        s3.upload_file(local_file_path, bucket_name, s3_file_path)
        print(f"File {local_file_path} uploaded to S3 bucket {bucket_name} as {s3_file_path}.")
    except NoCredentialsError:
        print("Credentials not available. Please check your AWS credentials.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    upload_file_to_s3(local_file_path, s3_file_path, BUCKET_NAME)
