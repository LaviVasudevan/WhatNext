"""
Career Preparation Assistant - Multi-Agent System

A production-ready multi-agent system for career preparation,
deployed on Google Vertex AI Agent Engine.

Main Components:
- config: Configuration management
- tools: Tool functions for GitHub, jobs, and profile analysis
- agents: Agent factory functions
- deploy: Deployment and management utilities

Quick Start:
    >>> from src.agents import create_orchestrator_agent
    >>> from src.deploy import create_adk_app
    >>> 
    >>> orchestrator = create_orchestrator_agent()
    >>> app = create_adk_app(orchestrator)
"""

__version__ = "2.0.0"
__author__ = "LaviVasudevan"

from .config import Config, config, initialize_vertex_ai, setup_credentials
from .tools import (
    get_github_profile_data,
    trigger_job_search,
    analyze_profile_document,
)
from .agents import (
    create_github_analyzer_agent,
    create_job_research_agent,
    create_profile_analyzer_agent,
    create_orchestrator_agent,
)
from .deploy import (
    create_adk_app,
    deploy_to_vertex_ai,
    get_deployed_agent,
    query_deployed_agent,
)

__all__ = [
    # Config
    "Config",
    "config",
    "initialize_vertex_ai",
    "setup_credentials",
    
    # Tools
    "get_github_profile_data",
    "trigger_job_search",
    "analyze_profile_document",
    
    # Agents
    "create_github_analyzer_agent",
    "create_job_research_agent",
    "create_profile_analyzer_agent",
    "create_orchestrator_agent",
    
    # Deployment
    "create_adk_app",
    "deploy_to_vertex_ai",
    "get_deployed_agent",
    "query_deployed_agent",
]
