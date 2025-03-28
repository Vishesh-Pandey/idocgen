import json
import csv
import boto3
import os
from datetime import datetime

# Initialize S3 client
s3_client = boto3.client("s3")

# Replace with your actual S3 bucket name
S3_BUCKET_NAME = "idocgen-files"

def handler(event, context):
    try:
        # Extract text data from request body
        body = json.loads(event["body"])
        text_data = body.get("data", "")

        if not text_data:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No data provided in request body."})
            }

        # Generate a unique file name
        file_name = f"output_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        local_file_path = f"/tmp/{file_name}"

        # Write text data to a CSV file
        with open(local_file_path, "w", newline="") as file:
            writer = csv.writer(file)
            for line in text_data.split("\n"):  # Splitting text by lines
                writer.writerow(line.split(","))  # Splitting each line by comma

        # Upload file to S3
        s3_client.upload_file(local_file_path, S3_BUCKET_NAME, file_name)

        # Generate S3 file URL
        s3_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{file_name}"

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "CSV file created and uploaded successfully.", "s3_url": s3_url})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
