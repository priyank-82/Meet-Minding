#!/bin/bash

echo "🚀 Starting Meeting Transcript Processor..."
echo "================================================"

# Function to cleanup on script exit
cleanup() {
    echo "🛑 Shutting down servers..."
    if [ ! -z "$MCP_PID" ]; then
        kill $MCP_PID 2>/dev/null
        echo "   MCP Server stopped"
    fi
    if [ ! -z "$FLASK_PID" ]; then
        kill $FLASK_PID 2>/dev/null
        echo "   Flask App stopped"
    fi
    echo "✅ Cleanup complete"
    exit 0
}

# Set up trap to cleanup on script exit
trap cleanup SIGINT SIGTERM EXIT

# Start MCP Server in background
echo "🔧 Starting MCP Server..."
python mcp_server.py &
MCP_PID=$!
echo "   MCP Server PID: $MCP_PID"

# Wait a moment for MCP server to start
sleep 3

# Start Flask App in background  
echo "🌐 Starting Flask Application..."
python app.py &
FLASK_PID=$!
echo "   Flask App PID: $FLASK_PID"

echo ""
echo "🎉 Both servers are running!"
echo "📊 MCP Server: http://localhost:8001"
echo "🌐 Web Interface: http://localhost:5001"
echo ""
echo "📝 Ready to process meeting transcripts!"
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for either process to finish
wait $MCP_PID $FLASK_PID
