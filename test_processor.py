#!/usr/bin/env python3
"""
Test script for Meeting Transcript Processor
"""

import json
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from meeting_processor import MeetingTranscriptProcessor

def test_processor():
    """Test the meeting processor with sample transcript"""
    
    # Sample meeting transcript
    sample_transcript = """
John Smith: Good morning everyone, let's start today's project review meeting.

Sarah Johnson: Thanks John. I wanted to discuss the progress on the marketing campaign. We need to finalize the budget by Friday.

John Smith: Great point Sarah. Can you take the lead on that? Also, we decided to move forward with the new design proposal.

Mike Davis: I'll handle the technical implementation. The deadline is next Tuesday.

Sarah Johnson: Perfect. I'll coordinate with the design team this week.
"""

    print("🧪 Testing Meeting Transcript Processor...")
    print("=" * 50)
    
    try:
        # Initialize processor
        processor = MeetingTranscriptProcessor()
        
        # Process the sample transcript
        print("📝 Processing sample transcript...")
        result = processor.process_meeting_transcript(sample_transcript)
        
        # Display results
        print("\n✅ Processing complete!")
        print("\n📋 RESULTS:")
        print("-" * 30)
        
        print(f"Summary: {result.get('summary', 'N/A')}")
        print(f"Participants: {', '.join(result.get('participants', []))}")
        print(f"Number of tasks: {len(result.get('tasks', []))}")
        print(f"Key decisions: {len(result.get('key_decisions', []))}")
        
        if result.get('tasks'):
            print("\n📋 TASKS:")
            for i, task in enumerate(result['tasks'], 1):
                print(f"  {i}. {task.get('task', 'N/A')} (Assignee: {task.get('assignee', 'N/A')})")
        
        if result.get('key_decisions'):
            print(f"\n🎯 DECISIONS:")
            for i, decision in enumerate(result['key_decisions'], 1):
                print(f"  {i}. {decision}")
        
        # Save detailed results to file
        with open('test_results.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: test_results.json")
        
        # Cleanup
        processor.cleanup()
        
        print("\n🎉 Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_processor()
    sys.exit(0 if success else 1)
