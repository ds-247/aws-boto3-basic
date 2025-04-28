import boto3
import zipfile

lambda_client = boto3.client('lambda', region_name='ap-south-1') 

def zip_lambda_function():
    with zipfile.ZipFile('lambda_logic.zip', 'w') as zipf:
        zipf.write('lambda_logic.py')

# Deploy the lambda function
def create_lambda_function():
    zip_lambda_function()

    with open('lambda_logic.zip', 'rb') as f:
        zipped_code = f.read()

    try:
        response = lambda_client.create_function(
            FunctionName='copy-object-from-bucket',
            Runtime='python3.9',
            Handler='lambda_logic.lambda_handler',
            Role='arn:aws:iam::194325853642:role/lambda-s3-access-role', 
            Code=dict(ZipFile=zipped_code)
        )
        print("Lambda function created successfully!")
    except Exception as e:
        print(f"Error creating Lambda function: {e}")


create_lambda_function()
