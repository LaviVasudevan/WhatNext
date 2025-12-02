"""
Agent definitions for Career Preparation Assistant.

This module contains factory functions to create all the specialized
agents used in the multi-agent system:
- GitHub Analyzer Agent
- Job Requirements Agent
- Profile Analyzer Agent
- Orchestrator Agent (main coordinator)
"""

from google import adk
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

from .tools import (
    get_github_profile_data,
    trigger_job_search,
    analyze_profile_document
)
from .config import Config


# ============================================================================
# Agent Instructions (Prompts)
# ============================================================================

GITHUB_AGENT_INSTRUCTIONS = """You are a GitHub profile analyzer and technical skills assessor.

Your role is to analyze GitHub profiles to assess:
- Programming languages and proficiency levels
- Project complexity and scope
- Repository topics and technologies
- Code activity and consistency
- Quality indicators (stars, forks, contributions)

Provide encouraging but honest analysis with actionable insights.

Focus on:
1. Technical depth (how complex are the projects?)
2. Breadth (variety of technologies and domains)
3. Consistency (commit patterns and maintenance)
4. Impact (community engagement, stars, forks)

Be supportive and constructive in your feedback."""


JOB_RESEARCH_AGENT_INSTRUCTIONS = """You are a job requirements research specialist with deep knowledge of tech industry roles.

Your role is to provide comprehensive information about:
- Must-have and nice-to-have technical skills
- Company-specific technologies and practices
- Interview process and expectations
- Career level requirements (entry, mid, senior)

Special focus areas:
- FAANG companies (Facebook/Meta, Amazon, Apple, Netflix, Google)
- ML Engineer roles: TensorFlow, PyTorch, MLOps, Cloud platforms (GCP, AWS)
- Software Engineer roles: Data structures, algorithms, system design
- Data Engineer roles: ETL, data pipelines, big data tools

Provide specific, actionable information. Reference actual job postings
and industry standards when possible.

Be realistic about requirements while being encouraging about growth paths."""


PROFILE_AGENT_INSTRUCTIONS = """You are a professional profile analyzer and career assessment specialist.

Your role is to analyze resumes and LinkedIn profiles to assess:
- Work experience and career progression
- Technical skills and proficiency levels
- Educational background and certifications
- Notable achievements and projects
- Strengths and areas for improvement

Analysis framework:
1. Experience Quality: Depth, relevance, impact
2. Skills Assessment: Technical skills, tools, frameworks
3. Education & Credentials: Degrees, certifications, training
4. Career Trajectory: Growth, transitions, focus areas

Provide supportive and constructive feedback that:
- Highlights strengths and achievements
- Identifies growth opportunities
- Suggests specific improvements
- Maintains a positive, motivating tone"""


ORCHESTRATOR_INSTRUCTIONS = """You are a career preparation coach helping people prepare for their dream jobs.

CRITICAL WORKFLOW - Follow this EXACT sequence:

**PHASE 1 - Immediate Parallel Analysis (DO THIS FIRST):**
When user provides their target role, company, and GitHub username:
1. IMMEDIATELY call BOTH tools in parallel (do NOT wait for user):
   - analyze_github_profile(username) 
   - research_job_requirements(company, role)
2. Do NOT ask for resume yet - analyze these first

**PHASE 2 - Resume Collection:**
After receiving results from BOTH parallel tools:
1. Acknowledge what you learned from GitHub and job research
2. Ask user to paste their resume/LinkedIn profile content
3. Wait for their response

**PHASE 3 - Resume Analysis:**
Once user provides resume:
1. Call analyze_professional_profile(profile_text)
2. Wait for analysis results

**PHASE 4 - Synthesis (KEEP CONCISE):**
Create a focused roadmap with:

**Strengths Aligned with Role:**
- List 3-5 key strengths from their profile that match job requirements
- Be specific about how each strength aligns

**Skill Gaps:**
- Identify 3-5 critical gaps between their skills and job requirements
- Prioritize by importance for the role

**8-Week Preparation Plan:**
Present as concise weekly chunks:
- Week 1-2: [Focus area] - [Key activities] - [Resources: 2-3 specific links]
- Week 3-4: [Focus area] - [Key activities] - [Resources: 2-3 specific links]
- Week 5-6: [Focus area] - [Key activities] - [Resources: 2-3 specific links]  
- Week 7-8: [Focus area] - [Key activities] - [Resources: 2-3 specific links]

Keep each week's description to 2-3 sentences. Focus on actionable items only.

**Success Metrics:**
- Bullet points for measuring progress at weeks 2, 4, 6, 8

Communication style:
- Be encouraging and realistic
- Use specific examples from their profiles
- Provide actionable advice with resources
- Maintain professional but friendly tone

IMPORTANT: Always trigger parallel tools FIRST before asking for more input."""


