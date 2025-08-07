#!/usr/bin/env python3
"""
Test script to read a JSON file from team_summaries and upload it to S3
"""

import json
import os
import sys
from s3_save import save_to_s3

def test_s3_upload():
    """Test uploading a team summary JSON file to S3"""
    
    # Path to test JSON file
    test_file_path = "team_summaries/demo-team/demo-team_20250806_113622.json"
    
    if not os.path.exists(test_file_path):
        print(f"Error: Test file not found at {test_file_path}")
        return False
    
    try:
        # Read the JSON file
        with open(test_file_path, 'r', encoding='utf-8') as f:
            meeting_data = json.load(f)
        
        print(f"Loaded meeting data from: {test_file_path}")
        print(f"Team ID: {meeting_data.get('team_id', 'Unknown')}")
        print(f"Date: {meeting_data.get('date', 'Unknown')}")
        print(f"Summary: {meeting_data.get('summary', 'No summary')}")
        print(f"Participants: {meeting_data.get('participants', [])}")
        print(f"Tasks: {len(meeting_data.get('tasks', []))} task(s)")
        print("\n" + "="*50 + "\n")
        
        # Extract team_id for the S3 save function
        team_id = meeting_data.get('team_id', 'unknown-team')
        
        print(f"Uploading to S3 for team: {team_id}")
        
        # Call the S3 save function
        result = save_to_s3(meeting_data, team_id)
        
        if result and 'error' in result:
            print(f"S3 upload failed: {result['error']}")
            return False
        else:
            print("S3 upload completed successfully!")
            return True
            
    except json.JSONDecodeError as e:
        print(f"Error reading JSON file: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def main():
    """Main function to run the test"""
    print("Testing S3 upload functionality...")
    print("="*50)
    
    success = test_s3_upload()
    
    if success:
        print("\n✅ Test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
