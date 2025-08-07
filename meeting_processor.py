import boto3
import json
import subprocess
import asyncio
from typing import List, Dict, Any
import threading
import time
import re
from botocore.config import Config
import sys
import os
import httpx
from fastmcp import Client

class MeetingTranscriptProcessor:
    def __init__(self):
        #################HERE IS THE PROFILE###############
        aws_profile = "default"
        session = boto3.Session(profile_name=aws_profile)
        
        config = Config(
            connect_timeout=3600,
            read_timeout=3600,
            retries={'max_attempts': 1}
        )
        self.bedrock = session.client('bedrock-runtime', config=config)
        self.model_id = "us.amazon.nova-lite-v1:0"
        self.mcp_process = None
        self.mcp_client = None
        self.server_url = "http://127.0.0.1:8001/mcp/"
        
    def start_mcp_server(self):
        """Start the MCP server as a subprocess"""
        try:
            print(f"Starting MCP server with Python: {sys.executable}")
            # Start the MCP server process using same Python executable
            self.mcp_process = subprocess.Popen(
                [sys.executable, 'mcp_server.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.getcwd(),
                env=os.environ.copy()
            )
            print("FastMCP Server started successfully")
            time.sleep(5)  # Give the server time to start
            
            # Test connection
            return self._test_connection()
            
        except Exception as e:
            print(f"Error starting MCP server: {e}")
            return False

    def _test_connection(self):
        """Test the connection to the MCP server"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = httpx.get(f"{self.server_url}capabilities", timeout=10)
                if response.status_code == 200:
                    print("MCP Server connection successful")
                    return True
                else:
                    print(f"MCP Server connection failed with status: {response.status_code}")
            except Exception as e:
                print(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait before retry
        
        print("Failed to connect to MCP server after all retries")
        return False

    def initialize_mcp(self):
        """Initialize the MCP client connection"""
        try:
            self.mcp_client = Client(session_id="session", server_url=self.server_url)
            result = self.mcp_client.initialize()
            if result:
                print("MCP Client initialized successfully")
                return True
            else:
                print("Failed to initialize MCP client")
                return False
        except Exception as e:
            print(f"Error initializing MCP client: {e}")
            return False

    def process_meeting_transcript(self, transcript: str, context: str = "") -> Dict[str, Any]:
        """
        Process a meeting transcript to extract summary and tasks
        Returns a JSON structure with summary and extracted tasks
        """
        try:
            # Ensure MCP server is running
            if not self.mcp_process or self.mcp_process.poll() is not None:
                if not self.start_mcp_server():
                    # Fallback to direct processing without MCP
                    return self._process_transcript_direct(transcript, context)
            
            # Initialize MCP client if not already done
            if not self.mcp_client:
                if not self.initialize_mcp():
                    return self._process_transcript_direct(transcript, context)
            
            # Create the analysis prompt
            analysis_prompt = self._create_analysis_prompt(transcript, context)
            
            # Get AI response for analysis
            ai_response = self._call_bedrock(analysis_prompt)
            
            # Parse the response into structured format
            result = self._parse_ai_response(ai_response)
            
            return result
            
        except Exception as e:
            print(f"Error processing transcript: {e}")
            return {
                "error": f"Failed to process transcript: {str(e)}",
                "summary": "",
                "tasks": [],
                "participants": [],
                "key_decisions": []
            }

    def _process_transcript_direct(self, transcript: str, context: str = "") -> Dict[str, Any]:
        """Fallback method to process transcript without MCP server"""
        try:
            analysis_prompt = self._create_analysis_prompt(transcript, context)
            ai_response = self._call_bedrock(analysis_prompt)
            return self._parse_ai_response(ai_response)
        except Exception as e:
            return {
                "error": f"Failed to process transcript: {str(e)}",
                "summary": "",
                "tasks": [],
                "participants": [],
                "key_decisions": []
            }

    def _create_analysis_prompt(self, transcript: str, context: str = "") -> str:
        """Create a structured prompt for analyzing the meeting transcript"""
        context_section = ""
        if context:
            context_section = f"""
{context}

IMPORTANT: When analyzing the current meeting transcript below, please:
- Reference previous action items and their current status
- Update task statuses based on progress mentioned in the current meeting
- Mark completed tasks as "completed" in the status field
- Note any follow-up tasks that build on previous work
- Ensure continuity in task tracking across meetings

"""
        
        return f"""
{context_section}Please analyze the following meeting transcript and extract the key information in a structured JSON format.

Meeting Transcript:
{transcript}

Please provide your analysis in the following JSON structure:
{{
    "summary": "A concise 2-3 sentence summary of the meeting",
    "participants": ["List of participant names mentioned"],
    "key_decisions": ["List of key decisions made during the meeting"],
    "tasks": [
        {{
            "task": "Description of the task",
            "assignee": "Person assigned (if mentioned)",
            "due_date": "Due date (if mentioned)",
            "priority": "high/medium/low",
            "status": "assigned/pending/discussed/completed/in-progress"
        }}
    ],
    "action_items": ["List of specific action items"],
    "next_meeting": "Next meeting date/time if mentioned",
    "topics_discussed": ["Main topics covered in the meeting"]
}}

Focus on extracting concrete, actionable tasks and clear decisions. If information is not explicitly mentioned, use "Not specified" or leave empty arrays as appropriate.
{f"Remember to track progress on previously assigned tasks and update their status based on the current meeting discussion." if context else ""}
"""

    def _call_bedrock(self, prompt: str) -> str:
        """Call Amazon Bedrock to process the prompt"""
        try:
            request_body = {
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": prompt}]
                    }
                ],
                "inferenceConfig": {
                    "temperature": 0.1,
                    "topP": 0.9,
                    "maxTokens": 4000
                }
            }
            
            response = self.bedrock.converse(
                modelId=self.model_id,
                messages=request_body["messages"],
                inferenceConfig=request_body["inferenceConfig"]
            )
            
            # Extract the response text
            if 'output' in response and 'message' in response['output']:
                content = response['output']['message']['content']
                if content and len(content) > 0:
                    return content[0]['text']
            
            return "Error: No response from Bedrock"
            
        except Exception as e:
            print(f"Error calling Bedrock: {e}")
            return f"Error calling Bedrock: {str(e)}"

    def _parse_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse the AI response and extract JSON structure"""
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                result = json.loads(json_str)
                
                # Validate and clean the result
                return self._validate_result_structure(result)
            else:
                # If no JSON found, create a basic structure
                return {
                    "summary": ai_response[:500] + "..." if len(ai_response) > 500 else ai_response,
                    "participants": [],
                    "key_decisions": [],
                    "tasks": [],
                    "action_items": [],
                    "next_meeting": "Not specified",
                    "topics_discussed": []
                }
                
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return {
                "error": "Failed to parse AI response as JSON",
                "raw_response": ai_response,
                "summary": "Error processing transcript",
                "participants": [],
                "key_decisions": [],
                "tasks": [],
                "action_items": [],
                "next_meeting": "Not specified",
                "topics_discussed": []
            }

    def _validate_result_structure(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and ensure proper structure of the result"""
        validated = {
            "summary": result.get("summary", ""),
            "participants": result.get("participants", []),
            "key_decisions": result.get("key_decisions", []),
            "tasks": result.get("tasks", []),
            "action_items": result.get("action_items", []),
            "next_meeting": result.get("next_meeting", "Not specified"),
            "topics_discussed": result.get("topics_discussed", [])
        }
        
        # Validate tasks structure
        if validated["tasks"]:
            validated_tasks = []
            for task in validated["tasks"]:
                if isinstance(task, dict):
                    validated_task = {
                        "task": task.get("task", ""),
                        "assignee": task.get("assignee", "Not specified"),
                        "due_date": task.get("due_date", "Not specified"),
                        "priority": task.get("priority", "medium"),
                        "status": task.get("status", "discussed")
                    }
                    validated_tasks.append(validated_task)
                elif isinstance(task, str):
                    validated_tasks.append({
                        "task": task,
                        "assignee": "Not specified",
                        "due_date": "Not specified",
                        "priority": "medium",
                        "status": "discussed"
                    })
            validated["tasks"] = validated_tasks
        
        return validated

    def cleanup(self):
        """Clean up resources"""
        try:
            if self.mcp_process and self.mcp_process.poll() is None:
                print("Terminating MCP server...")
                self.mcp_process.terminate()
                self.mcp_process.wait(timeout=5)
                print("MCP server terminated")
        except Exception as e:
            print(f"Error during cleanup: {e}")

    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()
