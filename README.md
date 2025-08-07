# Meeting Transcript Processor

A powerful AI-driven meeting transcript processing system that uses Amazon Bedrock Nova Lite and FastMCP to automatically analyze meeting transcripts, extract key information, and generate structured summaries with actionable tasks.

## Features

- 📝 **Automated Transcript Analysis**: Process meeting transcripts from text input or file upload
- 🎯 **Smart Task Extraction**: Automatically identify and extract action items with assignees, due dates, and priorities
- 📋 **Meeting Summarization**: Generate concise summaries of meeting discussions
- 👥 **Participant Detection**: Identify and list meeting participants
- 🔍 **Key Decision Tracking**: Extract important decisions made during meetings
- 💬 **Topic Identification**: Analyze and categorize discussion topics
- 📄 **PDF Report Generation**: Generate professional PDF reports with charts and formatted layouts
- 📤 **Multiple Export Formats**: Export results in JSON, Markdown, plain text, or PDF formats
- 🌐 **Minimalistic Web Interface**: Clean, modern, and responsive UI for easy interaction
- 📊 **Task Priority Visualization**: Automatic generation of priority distribution charts in PDF reports

## Architecture

This project is built on the FastMCPandAI_Solution foundation and includes:

- **Flask Web Application** (`app.py`): Main web server handling HTTP requests
- **Meeting Processor** (`meeting_processor.py`): Core AI processing logic using Amazon Bedrock
- **MCP Server** (`mcp_server.py`): FastMCP server providing specialized meeting analysis tools
- **Web Interface** (`templates/index.html`): Modern responsive UI for transcript processing

## Technology Stack

- **Backend**: Python, Flask, FastMCP
- **AI/ML**: Amazon Bedrock Nova Lite
- **Frontend**: HTML5, CSS3, JavaScript
- **File Processing**: Support for TXT, MD, DOC, DOCX files
- **Export Formats**: JSON, Markdown, Plain Text

## Installation

1. **Clone the project**:
   ```bash
   cd /path/to/mcp/directory
   cp -r FastMCPandAI_Solution MeetingTranscriptProcessor
   cd MeetingTranscriptProcessor
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure AWS credentials**:
   - Ensure your AWS credentials are configured with access to Amazon Bedrock
   - The default profile is used, but you can modify the profile in the code if needed

## Usage

### Starting the Application

1. **Start both servers**:
   ```bash
   # On macOS/Linux:
   ./start_both_servers.sh
   
   # On Windows:
   start_both_servers.bat
   ```

2. **Access the web interface**:
   Open your browser and navigate to `http://localhost:5000`

### Processing Transcripts

#### Method 1: File Upload
1. Click on the "Upload File" section
2. Select a transcript file (TXT, MD, DOC, DOCX)
3. Click "Upload & Process"

#### Method 2: Text Input
1. Paste your meeting transcript in the text area
2. Click "Process Transcript"

### Understanding Results

The system will analyze your transcript and provide:

- **Summary**: A concise overview of the meeting
- **Participants**: List of identified meeting attendees
- **Action Items & Tasks**: Extracted tasks with:
  - Task description
  - Assigned person (if mentioned)
  - Due date (if specified)
  - Priority level
  - Status
- **Key Decisions**: Important decisions made during the meeting
- **Topics Discussed**: Main themes and subjects covered

### Exporting Results

Use the export buttons to download results in your preferred format:
- **JSON**: Structured data format for further processing
- **Markdown**: Formatted document for documentation
- **Text**: Simple text format for sharing
- **PDF**: Professional report format with charts and layouts

## Example Transcript Format

For best results, format your transcripts like this:

```
John Smith: Good morning everyone, let's start today's project review meeting.

Sarah Johnson: Thanks John. I wanted to discuss the progress on the marketing campaign. We need to finalize the budget by Friday.

John Smith: Great point Sarah. Can you take the lead on that? Also, we decided to move forward with the new design proposal.

Mike Davis: I'll handle the technical implementation. The deadline is next Tuesday.

Sarah Johnson: Perfect. I'll coordinate with the design team this week.
```

## MCP Tools Available

The MCP server provides several specialized tools:

- `analyze_meeting_transcript`: Complete transcript analysis
- `extract_action_items`: Extract tasks and action items
- `get_meeting_summary`: Generate meeting summary
- `get_participant_list`: Extract participant names
- `format_meeting_output`: Format results in different formats
- `get_current_time`: Get current timestamp
- `calculate_meeting_duration`: Calculate meeting duration

## Configuration

### AWS Profile
To change the AWS profile, modify the profile name in both `meeting_processor.py` and `mcp_server.py`:

```python
aws_profile = "your-profile-name"
```

### Model Configuration
To use a different Bedrock model, update the model ID:

```python
self.model_id = "your-preferred-model-id"
```

## Troubleshooting

### Common Issues

1. **AWS Credentials Error**:
   - Ensure AWS CLI is configured: `aws configure`
   - Check that your profile has Bedrock permissions

2. **Port Already in Use**:
   - Check if ports 5000 or 8001 are in use
   - Modify port numbers in the configuration if needed

3. **MCP Server Connection Failed**:
   - Ensure the MCP server is running on port 8001
   - Check firewall settings

### Error Messages

- **"No transcript provided"**: Ensure you've entered text or selected a file
- **"Failed to process transcript"**: Check AWS credentials and network connection
- **"MCP Server connection failed"**: Restart the MCP server component

## Development

### Project Structure
```
MeetingTranscriptProcessor/
├── app.py                 # Main Flask application
├── meeting_processor.py   # AI processing logic
├── mcp_server.py         # FastMCP server
├── requirements.txt      # Python dependencies
├── start_both_servers.sh # Startup script (macOS/Linux)
├── start_both_servers.bat# Startup script (Windows)
├── templates/
│   └── index.html        # Web interface
├── static/
│   └── style.css         # Styling
└── README.md            # This file
```

### Adding New Features

1. **New MCP Tools**: Add functions decorated with `@mcp.tool()` in `mcp_server.py`
2. **Enhanced Processing**: Modify `meeting_processor.py` for new AI capabilities
3. **UI Improvements**: Update `templates/index.html` and `static/style.css`

## License

This project is based on the FastMCPandAI_Solution and follows the same licensing terms.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the original FastMCPandAI_Solution documentation
3. Ensure all dependencies are properly installed
4. Verify AWS Bedrock access and credentials
