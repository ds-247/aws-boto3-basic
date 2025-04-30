import boto3
import zipfile
import time
import os


REGION = 'ap-south-1'
SOURCE_BUCKET = 'src-bkt-04-28'
DESTINATION_BUCKET = 'dst-bkt-04-28'
LAMBDA_NAME = 'copy-object-from-bucket'
LAMBDA_ROLE_ARN = 'arn:aws:iam::194325853642:role/lambda-s3-access-role'
LAMBDA_HANDLER_FILE = 'lambda_logic.py'
ZIP_FILE = 'lambda_logic.zip'
LAMBDA_ARN = f'arn:aws:lambda:{REGION}:194325853642:function:{LAMBDA_NAME}'


def create_s3_bucket(bucket_name):
    try:
        s3_client = boto3.client('s3', region_name=REGION)
        response = s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': REGION},
        )
        print(f"Bucket {bucket_name} created:", response)
    except Exception as e:
        print(f"Error creating bucket {bucket_name}: {e}")


def create_buckets():
    create_s3_bucket(SOURCE_BUCKET)
    create_s3_bucket(DESTINATION_BUCKET)


def zip_lambda_function():
    with zipfile.ZipFile(ZIP_FILE, 'w') as zipf:
        zipf.write(LAMBDA_HANDLER_FILE)


def create_lambda_function():
    lambda_client = boto3.client('lambda', region_name=REGION)
    zip_lambda_function()

    with open(ZIP_FILE, 'rb') as f:
        zipped_code = f.read()

    try:
        response = lambda_client.create_function(
            FunctionName=LAMBDA_NAME,
            Runtime='python3.9',
            Handler='lambda_logic.lambda_handler',
            Role=LAMBDA_ROLE_ARN,
            Code=dict(ZipFile=zipped_code),
        )
        print("Lambda function created:", response)
    except Exception as e:
        print(f"Error creating Lambda function: {e}")
    finally:
        if os.path.exists(ZIP_FILE):
            os.remove(ZIP_FILE)


def wait_for_lambda(lambda_name):
    lambda_client = boto3.client('lambda', region_name=REGION)
    for _ in range(10):
        try:
            lambda_client.get_function(FunctionName=lambda_name)
            print("Lambda is ready.")
            return
        except:
            print("Waiting for Lambda to become available...")
            time.sleep(2)
    print("Timeout: Lambda function may not be ready yet.")


def add_lambda_permission():
    lambda_client = boto3.client('lambda', region_name=REGION)
    try:
        response = lambda_client.add_permission(
            FunctionName=LAMBDA_NAME,
            StatementId='S3InvokePermission',
            Action='lambda:InvokeFunction',
            Principal='s3.amazonaws.com',
            SourceArn=f'arn:aws:s3:::{SOURCE_BUCKET}'
        )
        print("Lambda permission added:", response)
    except Exception as e:
        print(f"Error adding Lambda permission: {e}")


def configure_s3_event_notification():
    s3_client = boto3.client('s3', region_name=REGION)
    try:
        response = s3_client.put_bucket_notification_configuration(
            Bucket=SOURCE_BUCKET,
            NotificationConfiguration={
                'LambdaFunctionConfigurations': [
                    {
                        'LambdaFunctionArn': LAMBDA_ARN,
                        'Events': ['s3:ObjectCreated:*']
                    },
                ],
            }
        )
        print("S3 event notification configured:", response)
    except Exception as e:
        print(f"Error configuring S3 notification: {e}")


def main():
    create_buckets()
    create_lambda_function()
    wait_for_lambda(LAMBDA_NAME)
    add_lambda_permission()
    configure_s3_event_notification()


if __name__ == "__main__":
    main()
