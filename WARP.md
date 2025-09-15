# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Overview

NewsletterGen is an AI-powered newsletter creation suite that uses CrewAI to orchestrate multiple specialized agents for automated newsletter generation. The system takes a topic and optional personal message as input and produces a professional HTML newsletter.

## Architecture

### Multi-Agent System (CrewAI)
The core architecture uses three specialized agents working in sequence:

1. **Research Agent** (`researcher`) - Uses Exa API to search and summarize recent news
2. **Editor Agent** (`editor`) - Refines content, validates sources, and ensures quality 
3. **Designer Agent** (`designer`) - Compiles content into HTML newsletter format

### Key Components
- **Agent Configurations**: `src/newsletter_gen/config/agents.yaml` - Defines roles, goals, and backstories
- **Task Definitions**: `src/newsletter_gen/config/tasks.yaml` - Detailed prompts and expected outputs
- **Research Tools**: `src/newsletter_gen/tools/research.py` - Exa API integration with retry logic
- **Crew Orchestration**: `src/newsletter_gen/crew.py` - Main agent coordination and LLM configuration
- **HTML Template**: `src/newsletter_gen/config/newsletter_template.html` - Newsletter design template

### User Interfaces
- **CLI Interface**: `src/newsletter_gen/main.py` - Command-line newsletter generation
- **Streamlit GUI**: `src/gui/app.py` - Web interface with real-time progress updates
- **Cloud Deployment**: `streamlit_app.py` - Entry point for Streamlit Cloud with fallback error handling

## Development Commands

### Environment Setup
```bash
# Install dependencies (Poetry preferred)
poetry install
# Or use pip
pip install -r requirements.txt
```

### Environment Variables Required
```bash
export GOOGLE_API_KEY="your-gemini-api-key"    # For LLM (Gemini 2.0 Flash-Lite)
export EXA_API_KEY="your-exa-api-key"          # For web research
```

### Running the Application

**Command Line Interface:**
```bash
# Using Poetry
poetry run newsletter_gen

# Direct Python execution
python src/newsletter_gen/main.py
```

**Streamlit Web Interface:**
```bash
# Local development
streamlit run streamlit_app.py

# Or run the GUI module directly
streamlit run src/gui/app.py
```

### Testing
```bash
# Test Gemini API integration
python test_gemini.py
```

### Deployment
The app is configured for Streamlit Cloud deployment with:
- `render.yaml` for Render deployment
- `packages.txt` for system dependencies
- Automatic API key management via Streamlit secrets

## Important Implementation Details

### Rate Limiting & Error Handling
- Exa API calls include built-in retry logic with exponential backoff
- 1-second delays between API calls to respect rate limits
- Tools handle 413/429 errors gracefully with tenacity retry decorator

### Agent Communication
- Agents work sequentially: Research → Edit → Newsletter
- Each task outputs to timestamped log files in `logs/` directory
- Task outputs are automatically passed between agents as context

### LLM Configuration
Currently configured to use Google Gemini 2.0 Flash-Lite (free tier). Alternative LLMs are commented out in `crew.py`:
- Claude 3 Sonnet (Anthropic)
- Llama3-8b and Mixtral (Groq)

### HTML Newsletter Generation
- Uses email-compatible HTML template with responsive design
- Template includes placeholders for personal messages and news items
- Designer agent fills template without modifying structure

## Troubleshooting

### Common Issues
1. **API Key Errors**: Ensure both GOOGLE_API_KEY and EXA_API_KEY are set
2. **Rate Limiting**: Tools include built-in retry logic, but heavy usage may hit limits
3. **Import Errors**: Check that `src` directory is in Python path
4. **Template Issues**: Newsletter template path is hardcoded to `src/newsletter_gen/config/newsletter_template.html`

### Development Notes
- Task descriptions in `tasks.yaml` include specific instructions about underscore escaping for tool parameters
- Agent step callbacks provide detailed logging in Streamlit interface
- Output files are automatically timestamped in `logs/` directory
- The system searches for news from the last 7 days by default

## File Structure Highlights
- `src/newsletter_gen/` - Core CrewAI implementation
- `src/gui/` - Streamlit interface
- `src/newsletter_gen/config/` - Agent/task configurations and HTML template
- `logs/` - Generated output files with timestamps
- `streamlit_app.py` - Cloud deployment entry point with error handling
