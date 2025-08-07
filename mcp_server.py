import asyncio
from datetime import datetime
import json
from typing import Dict, Any, Optional, List
from fastmcp import FastMCP
import sys
import io
import re

# Ensure proper Unicode handling for Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Create FastMCP server
mcp = FastMCP("Meeting Transcript Processor with AI Analysis")

class MeetingAnalyzer:
    def __init__(self):
        self.processed_transcripts = {}
        self.analysis_cache = {}
        
    def extract_participants(self, transcript: str) -> List[str]:
        """Extract participant names from transcript"""
        participants = set()
        
        # Look for common patterns like "Speaker:", "John:", "[John]", etc.
        speaker_patterns = [
            r'^([A-Z][a-zA-Z\s]+):\s',  # "John Doe: "
            r'\[([A-Z][a-zA-Z\s]+)\]',  # "[John Doe]"
            r'Speaker\s+([A-Z][a-zA-Z\s]+)',  # "Speaker John Doe"
        ]
        
        for pattern in speaker_patterns:
            matches = re.findall(pattern, transcript, re.MULTILINE)
            for match in matches:
                name = match.strip()
                if len(name) > 1 and name not in ['Speaker', 'Unknown']:
                    participants.add(name)
        
        return list(participants)
    
    def extract_tasks_pattern_based(self, transcript: str) -> List[Dict[str, str]]:
        """Extract tasks using pattern matching"""
        tasks = []
        
        # Task indication patterns
        task_patterns = [
            r'(?:action item|task|todo|assignment|responsible for|will do|needs to|should)[:.\s]+([^.!?]+)',
            r'([A-Z][a-zA-Z\s]+)\s+(?:will|should|needs to|is responsible for|assigned to)\s+([^.!?]+)',
            r'by\s+([A-Z][a-zA-Z\s]+)[:.\s]+([^.!?]+)',
        ]
        
        for pattern in task_patterns:
            matches = re.findall(pattern, transcript, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple) and len(match) == 2:
                    assignee, task_desc = match
                    tasks.append({
                        "task": task_desc.strip(),
                        "assignee": assignee.strip(),
                        "due_date": "Not specified",
                        "priority": "medium",
                        "status": "assigned"
                    })
                else:
                    tasks.append({
                        "task": match.strip() if isinstance(match, str) else str(match),
                        "assignee": "Not specified",
                        "due_date": "Not specified",
                        "priority": "medium",
                        "status": "discussed"
                    })
        
        return tasks[:10]  # Limit to 10 tasks
    
    def extract_decisions(self, transcript: str) -> List[str]:
        """Extract key decisions from transcript"""
        decisions = []
        
        decision_patterns = [
            r'(?:decided|decision|agreed|resolved|concluded)[:.\s]+([^.!?]+)',
            r'we\s+(?:will|shall|agreed to|decided to)\s+([^.!?]+)',
            r'final decision[:.\s]+([^.!?]+)',
        ]
        
        for pattern in decision_patterns:
            matches = re.findall(pattern, transcript, re.IGNORECASE)
            for match in matches:
                decision = match.strip()
                if len(decision) > 10:  # Filter out very short matches
                    decisions.append(decision)
        
        return decisions[:5]  # Limit to 5 decisions

# Initialize the meeting analyzer
meeting_analyzer = MeetingAnalyzer()

@mcp.tool()
def analyze_meeting_transcript(transcript: str) -> Dict[str, Any]:
    """
    Analyze a meeting transcript to extract summary, participants, tasks, and decisions
    
    Args:
        transcript: The meeting transcript text to analyze
        
    Returns:
        Dict containing structured analysis of the meeting
    """
    try:
        # Extract basic information using pattern matching
        participants = meeting_analyzer.extract_participants(transcript)
        tasks = meeting_analyzer.extract_tasks_pattern_based(transcript)
        decisions = meeting_analyzer.extract_decisions(transcript)
        
        # Generate a simple summary (first few sentences or key points)
        sentences = transcript.split('.')[:3]
        summary = '. '.join(sentences).strip() + '.' if sentences else "Meeting transcript provided."
        
        # Extract topics (look for repeated key words)
        words = re.findall(r'\b[A-Z][a-zA-Z]{3,}\b', transcript)
        word_freq = {}
        for word in words:
            if word not in ['Speaker', 'The', 'This', 'That', 'With', 'From']:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        topics = [word for word, freq in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]]
        
        result = {
            "summary": summary,
            "participants": participants,
            "key_decisions": decisions,
            "tasks": tasks,
            "action_items": [task["task"] for task in tasks],
            "next_meeting": "Not specified",
            "topics_discussed": topics,
            "analysis_timestamp": datetime.now().isoformat(),
            "transcript_length": len(transcript),
            "processing_method": "pattern_based_extraction"
        }
        
        # Cache the result
        transcript_hash = str(hash(transcript))
        meeting_analyzer.analysis_cache[transcript_hash] = result
        
        return result
        
    except Exception as e:
        return {
            "error": f"Failed to analyze transcript: {str(e)}",
            "summary": "",
            "participants": [],
            "key_decisions": [],
            "tasks": [],
            "action_items": [],
            "next_meeting": "Not specified",
            "topics_discussed": []
        }

@mcp.tool()
def extract_action_items(transcript: str, assignee_filter: Optional[str] = None) -> List[Dict[str, str]]:
    """
    Extract action items and tasks from a meeting transcript
    
    Args:
        transcript: The meeting transcript text
        assignee_filter: Optional filter to only return tasks for a specific person
        
    Returns:
        List of action items with details
    """
    try:
        tasks = meeting_analyzer.extract_tasks_pattern_based(transcript)
        
        if assignee_filter:
            filtered_tasks = []
            for task in tasks:
                if assignee_filter.lower() in task.get("assignee", "").lower():
                    filtered_tasks.append(task)
            tasks = filtered_tasks
        
        return tasks
        
    except Exception as e:
        return [{"error": f"Failed to extract action items: {str(e)}"}]