# ============================================================================
# Agent Factory Functions
# ============================================================================

def create_github_analyzer_agent(model_name: str = None) -> adk.Agent:
    """
    Create GitHub profile analyzer agent.
    
    Args:
        model_name: Model to use (defaults to Config.MODEL_NAME)
        
    Returns:
        Configured GitHub analyzer agent
    """
    github_tool = FunctionTool(func=get_github_profile_data)
    
    return adk.Agent(
        name="GitHubAnalyzer",
        model=model_name or Config.MODEL_NAME,
        instruction=GITHUB_AGENT_INSTRUCTIONS,
        tools=[github_tool],
    )


def create_job_research_agent(model_name: str = None) -> adk.Agent:
    """
    Create job requirements research agent.
    
    Args:
        model_name: Model to use (defaults to Config.MODEL_NAME)
        
    Returns:
        Configured job research agent
    """
    job_search_trigger_tool = FunctionTool(func=trigger_job_search)
    
    return adk.Agent(
        name="JobRequirementsResearcher",
        model=model_name or Config.MODEL_NAME,
        instruction=JOB_RESEARCH_AGENT_INSTRUCTIONS,
        tools=[job_search_trigger_tool],
    )


def create_profile_analyzer_agent(model_name: str = None) -> adk.Agent:
    """
    Create professional profile analyzer agent.
    
    Args:
        model_name: Model to use (defaults to Config.MODEL_NAME)
        
    Returns:
        Configured profile analyzer agent
    """
    profile_tool = FunctionTool(func=analyze_profile_document)
    
    return adk.Agent(
        name="ProfileAnalyzer",
        model=model_name or Config.MODEL_NAME,
        instruction=PROFILE_AGENT_INSTRUCTIONS,
        tools=[profile_tool],
    )


def create_orchestrator_agent(model_name: str = None) -> adk.Agent:
    """
    Create main orchestrator agent that coordinates all specialist agents.
    
    The orchestrator manages the workflow:
    1. Parallel execution of GitHub + Job analysis
    2. Request for resume/profile
    3. Sequential profile analysis
    4. Synthesis and roadmap generation
    
    Args:
        model_name: Model to use (defaults to Config.MODEL_NAME)
        
    Returns:
        Configured orchestrator agent with all specialist agents as tools
    """
    # Create specialist agents
    github_analyzer = create_github_analyzer_agent(model_name)
    job_researcher = create_job_research_agent(model_name)
    profile_analyzer = create_profile_analyzer_agent(model_name)
    
    # Convert agents to tools
    github_analyzer_tool = AgentTool(agent=github_analyzer)
    job_requirements_tool = AgentTool(agent=job_researcher)
    profile_analysis_tool = AgentTool(agent=profile_analyzer)
    
    # Create orchestrator with all tools
    return adk.Agent(
        name="CareerPrepOrchestrator",
        model=model_name or Config.MODEL_NAME,
        instruction=ORCHESTRATOR_INSTRUCTIONS,
        tools=[
            github_analyzer_tool,
            job_requirements_tool,
            profile_analysis_tool,
            PreloadMemoryTool(),  # Memory management
        ],
    )


def get_agent_info() -> None:
    """Print information about available agents."""
    agents_info = [
        {
            "name": "GitHub Analyzer",
            "function": "create_github_analyzer_agent()",
            "purpose": "Analyzes GitHub profiles for technical skills",
            "tools": ["get_github_profile_data"]
        },
        {
            "name": "Job Requirements Researcher",
            "function": "create_job_research_agent()",
            "purpose": "Researches job requirements and expectations",
            "tools": ["trigger_job_search"]
        },
        {
            "name": "Profile Analyzer",
            "function": "create_profile_analyzer_agent()",
            "purpose": "Analyzes resumes and professional profiles",
            "tools": ["analyze_profile_document"]
        },
        {
            "name": "Career Prep Orchestrator",
            "function": "create_orchestrator_agent()",
            "purpose": "Main coordinator for multi-agent workflow",
            "tools": ["All specialist agents + Memory"]
        }
    ]
    
    print("\n" + "=" * 70)
    print("Available Agents")
    print("=" * 70)
    
    for info in agents_info:
        print(f"\n {info['name']}")
        print(f"   Function: {info['function']}")
        print(f"   Purpose: {info['purpose']}")
        print(f"   Tools: {', '.join(info['tools'])}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    # Display agent information when run directly
    get_agent_info()
