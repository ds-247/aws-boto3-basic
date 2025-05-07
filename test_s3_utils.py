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

BUCKET_NAME = 'test-bucket'
REGION = 'ap-south-1'
NUM_OF_FILES = 2000
TAG_KEY = 'type'
TAG_VALUE_ODD = 'odd'
TAG_VALUE_EVEN = 'even'

@mock_aws
def test_create_bucket():
    s3 = boto3.client('s3', region_name=REGION)
    success = create_bucket(s3, BUCKET_NAME, REGION)
    assert success is True
    response = s3.list_buckets()
    bucket_names = [bucket['Name'] for bucket in response['Buckets']]
    assert BUCKET_NAME in bucket_names


@mock_aws
def test_upload_files():
    s3 = boto3.client('s3', region_name=REGION)
    create_bucket(s3, BUCKET_NAME, REGION)
    success = upload_files(s3, BUCKET_NAME, number_of_files=NUM_OF_FILES)
    assert success is True
    response = s3.list_objects(Bucket=BUCKET_NAME)
    assert len(response.get('Contents', [])) == NUM_OF_FILES


@mock_aws
def test_list_bucket_objects():
    s3 = boto3.client('s3', region_name=REGION)
    create_bucket(s3, BUCKET_NAME, REGION)
    upload_files(s3, BUCKET_NAME, number_of_files=NUM_OF_FILES)
    objects = list_bucket_objects(s3, BUCKET_NAME)
    assert objects is not None
    assert len(objects) == NUM_OF_FILES
    for obj in objects:
        assert 'Key' in obj
        assert 'Tags' in obj
        assert 'Metadata' in obj


@mock_aws
def test_filter_objects():
    objects = [
        {'Key': 'file1.txt', 'Tags': {TAG_KEY: TAG_VALUE_ODD}},
        {'Key': 'file2.txt', 'Tags': {TAG_KEY: TAG_VALUE_EVEN}},
        {'Key': 'file3.txt', 'Tags': {TAG_KEY: TAG_VALUE_ODD}}
    ]
    filtered = filter_objects(objects, TAG_KEY, TAG_VALUE_ODD)
    assert len(filtered) == 2
    assert filtered[0]['Key'] == 'file1.txt'
    assert filtered[1]['Key'] == 'file3.txt'


@mock_aws
def test_delete_object():
    s3 = boto3.client('s3', region_name=REGION)
    create_bucket(s3, BUCKET_NAME, REGION)
    upload_files(s3, BUCKET_NAME, number_of_files=NUM_OF_FILES)
    all_objects = list_bucket_objects(s3,BUCKET_NAME)
    to_delete = filter_objects(all_objects, TAG_KEY, TAG_VALUE_ODD)
    success =  delete_object(s3, BUCKET_NAME, to_delete)
    assert success is True
    remaining = s3.list_objects(Bucket=BUCKET_NAME).get('Contents', [])
    remaining_keys = [obj['Key'] for obj in remaining]
    deleted_keys = [obj['Key'] for obj in to_delete]
    for key in deleted_keys:
        assert key not in remaining_keys