@mcp.tool() 
def get_meeting_summary(transcript: str, max_length: int = 200) -> str:
    """
    Generate a concise summary of the meeting transcript
    
    Args:
        transcript: The meeting transcript text
        max_length: Maximum length of the summary in characters
        
    Returns:
        A concise summary of the meeting
    """
    try:
        # Simple extractive summarization
        sentences = transcript.split('.')
        important_sentences = []
        
        # Look for sentences with key words
        key_words = ['decided', 'agreed', 'action', 'task', 'deadline', 'next', 'meeting', 'project']
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:  # Skip very short sentences
                for key_word in key_words:
                    if key_word.lower() in sentence.lower():
                        important_sentences.append(sentence)
                        break
        
        # If no key sentences found, take the first few sentences
        if not important_sentences:
            important_sentences = [s.strip() for s in sentences[:3] if len(s.strip()) > 20]
        
        summary = '. '.join(important_sentences)
        
        # Truncate if too long
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."
        
        return summary
        
    except Exception as e:
        return f"Error generating summary: {str(e)}"

@mcp.tool()
def get_participant_list(transcript: str) -> List[str]:
    """
    Extract list of meeting participants from transcript
    
    Args:
        transcript: The meeting transcript text
        
    Returns:
        List of participant names
    """
    try:
        return meeting_analyzer.extract_participants(transcript)
    except Exception as e:
        return [f"Error extracting participants: {str(e)}"]

@mcp.tool()
def format_meeting_output(analysis_result: Dict[str, Any], format_type: str = "json") -> str:
    """
    Format the meeting analysis result in different output formats
    
    Args:
        analysis_result: The analysis result dictionary
        format_type: Output format ("json", "markdown", "text")
        
    Returns:
        Formatted output string
    """
    try:
        if format_type.lower() == "markdown":
            output = f"""# Meeting Analysis Report

## Summary
{analysis_result.get('summary', 'No summary available')}

## Participants
{', '.join(analysis_result.get('participants', []))}

## Key Decisions
"""
            for decision in analysis_result.get('key_decisions', []):
                output += f"- {decision}\n"
            
            output += "\n## Action Items\n"
            for task in analysis_result.get('tasks', []):
                output += f"- **Task**: {task.get('task', '')}\n"
                output += f"  - **Assignee**: {task.get('assignee', 'Not specified')}\n"
                output += f"  - **Due Date**: {task.get('due_date', 'Not specified')}\n"
                output += f"  - **Priority**: {task.get('priority', 'medium')}\n\n"
            
            output += f"\n## Topics Discussed\n"
            for topic in analysis_result.get('topics_discussed', []):
                output += f"- {topic}\n"
            
            return output
            
        elif format_type.lower() == "text":
            output = f"MEETING ANALYSIS REPORT\n{'='*25}\n\n"
            output += f"Summary: {analysis_result.get('summary', 'No summary available')}\n\n"
            output += f"Participants: {', '.join(analysis_result.get('participants', []))}\n\n"
            
            if analysis_result.get('key_decisions'):
                output += "Key Decisions:\n"
                for i, decision in enumerate(analysis_result.get('key_decisions', []), 1):
                    output += f"{i}. {decision}\n"
                output += "\n"
            
            if analysis_result.get('tasks'):
                output += "Action Items:\n"
                for i, task in enumerate(analysis_result.get('tasks', []), 1):
                    output += f"{i}. {task.get('task', '')} "
                    output += f"(Assigned to: {task.get('assignee', 'Not specified')})\n"
                output += "\n"
            
            return output
            
        else:  # Default to JSON
            return json.dumps(analysis_result, indent=2)
            
    except Exception as e:
        return f"Error formatting output: {str(e)}"

# Time utility tools
@mcp.tool()
def get_current_time() -> str:
    """Get the current date and time"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@mcp.tool()
def calculate_meeting_duration(start_time: str, end_time: str) -> str:
    """
    Calculate meeting duration from start and end times
    
    Args:
        start_time: Start time in format "HH:MM" or "YYYY-MM-DD HH:MM"
        end_time: End time in format "HH:MM" or "YYYY-MM-DD HH:MM"
        
    Returns:
        Duration string
    """
    try:
        # Parse times - handle different formats
        if len(start_time) == 5:  # "HH:MM"
            start = datetime.strptime(start_time, "%H:%M")
            end = datetime.strptime(end_time, "%H:%M")
        else:  # Full datetime
            start = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
            end = datetime.strptime(end_time, "%Y-%m-%d %H:%M")
        
        duration = end - start
        
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours} hours and {minutes} minutes"
        else:
            return f"{minutes} minutes"
            
    except Exception as e:
        return f"Error calculating duration: {str(e)}"

# Run the server
if __name__ == "__main__":
    print("🚀 Starting Meeting Transcript Processor MCP Server...")
    print("🔧 Available tools:")
    print("   - analyze_meeting_transcript: Full transcript analysis")
    print("   - extract_action_items: Extract tasks and action items")
    print("   - get_meeting_summary: Generate meeting summary")
    print("   - get_participant_list: Extract participant names")
    print("   - format_meeting_output: Format results in different formats")
    print("   - get_current_time: Get current timestamp")
    print("   - calculate_meeting_duration: Calculate meeting duration")
    print("📊 MCP Server ready for stdio communication")
    
    try:
        asyncio.run(mcp.run_stdio_async())
    except Exception as e:
        print(f"❌ Error starting MCP server: {e}")
        sys.exit(1)
