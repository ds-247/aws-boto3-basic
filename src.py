# create venv
# pip install robo3
# install cli for aws 
# aws configure 


import boto3

s3 = boto3.resource('s3')

# Print out bucket names
for bucket in s3.buckets.all():
    print(bucket.name)

print("End of script")