import requests
import boto3
import json
import os
import logging
from datetime import datetime

s3 = boto3.client('s3')
#S3_BUCKET = os.environ['S3_BUCKET']
S3_BUCKET = "team36-project-tracker"
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def save_to_s3(data, team_id, email=None):
    """Saves the meeting summary to S3 bucket using the same structure as local storage."""
    try:
        # Convert team_id to match local storage format (lowercase, spaces to underscores)
        team_dir = team_id.lower().replace(" ", "_")
        
        # Generate timestamp for filename
        datetime_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{team_dir}_{datetime_str}.json"
        
        # Create S3 key path: team_summaries/{team_dir}/{filename}
        S3_FILE_KEY = f"team_summaries/{team_dir}/{filename}"
        
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=S3_FILE_KEY,
            Body=json.dumps(data, default=str),
            ContentType="application/json"
        )
        logger.info(f"Results successfully saved to S3: {S3_BUCKET}/{S3_FILE_KEY}")

    except boto3.exceptions.Boto3Error as e:
        logger.error(f"Failed to upload to S3: {e}")
        return {"error": f"S3 upload error: {str(e)}"}