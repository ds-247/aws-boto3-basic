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


def list_buckets(s3_client):
    try:
        response = s3_client.list_buckets()
        print("Existing buckets:")
        for bucket in response['Buckets']:
            print(f"  {bucket['Name']}")
    except ClientError as e:
        print(f"Error listing buckets: {e}")

def list_bucket_objects(s3_client, bucket_name):
    try:
        response = s3_client.list_objects(Bucket=bucket_name)

        if 'Contents' in response:
            print(f"Objects in bucket {bucket_name}:")
            for obj in response['Contents']:
                object_key = obj['Key']
                object_info = {'Key': object_key}

                try:
                    metadata_response = s3_client.head_object(Bucket=bucket_name, Key=object_key)
                    object_info['Metadata'] = metadata_response.get('Metadata', {})
                except ClientError as e:
                    print(f"Error getting metadata for '{object_key}': {e}")
                    object_info['Metadata'] = {}

                
                try:
                    tagging_response = s3_client.get_object_tagging(Bucket=bucket_name, Key=object_key)
                    object_info['Tags'] = {tag['Key']: tag['Value'] for tag in tagging_response.get('TagSet', [])}
                except ClientError as e:    
                    if e.response.get('Error', {}).get('Code') == 'NoSuchTagSet':
                        object_info['Tags'] = {}
                    else:
                        print(f"Error getting tags for '{object_key}': {e}")
                        object_info['Tags'] = {}

                print(f"  Key: {object_key}, Metadata: {object_info['Metadata']}, Tags: {object_info['Tags']}")
        else:
            print(f"No objects found in bucket {bucket_name}.")
    except ClientError as e:
        print(f"Error listing objects in bucket: {e}")


def main() :
    s3_client = boto3.client('s3', region_name=region)
    # create_bucket(s3_client, bucket_name, region)
    # upload_file_to_bucket(s3_client, './files/temp1.txt', bucket_name, 'mytag=tag1', {'meta-key': 'meta-value'})

    # list_buckets(s3_client)
    list_bucket_objects(s3_client, bucket_name)
    

if __name__ == "__main__":
    main()
