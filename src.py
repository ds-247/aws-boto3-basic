# create venv
# pip install robo3
# install cli for aws 
# aws configure 

import boto3

client = boto3.client('s3')

response = client.create_bucket(
    Bucket='dipsbhaikipehlibucket',
     CreateBucketConfiguration={
        'LocationConstraint': 'ap-south-1',
    },
)

print(response)


print("End of script")