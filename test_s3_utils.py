import boto3
import pytest
from moto import mock_aws

from s3_utils import (  
    create_bucket,
    upload_files,
    list_bucket_objects,
    filter_objects,
    delete_object,
)

bucket_name = 'test-bucket'
region = 'ap-south-1'
num_of_files = 5

@mock_aws
def test_create_bucket():
    s3 = boto3.client('s3', region_name=region)
    create_bucket(s3, bucket_name, region)
    response = s3.list_buckets()
    bucket_names = [bucket['Name'] for bucket in response['Buckets']]
    
    assert bucket_name in bucket_names


@mock_aws
def test_upload_files():
    s3 = boto3.client('s3', region_name=region)
    create_bucket(s3, bucket_name, region)
    upload_files(s3, bucket_name, number_of_files=num_of_files)
    response = s3.list_objects(Bucket=bucket_name)
    assert len(response.get('Contents', [])) == num_of_files


@mock_aws
def test_list_bucket_objects():
    s3 = boto3.client('s3', region_name=region)
    create_bucket(s3, bucket_name, region)
    upload_files(s3, bucket_name, number_of_files=num_of_files)
    objects = list_bucket_objects(s3, bucket_name)
    assert len(objects) == num_of_files
    for obj in objects:
        assert 'Key' in obj
        assert 'Tags' in obj
        assert 'Metadata' in obj


@mock_aws
def test_filter_objects():
    objects = [
        {'Key': 'file1.txt', 'Tags': {'type': 'odd'}},
        {'Key': 'file2.txt', 'Tags': {'type': 'even'}},
        {'Key': 'file3.txt', 'Tags': {'type': 'odd'}}
    ]
    filtered = filter_objects(objects, 'type', 'odd')
    assert len(filtered) == 2
    assert filtered[0]['Key'] == 'file1.txt'
    assert filtered[1]['Key'] == 'file3.txt'


@mock_aws
def test_delete_object():
    s3 = boto3.client('s3', region_name=region)
    create_bucket(s3, bucket_name, region)
    upload_files(s3, bucket_name, number_of_files=num_of_files)
    all_objects = list_bucket_objects(s3,bucket_name)
    to_delete = filter_objects(all_objects, 'type', 'odd')
    delete_object(s3, bucket_name, to_delete)
    remaining = s3.list_objects(Bucket=bucket_name).get('Contents', [])
    remaining_keys = [obj['Key'] for obj in remaining]
    deleted_keys = [obj['Key'] for obj in to_delete]
    for key in deleted_keys:
        assert key not in remaining_keys