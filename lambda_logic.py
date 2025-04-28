import boto3
import urllib.parse


def copy_object_from_bucket(source_bucket, source_key, destination_bucket) :

    s3 = boto3.client('s3')
    
    try:

        copy_source = {
            'Bucket': source_bucket,
            'Key': source_key
        }
    
        s3.copy(CopySource=copy_source, Bucket=destination_bucket, Key= source_key)
        print(f'Copied {source_bucket}/{source_key} to {destination_bucket}/{source_key}')

    except Exception as e:
        print(f'Error copying object: {e}')



def lambda_handler(event, context):
    # Extract information from the event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    destination_bucket = 'dst-bkt-04-28' 
    
    copy_object_from_bucket(bucket_name, object_key, destination_bucket)
    
