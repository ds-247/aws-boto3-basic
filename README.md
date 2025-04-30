# S3-to-Lambda Trigger Setup via CloudFormation

This project sets up two S3 buckets and a Lambda function using AWS CloudFormation. When an object is uploaded to the source bucket, the Lambda function is triggered and copies it to the destination bucket.

---

## 🧰 Prerequisites

- AWS CLI configured with appropriate credentials
- Python 3.9+ installed
- AWS CloudFormation permissions
- IAM role for Lambda with necessary S3 and CloudFormation access

---

## 📦 Project Structure

```
.
├── automation.yaml           # CloudFormation template with custom resource
├── README.md               # You're here
```

---

## ⚙️ Setup Instructions

### 1. Create and activate a virtual environment (optional but recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 2. Install dependencies

Only needed if testing Lambda locally or using `cfnresponse` externally:

```bash
pip install boto3
```

> Note: The `cfnresponse` module is available by default in AWS Lambda. You do **not** need to include it manually unless testing locally.

---

## 🏗️ CloudFormation Template Features

### ✅ Creates:

- A **source S3 bucket** (`src-bkt-04-28`)
- A **destination S3 bucket** (`dst-bkt-04-28`)
- A **Lambda function** triggered on object upload to the source bucket
- A **custom resource Lambda** to attach S3 trigger _after_ the Lambda is created

---

## ⚠️ Problem: S3 and Lambda Circular Dependency

You cannot directly configure an S3 trigger inside the `AWS::S3::Bucket` while referencing a Lambda that is defined later in the same template. This results in a circular dependency error.

### ❌ Problematic Attempt (Invalid)

```yaml
S3Bucket:
  Type: AWS::S3::Bucket
  Properties:
    NotificationConfiguration:
      LambdaConfigurations:
        - Event: s3:ObjectCreated:*
          Function: !GetAtt LambdaFunction.Arn
```

---

## ✅ Solution: Use a Custom Resource

To work around this, we used a custom Lambda (`S3NotificationCustomResourceLambda`) that:

1. Waits until all resources (bucket + Lambda) are created
2. Uses `boto3.put_bucket_notification_configuration()` to attach the trigger
3. Sends a CloudFormation response back using `cfnresponse` module

### Custom Resource Lambda Logic

```python
s3 = boto3.client('s3')
props = event['ResourceProperties']
s3.put_bucket_notification_configuration(
    Bucket=props['BucketName'],
    NotificationConfiguration={
        'LambdaFunctionConfigurations': [
            {
                'LambdaFunctionArn': props['LambdaArn'],
                'Events': ['s3:ObjectCreated:*']
            }
        ]
    }
)
```

---

## 🚀 Deployment

You can deploy this template via AWS CLI:

```bash
aws cloudformation deploy \
  --template-file template.yaml \
  --stack-name s3-lambda-trigger-stack \
  --capabilities CAPABILITY_NAMED_IAM
```

---

## ✅ Final Flow

1. User uploads an object to **`src-bkt-04-28`**
2. S3 triggers **`LambdaFunction`**
3. Lambda copies object to **`dst-bkt-04-28`**

---

## 📝 IAM Role Requirements

The Lambda execution role (`lambda-s3-access-role`) must include:

- `s3:GetObject`, `s3:PutObject`, `s3:ListBucket`
- `lambda:InvokeFunction` (if testing with other services)
- `logs:*` permissions (optional, for CloudWatch logging)

---

## 📌 Notes

- Bucket names must be globally unique. Modify `src-bkt-04-28` and `dst-bkt-04-28` if deploying again.
- Ensure `LambdaInvokePermission` allows S3 to trigger the Lambda.
- Custom resource execution time should be sufficient (`Timeout: 60` recommended).

---
