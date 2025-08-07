from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from meeting_processor import MeetingTranscriptProcessor
from team_storage import TeamSummaryManager
import atexit

app = Flask(__name__)
CORS(app)

# Initialize the meeting processor and team storage
processor = MeetingTranscriptProcessor()
team_manager = TeamSummaryManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_transcript', methods=['POST'])
def process_transcript():
    try:
        data = request.get_json()
        transcript = data.get('transcript', '')
        team_id = data.get('team_id', '')
        
        if not transcript:
            return jsonify({'error': 'No transcript provided'}), 400
        
        # Get previous meeting context if team_id is provided
        context = ""
        if team_id:
            context = team_manager.generate_context_prompt(team_id)
        
        # Process the meeting transcript with context
        result = processor.process_meeting_transcript(transcript, context)
        
        # Save the summary if team_id is provided
        if team_id and result:
            team_manager.save_meeting_summary(team_id, result)
        
        return jsonify({
            'result': result,
            'status': 'success',
            'team_id': team_id or None
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload_transcript', methods=['POST'])
def upload_transcript():
    """Handle file upload for transcript"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get team_id from form data
        team_id = request.form.get('team_id', '')
        
        # Read the transcript content
        transcript = file.read().decode('utf-8')
        
        # Get previous meeting context if team_id is provided
        context = ""
        if team_id:
            context = team_manager.generate_context_prompt(team_id)
        
        # Process the meeting transcript with context
        result = processor.process_meeting_transcript(transcript, context)
        
        # Save the summary if team_id is provided
        if team_id and result:
            team_manager.save_meeting_summary(team_id, result)
        
        return jsonify({
            'result': result,
            'status': 'success',
            'team_id': team_id or None
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/teams', methods=['GET'])
def get_teams():
    """Get list of teams with stored summaries"""
    try:
        teams = team_manager.get_team_list()
        return jsonify({
            'teams': teams,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/team/<team_id>/history', methods=['GET'])
def get_team_history(team_id):
    """Get meeting history for a specific team"""
    try:
        limit = request.args.get('limit', 5, type=int)
        history = team_manager.get_previous_meetings_for_context(team_id, limit)
        return jsonify({
            'team_id': team_id,
            'history': history,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

# Cleanup handler
@atexit.register
def cleanup():
    try:
        processor.cleanup()
    except:
        pass

if __name__ == '__main__':
    print("🚀 Starting Meeting Transcript Processor Web Interface...")
    print("📝 Access the application at: http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)