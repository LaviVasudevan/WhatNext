# Career Preparation Assistant - Multi-Agent System

AI-powered career preparation assistant deployed on Google Vertex AI Agent Engine. Helps job seekers prepare for their dream roles through parallel analysis of GitHub profiles, job requirements, and professional profiles.

## Features

- **Parallel Tool Execution**: Simultaneously analyzes GitHub profile and job requirements
- **Multi-Agent Architecture**: Specialized agents for different analysis tasks
- **Comprehensive Analysis**:
  - GitHub profile and technical skills assessment
  - Job requirements research (FAANG-focused)
  - Resume/LinkedIn profile analysis
- **Personalized Roadmap**: 8-week preparation plan with actionable steps
- **Production-Ready**: Deployed on Vertex AI with managed sessions and memory

## Architecture

```
Career Prep Orchestrator
├── GitHub Analyzer Agent
│   └── GitHub Profile Tool
├── Job Requirements Agent
│   └── Job Search Trigger Tool
└── Profile Analyzer Agent
    └── Profile Analysis Tool
```

[https://github.com/LaviVasudevan/WhatNext-/blob/b159f2621d0a5ec94e58bd040ab4c6601826488d/97de19cfdf9750ba9b78f8c8a1c166ee.png]

### Workflow

1. The system begins with the user providing their target role, company, application status, and GitHub profile, which triggers two parallel analysis pipelines: the Job Researcher Agent and the GitHub Analyzer Agent.
2. The Job Researcher Agent gathers relevant job descriptions and extracts both must-have and good-to-have skills: technical, behavioral, and domain-specific, building a clear picture of industry expectations.
3. Simultaneously, the GitHub Analyzer Agent studies the user's GitHub work to understand their strengths, technologies used, and project depth.
4. Once the user uploads their resume or LinkedIn profile, the Profile Analyzer agent gets a holistic view of the user's current career position.
5. These outputs are then handed to the Orchestrator Agent, which synthesizes them into a personalized preparation journey containing gap analysis, clear milestones, progress metrics, and curated resources.

Together, the system acts as a clarifying companion that transforms confusion about "what next?" into a structured, actionable career roadmap.

## Project Structure

```
career-prep-agent/
├── README.md                      # Project documentation
├── requirements.txt               # Python dependencies
├── .gitignore                    # Git ignore rules
│
├── src/                          # Source code
│   ├── __init__.py              # Package initialization
│   ├── config.py                # Configuration management
│   ├── tools.py                 # Tool implementations
│   ├── agents.py                # Agent definitions
│   └── deploy.py                # Deployment utilities
│
└── notebooks/                    # Jupyter notebooks
    └── agent-deployment.ipynb   # Full deployment tutorial
```

## Prerequisites

- Python 3.11+
- Google Cloud Project with billing enabled
- Vertex AI API enabled
- Cloud Storage bucket
- Service account credentials

## Installation

```bash
# Clone repository
git clone https://github.com/LaviVasudevan/career-prep-agent.git
cd career-prep-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up authentication
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
```

#### Deployment to Vertex AI

```python
from src import (
    create_orchestrator_agent,
    create_adk_app,
    initialize_vertex_ai,
    deploy_to_vertex_ai
)
import asyncio

async def deploy():
    # Initialize Vertex AI
    client = initialize_vertex_ai()
    
    # Create and wrap agent
    orchestrator = create_orchestrator_agent()
    app = create_adk_app(orchestrator)
    
    # Deploy to Vertex AI
    remote_agent = deploy_to_vertex_ai(app, client)
    
    print(f"✅ Deployed! Resource: {remote_agent.resource_name}")

asyncio.run(deploy())
```

## Configuration

Create a `.env` file in the project root:

```bash
GCP_PROJECT_ID=your-project-id
GCP_LOCATION=us-central1
GCP_STAGING_BUCKET=gs://your-bucket-name
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

Or configure in `src/config.py`:

```python
PROJECT_ID = "your-project-id"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://your-bucket-name"
```

### Local Development
```bash
# Install in development mode
pip install -e .

# Run with auto-reload (in Jupyter)
%load_ext autoreload
%autoreload 2
```

## Acknowledgments

- Built with Google Vertex AI Agent Engine
- Uses Gemini 2.0 Flash model
- GitHub API for profile analysis
- Agent Development Kit (ADK) for multi-agent orchestration


## Quick Links

- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [ADK Documentation](https://cloud.google.com/vertex-ai/docs/generative-ai/agent-development-kit)
- [GitHub API Docs](https://docs.github.com/en/rest)
- [Google Cloud Console](https://console.cloud.google.com)
