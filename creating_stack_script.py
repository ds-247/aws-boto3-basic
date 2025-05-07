import boto3
import zipfile
import os

S3_BUCKET = 's3-copy-lambda-code-bucket'
S3_KEY = 'lambda/lambda_logic.zip'
REGION = 'ap-south-1'
ZIP_FILE = 'lambda_logic.zip'
LAMBDA_HANDLER_FILE = 'lambda_logic.py'
LAMBDA_HANDLER = 'lambda_logic.lambda_handler'
STACK_NAME = 's3-bucket-copy-automation'
TEMPLATE_FILE = 'automation.yaml'

params = [
    {'ParameterKey': 'SrcBucketName', 'ParameterValue': 'src-bkt-04-28'},
    {'ParameterKey': 'DestBucketName', 'ParameterValue': 'dst-bkt-04-28'},
    {'ParameterKey': 'LambdaRuntimeVersion', 'ParameterValue': 'python3.12'},
    {'ParameterKey': 'LambdaCodeBucket', 'ParameterValue': S3_BUCKET},
    {'ParameterKey': 'LambdaCodeBucketObjectKey', 'ParameterValue': S3_KEY},
    {'ParameterKey': 'LambdaHandler', 'ParameterValue': LAMBDA_HANDLER},
]


s3 = boto3.client('s3', region_name=REGION)
cf = boto3.client('cloudformation', region_name=REGION)


def create_s3_bucket(bucket_name, region):
    try:
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': region},
        )
        print(f"Bucket {bucket_name} created:")
        return True
    except Exception as e:
        print(f"Error creating bucket {bucket_name}: {e}")
        return False


def zip_lambda_function():
    try:
        with zipfile.ZipFile(ZIP_FILE, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(LAMBDA_HANDLER_FILE)
        print(f"Zipped {LAMBDA_HANDLER_FILE} to {ZIP_FILE}")
        return True
    except Exception as e:
        print(f"Error zipping {LAMBDA_HANDLER_FILE}: {e}")
        return False


def upload_to_s3(bucket_name, zip_name, s3_key):
    try:
        s3.upload_file(zip_name, bucket_name, s3_key)
        print(f"Uploaded {zip_name} to s3://{bucket_name}/{s3_key}")
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return False
    finally:
        if os.path.exists(zip_name):
            os.remove(zip_name)
            print(f"Deleted local zip file: {zip_name}")
            return True


def deploy_stack(stack_name, template_body, parameters):
    try:
        cf.describe_stacks(StackName=stack_name)
        print(f"Stack '{stack_name}' exists. Updating...")
        cf.update_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Parameters=parameters,
            Capabilities=['CAPABILITY_NAMED_IAM']
        )
        waiter = cf.get_waiter('stack_update_complete')
    except cf.exceptions.ClientError as e:
        if "does not exist" in str(e):
            print(f"Creating new stack '{stack_name}'...")
            cf.create_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Parameters=parameters,
                Capabilities=['CAPABILITY_NAMED_IAM']
            )
            waiter = cf.get_waiter('stack_create_complete')
        else:
            raise

    print("Waiting for stack operation to complete...")
    waiter.wait(StackName=stack_name)
    print(f"Stack '{stack_name}' deployed successfully!")


def main():
    if not create_s3_bucket(S3_BUCKET, REGION):
        return
    
    if not zip_lambda_function():
        return 
    
    if not upload_to_s3(S3_BUCKET, ZIP_FILE, S3_KEY):
        return

    with open(TEMPLATE_FILE, 'r') as f:
        template_body = f.read()

    deploy_stack(STACK_NAME, template_body, params)

if __name__ == "__main__":
   main()