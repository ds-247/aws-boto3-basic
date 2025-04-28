import boto3

def create_s3_bucket(bucket_name):
    try:
        # Create the S3 client
        s3_client = boto3.client('s3')

        # Create the bucket
        response = s3_client.create_bucket(
            Bucket=bucket_name,
             CreateBucketConfiguration={
        'LocationConstraint': 'ap-south-1',
    },
        )
        print(f"Bucket {bucket_name} created successfully.")
    except Exception as e:
       print(f"Error creating bucket {bucket_name}: {e}")



source_bucket_name = 'src-bkt-04-28'
destination_bucket_name = 'dst-bkt-04-28'

# Create both buckets
create_s3_bucket(source_bucket_name)
create_s3_bucket(destination_bucket_name)
