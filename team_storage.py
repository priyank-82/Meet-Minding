import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import glob

class TeamSummaryManager:
    """Manages team meeting summaries and provides context from previous meetings"""
    
    def __init__(self, base_dir: str = "team_summaries"):
        self.base_dir = base_dir
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
    
    def _get_team_dir(self, team_id: str) -> str:
        """Get the directory path for a specific team"""
        team_dir = os.path.join(self.base_dir, team_id.lower().replace(" ", "_"))
        if not os.path.exists(team_dir):
            os.makedirs(team_dir)
        return team_dir
    
    def _generate_filename(self, team_id: str, date: datetime = None) -> str:
        """Generate filename for team summary with date and time"""
        if date is None:
            date = datetime.now()
        datetime_str = date.strftime("%Y%m%d_%H%M%S")
        return f"{team_id.lower().replace(' ', '_')}_{datetime_str}.json"
    
    def save_meeting_summary(self, team_id: str, summary_data: Dict[str, Any]) -> str:
        """Save meeting summary for a team with timestamp"""
        team_dir = self._get_team_dir(team_id)
        filename = self._generate_filename(team_id)
        filepath = os.path.join(team_dir, filename)
        
        # No longer remove existing files - allow multiple meetings per day
        # Each meeting gets its own timestamped file
        
        # Add metadata
        summary_data['team_id'] = team_id
        summary_data['date'] = datetime.now().isoformat()
        summary_data['filename'] = filename
        
        # Save new summary
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def get_previous_meetings(self, team_id: str, limit: int = 5, exclude_current: bool = True) -> List[Dict[str, Any]]:
        """Get previous meeting summaries for context"""
        team_dir = self._get_team_dir(team_id)
        
        # Get all summary files for this team
        pattern = os.path.join(team_dir, f"{team_id.lower().replace(' ', '_')}_*.json")
        summary_files = glob.glob(pattern)
        
        # Sort by filename (which includes timestamp) to get chronological order (newest first)
        summary_files.sort(reverse=True)
        
        # Load the most recent summaries
        previous_summaries = []
        current_time = datetime.now()
        current_time_threshold = current_time - timedelta(minutes=1)  # Allow 1-minute buffer for current meeting
        
        for filepath in summary_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    summary = json.load(f)
                    
                    # Parse the meeting date from the summary
                    meeting_date_str = summary.get('date', '')
                    if meeting_date_str and exclude_current:
                        try:
                            meeting_date = datetime.fromisoformat(meeting_date_str.replace('Z', '+00:00'))
                            # Only include meetings that are at least 1 minute old (to exclude current meeting)
                            if meeting_date > current_time_threshold:
                                continue
                        except ValueError:
                            # If we can't parse the date, include it anyway
                            pass
                    
                    previous_summaries.append(summary)
                    
            except (json.JSONDecodeError, OSError):
                continue
                
            if len(previous_summaries) >= limit:
                break
        
        return previous_summaries
    
    def get_previous_meetings_for_context(self, team_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get previous meeting summaries for context - includes all previous meetings without time-based exclusion"""
        return self.get_previous_meetings(team_id, limit, exclude_current=False)
    
    def generate_context_prompt(self, team_id: str) -> str:
        """Generate context prompt from previous meetings"""
        previous_meetings = self.get_previous_meetings_for_context(team_id)
        
        if not previous_meetings:
            return ""
        
        context_parts = [
            f"\n=== PREVIOUS MEETING CONTEXT FOR TEAM: {team_id.upper()} ===\n",
            "The following are summaries from recent team meetings. Use this context to:",
            "- Track progress on previously assigned tasks",
            "- Identify recurring issues or themes",
            "- Note completed vs. pending action items",
            "- Provide continuity in task tracking\n"
        ]
        
        for i, meeting in enumerate(previous_meetings, 1):
            meeting_datetime = meeting.get('date', 'Unknown date')
            # Format datetime to be more readable (YYYY-MM-DD HH:MM)
            try:
                dt = datetime.fromisoformat(meeting_datetime.replace('Z', '+00:00'))
                formatted_datetime = dt.strftime("%Y-%m-%d %H:%M")
            except (ValueError, AttributeError):
                formatted_datetime = meeting_datetime[:16] if meeting_datetime else 'Unknown date'
            
            context_parts.append(f"\n--- Meeting {i} ({formatted_datetime}) ---")
            
            # Add summary
            if 'summary' in meeting:
                context_parts.append(f"Summary: {meeting['summary']}")
            
            # Add key tasks with status tracking
            if 'tasks' in meeting and meeting['tasks']:
                context_parts.append("\nPrevious Action Items:")
                for task in meeting['tasks']:
                    task_desc = task.get('task', 'No description')
                    assignee = task.get('assignee', 'Unassigned')
                    due_date = task.get('due_date', 'No due date')
                    status = task.get('status', 'Unknown')
                    context_parts.append(f"  • {task_desc} (Assigned: {assignee}, Due: {due_date}, Status: {status})")
            
            # Add key decisions
            if 'key_decisions' in meeting and meeting['key_decisions']:
                context_parts.append(f"\nKey Decisions: {'; '.join(meeting['key_decisions'])}")
            
            context_parts.append("")  # Empty line between meetings
        
        context_parts.append("=== END PREVIOUS MEETING CONTEXT ===\n")
        
        return "\n".join(context_parts)
    
    def get_team_list(self) -> List[str]:
        """Get list of all teams with stored summaries"""
        teams = []
        if os.path.exists(self.base_dir):
            for item in os.listdir(self.base_dir):
                item_path = os.path.join(self.base_dir, item)
                if os.path.isdir(item_path):
                    teams.append(item.replace("_", " "))
        return sorted(teams)
