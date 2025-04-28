import boto3

lambda_client = boto3.client('lambda')

response = lambda_client.add_permission(
    FunctionName='copy-object-from-bucket',
    StatementId='S3InvokePermission',  
    Action='lambda:InvokeFunction',
    Principal='s3.amazonaws.com',
    SourceArn='arn:aws:s3:::src-bkt-04-28'
)

print("Permission added:", response)
