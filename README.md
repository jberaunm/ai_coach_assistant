# CS550 - AI Running Coach Assistant

An intelligent multi-agent system that provides personalized running training plans, session analysis, and coaching insights using AI agents, RAG knowledge base, and integration with Strava and Google Calendar.

## 🏃‍♂️ Features

- **Multi-Agent Architecture**: Orchestrator, Planner, Scheduler, Analyser, Strava, and RAG agents
- **Personalized Training Plans**: AI-generated training plans based on user goals and preferences
- **Session Analysis**: Detailed analysis of running sessions with coach feedback
- **Strava Integration**: Automatic activity tracking and completion detection
- **Google Calendar Integration**: Smart scheduling and rescheduling of training sessions
- **RAG Knowledge Base**: Research-based insights from uploaded training documents
- **Dynamic Coach Feedback**: Adaptive analysis based on available research knowledge

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- Google Calendar API credentials
- Strava API credentials

### 1. Environment Setup

```bash
# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 2. API Setup

#### Google Calendar Setup
```bash
# Run the Google Calendar setup script
python setup_calendar_auth.py
```
Follow the prompts to:
- Download credentials.json
- Complete OAuth flow
- Grant necessary permissions

#### Strava Setup
```bash
# Run the Strava setup script
python setup_strava_auth.py
```
Follow the prompts to:
- Enter your Strava Client ID and Client Secret
- Complete OAuth flow
- Grant necessary permissions

### 4. Start the Application

#### Backend (Terminal 1)
```bash
cd app
uvicorn main:app --reload
```
The backend API will be available at `http://localhost:8000`

#### Frontend (Terminal 2)
```bash
cd frontend
npm install
npm run dev
```
The frontend will be available at `http://localhost:3000`

## 📁 Project Structure

```
ai_coach_assistant/
├── app/                          # Backend Python application
│   ├── ai_coach_agent/          # AI agents and workflows
│   │   ├── agent.py             # Main agent definitions
│   │   └── tools/               # Agent tools and utilities
│   ├── db/                      # Database services
│   ├── data/                    # ChromaDB data storage
│   └── main.py                  # FastAPI application
├── frontend/                    # Next.js React frontend
│   ├── src/app/                 # React components
│   └── public/                  # Static assets
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🤖 Agent Architecture

### Orchestrator Agent
- Coordinates all other agents
- Manages workflow execution
- Handles user requests and routing

### Planner Agent
- Creates personalized training plans
- Uses RAG knowledge for evidence-based planning
- Integrates user preferences and goals

### Scheduler Agent
- Manages Google Calendar integration
- Handles session scheduling and rescheduling
- Provides weather-aware scheduling

### Analyser Agent
- Analyzes running sessions
- Generates dynamic coach feedback
- Uses RAG knowledge for research-based insights

### Strava Agent
- Integrates with Strava API
- Tracks activity completion
- Retrieves detailed activity data

### RAG Agent
- Processes research documents
- Creates knowledge chunks
- Enhances agent capabilities

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the `app/` directory:

```env
# API Keys
STRAVA_CLIENT_ID=your_strava_client_id
STRAVA_CLIENT_SECRET=your_strava_client_secret
GOOGLE_CALENDAR_CREDENTIALS_PATH=credentials.json

# AI Model Configuration
MISTRAL_API_KEY=your_mistral_api_key
GEMINI_API_KEY=your_gemini_api_key

# Database
CHROMA_DB_PATH=./data/chroma
```

### API Credentials Setup

1. **Google Calendar API**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Enable Calendar API
   - Create credentials (OAuth 2.0)
   - Download credentials.json

2. **Strava API**:
   - Go to [Strava API](https://www.strava.com/settings/api)
   - Create a new application
   - Get Client ID and Client Secret

## 📊 Usage

### Creating Training Plans
1. Navigate to the frontend at `http://localhost:3000`
2. Use the "Create Training Plan" feature
3. Provide your running goals, preferences, and target race date
4. The system will generate a personalized training plan

### Session Analysis
1. After completing a run, go to the "Insights" section
2. Provide your RPE (Rate of Perceived Effort) and feedback
3. The system will analyze your session and provide coach feedback

### Document Upload
1. Upload research documents (PDFs) to enhance the knowledge base
2. The RAG agent will process and create knowledge chunks
3. This knowledge will enhance future training plans and analysis

## 🛠️ Development

### Adding New Agents
1. Define the agent in `app/ai_coach_agent/agent.py`
2. Add necessary tools in `app/ai_coach_agent/tools/`
3. Update the orchestrator to include the new agent

### Extending RAG Knowledge
1. Add new documents to the `app/uploads/` directory
2. Use the RAG agent to process documents
3. Knowledge will be automatically integrated into agent workflows

## 🐛 Troubleshooting

### Common Issues

1. **API Authentication Errors**:
   - Re-run the setup scripts
   - Check API credentials in `.env` file
   - Ensure OAuth tokens are valid

2. **Database Issues**:
   - Check ChromaDB data directory permissions
   - Re-initialize the database if needed

3. **Frontend Build Issues**:
   - Clear node_modules and reinstall: `rm -rf node_modules && npm install`
   - Check Node.js version compatibility

### Logs
- Backend logs: Check terminal running `uvicorn main:app --reload`
- Frontend logs: Check terminal running `npm run dev`
- Agent logs: Available in the application interface

## 📝 License

This project is part of CS550 coursework and is for educational purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review agent logs for error details
3. Ensure all API credentials are properly configured
