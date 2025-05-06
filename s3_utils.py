import boto3
from botocore.exceptions import ClientError

BUCKET_NAME = 'test-bucket-04-30'
REGION = 'ap-south-1'
NUM_OF_FILES = 5
FILE_PREFIX = 'temp_file_'
FILE_CONTENT_PREFIX = 'This is random text for file '
TAG_KEY_TYPE = 'type'
TAG_VALUE_EVEN = 'even'
TAG_VALUE_ODD = 'odd'
TAG_KEY_NUMBER = 'number'
METADATA_DESCRIPTION_KEY = 'description'
METADATA_DESCRIPTION_VALUE = 'temp file upload'
FILTER_TAG_KEY = TAG_KEY_TYPE
FILTER_TAG_VALUE = TAG_VALUE_ODD


def create_bucket(s3_client, bucket_name, region):
    try:
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': region}
        )
        print(f"Bucket {bucket_name} created successfully in {region}.")
        return True
    except Exception as e:
        print(f"Error creating bucket: {e}")
        return False


def upload_files(s3_client, bucket_name, number_of_files):
    try:
        for i in range(1, number_of_files + 1):
            object_key = f'{FILE_PREFIX}{i}.txt'
            content = f'{FILE_CONTENT_PREFIX}{FILE_PREFIX}{i}'
            tag_value = TAG_VALUE_EVEN if i % 2 == 0 else TAG_VALUE_ODD
            tags = f'{TAG_KEY_NUMBER}={i}&{TAG_KEY_TYPE}={tag_value}'
            metadata = {TAG_KEY_NUMBER: str(i), METADATA_DESCRIPTION_KEY: METADATA_DESCRIPTION_VALUE}
            s3_client.put_object(
                Bucket=bucket_name,
                Key=object_key,
                Body=content,
                Tagging=tags,
                Metadata=metadata
            )
            print(f'Uploaded {object_key} with {tags}')
    except ClientError as e:
        print(f"Error uploading files: {e}")
        return False
    return True


def filter_objects(objects_data, tag_type, tag_value):
    filtered_objects = []
    for obj in objects_data:
        tags = obj.get('Tags', {})
        if tag_type in tags and tags[tag_type] == tag_value :
            filtered_objects.append({'Key': obj['Key']})
    return filtered_objects


def delete_object(s3_client, bucket_name, object_list):
    try:
        response = s3_client.delete_objects(
            Bucket=bucket_name,
            Delete={
                'Objects': object_list
            },
        )

        deleted = response.get('Deleted', [])
        errors = response.get('Errors', [])

        if errors:
            print(f"Errors occurred while deleting objects: {errors}")
            return False
        
        print(f"Deleted {len(deleted)} objects successfully.")
        return True
    except ClientError as e:
        print(f"Error deleting object: {e}")
        return False


def list_bucket_objects(s3_client, bucket_name):
    objects_data = []
    try:
        response = s3_client.list_objects(Bucket=bucket_name)
        if 'Contents' in response:
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
                objects_data.append(object_info)
        else:
            print(f"No objects found in bucket {bucket_name}.")
            return  objects_data
    except ClientError as e:
        print(f"Error listing objects in bucket: {e}")
        return None
    return objects_data

def main() :
    s3_client = boto3.client('s3', region_name=REGION)

    if not create_bucket(s3_client, BUCKET_NAME, REGION):
        return

    if not upload_files(s3_client, BUCKET_NAME, NUM_OF_FILES):
        return

    objects_data = list_bucket_objects(s3_client, BUCKET_NAME)
    if objects_data is None:
        return

    objects_to_delete = filter_objects(objects_data, FILTER_TAG_KEY, FILTER_TAG_VALUE)
    if not objects_to_delete:
        print("Nothing to delete.")
        return

    if not delete_object(s3_client, BUCKET_NAME, objects_to_delete):
        return
    

if __name__ == "__main__":
    main()
