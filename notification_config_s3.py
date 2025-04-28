import boto3

s3_client = boto3.client('s3')

response = s3_client.put_bucket_notification_configuration(
    Bucket='src-bkt-04-28',
    NotificationConfiguration={
        'LambdaFunctionConfigurations': [
            {
                'LambdaFunctionArn': 'arn:aws:lambda:ap-south-1:194325853642:function:copy-object-from-bucket',
                'Events': [
                    's3:ObjectCreated:*'
                ],
            },
        ],
    }
)

print("Notification configuration set:", response)
