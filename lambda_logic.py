import boto3
import urllib.parse
import os

s3 = boto3.client('s3')

def lambda_handler(event, context):
    source_bucket= event['Records'][0]['s3']['bucket']['name']
    source_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    destination_bucket = os.environ['DEST_BUCKET']

    try:
        copy_source = {
            'Bucket': source_bucket,
            'Key': source_key
        }

        response = s3.copy(CopySource=copy_source, Bucket=destination_bucket, Key= source_key)

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise Exception(f"Failed to copy file: {response}")

        print(f'Copied {source_bucket}/{source_key} to {destination_bucket}/{source_key}')

    except Exception as e:
        print(f'Error copying object: {e}')
        raise e