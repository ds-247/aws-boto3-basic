import boto3
from botocore.exceptions import ClientError
import os

bucket_name = 'test-bucket-04-30'
region = 'ap-south-1'

def create_bucket(s3_client, bucket_name, region):
    try:
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': region}
        )
        print(f"Bucket {bucket_name} created successfully in {region}.")
    except Exception as e:
        print(f"Error creating bucket: {e}")


def upload_file_to_bucket(s3_client, file_path, bucket_name,  custom_tag, metadata, object_name=None,):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return 
    
    if object_name is None:
        object_name = os.path.basename(file_path)

    s3_client = boto3.client('s3')

    try:
        response = s3_client.upload_file(
            file_path, bucket_name, object_name,
            ExtraArgs={'Metadata': metadata, 'Tagging': custom_tag}
        )
        print(f"File {file_path} uploaded to bucket {bucket_name} as {object_name}.", response)
    except ClientError as e:
        print(f"Error uploading file: {e}")


def delete_bucket(s3_client, bucket_name):
    try:
        s3_client.delete_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} deleted successfully.")
    except ClientError as e:
        print(f"Error deleting bucket: {e}")


def main() :
    s3_client = boto3.client('s3', region_name=region)
    create_bucket(s3_client, bucket_name, region)
    upload_file_to_bucket(s3_client, './files/temp1.txt', bucket_name, 'mytag=tag1', {'meta-key': 'meta-value'})
    

if __name__ == "__main__":
    main()
