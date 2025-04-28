# create venv
# pip install robo3
# install cli for aws 
# aws configure 

import boto3

client = boto3.client('s3')

response = client.delete_bucket(
    Bucket='dipsbhaikipehlibucket',
)

print(response)