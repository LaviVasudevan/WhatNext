"""
Tool functions for Career Preparation Assistant.

This module contains all the tool functions used by the agents:
- GitHub profile analysis
- Job requirements research
- Professional profile analysis
"""

import requests
import json
from typing import Any, Dict


async def get_github_profile_data(username: str) -> Dict[str, Any]:
    """
    Fetch and return GitHub profile data for analysis.
    
    This tool retrieves comprehensive GitHub profile information including:
    - User profile details
    - Repository information
    - Programming languages used
    - Project topics and statistics
    
    Args:
        username: GitHub username to analyze
        
    Returns:
        Dict containing:
            - username: GitHub username
            - profile: User profile information
            - statistics: Aggregated statistics
            - repositories: List of repositories (up to 20)
            - topics: List of unique topics across repos
            - error: Error message if something went wrong
    
    Example:
        >>> data = await get_github_profile_data("LaviVasudevan")
        >>> print(data['profile']['public_repos'])
        >>> print(data['statistics']['languages'])
    """
    try:
        # Fetch user profile
        user_response = requests.get(
            f"https://api.github.com/users/{username}",
            headers={"Accept": "application/vnd.github.v3+json"},
            timeout=10
        )
        
        if user_response.status_code == 404:
            return {"error": f"User '{username}' not found on GitHub"}
        elif user_response.status_code != 200:
            return {"error": f"GitHub API error: {user_response.status_code}"}
        
        user_data = user_response.json()
                
        # Fetch repositories
        repos_response = requests.get(
            f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated",
            headers={"Accept": "application/vnd.github.v3+json"},
            timeout=10
        )
        repos_data = repos_response.json() if repos_response.status_code == 200 else []
        
        # Aggregate data
        languages = {}
        topics = set()
        total_stars = 0
        total_forks = 0
        
        for repo in repos_data:
            # Count non-forked repos for language statistics
            if not repo.get('fork'):
                if repo.get('language'):
                    languages[repo['language']] = languages.get(repo['language'], 0) + 1
            
            # Collect topics
            if repo.get('topics'):
                topics.update(repo['topics'])
            
            # Aggregate statistics
            total_stars += repo.get('stargazers_count', 0)
            total_forks += repo.get('forks_count', 0)
        
        # Build result
        result = {
            "username": username,
            "profile": {
                "name": user_data.get("name"),
                "bio": user_data.get("bio"),
                "location": user_data.get("location"),
                "public_repos": user_data.get("public_repos"),
                "followers": user_data.get("followers"),
            },
            "statistics": {
                "total_stars": total_stars,
                "total_forks": total_forks,
                "languages": languages,
                "total_topics": len(topics),
            },
            "repositories": [
                {
                    "name": repo.get("name"),
                    "description": repo.get("description"),
                    "language": repo.get("language"),
                    "stars": repo.get("stargazers_count"),
                    "topics": repo.get("topics", []),
                }
                for repo in repos_data[:20]  # Return top 20 repos
            ],
            "topics": sorted(list(topics)),
        }
        
        return result
        
    except requests.RequestException as e:
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        return {"error": f"Exception: {str(e)}"}


async def trigger_job_search(company: str, role: str) -> str:
    """
    Trigger for job requirements research.
    
    This tool signals that job requirements research should be conducted
    for a specific company and role combination.
    
    Args:
        company: Target company name (e.g., "Google", "Meta")
        role: Target job role/title (e.g., "Machine Learning Engineer")
        
    Returns:
        JSON string containing:
            - action: Type of action to perform
            - company: Target company
            - role: Target role
            - status: Ready status
    
    Example:
        >>> result = await trigger_job_search("Google", "ML Engineer")
        >>> print(result)
        {"action": "research_job_requirements", ...}
    """
    return json.dumps({
        "action": "research_job_requirements",
        "company": company,
        "role": role,
        "status": "ready_for_research",
        "message": f"Ready to research {role} position at {company}"
    })


async def analyze_profile_document(profile_text: str) -> Dict[str, Any]:
    """
    Analyze professional profile document (LinkedIn/Resume).
    
    This tool processes raw text from a resume or professional profile
    and extracts structured information about:
    - Skills and expertise
    - Work experience
    - Education
    - Relevant sections
    
    Args:
        profile_text: Raw text from resume or profile (can be pasted text,
                     extracted from PDF, or LinkedIn profile text)
        
    Returns:
        Dict containing:
            - skills: List of identified skills
            - experience: List of experience entries
            - education: List of education entries
            - raw_text: First 1000 chars of input (for reference)
            - sections: Dictionary of identified sections
            - error: Error message if analysis fails
    
    Example:
        >>> text = "EXPERIENCE\\nSoftware Engineer at Google..."
        >>> result = await analyze_profile_document(text)
        >>> print(result['sections']['experience'])
    
    Note:
        This is a basic implementation. For production use, consider
        using NLP libraries or ML models for better extraction.
    """
    try:
        profile = {
            "skills": [],
            "experience": [],
            "education": [],
            "raw_text": profile_text[:1000],  # Store sample for reference
            "sections": {}
        }
        
        lines = profile_text.split('\n')
        current_section = "unknown"
        
        # Simple section detection based on keywords
        for line in lines:
            line_lower = line.lower().strip()
            
            # Detect section headers
            if any(kw in line_lower for kw in ['experience', 'work history', 'employment']):
                current_section = "experience"
            elif any(kw in line_lower for kw in ['education', 'academic', 'degree']):
                current_section = "education"
            elif any(kw in line_lower for kw in ['skills', 'expertise', 'technical skills']):
                current_section = "skills"
            elif any(kw in line_lower for kw in ['projects', 'portfolio']):
                current_section = "projects"
            elif any(kw in line_lower for kw in ['certifications', 'certificates']):
                current_section = "certifications"
            
            # Initialize section if not exists
            if current_section not in profile["sections"]:
                profile["sections"][current_section] = []
            
            # Add line to current section
            if line.strip():  # Only add non-empty lines
                profile["sections"][current_section].append(line.strip())
        
        # Populate top-level fields from sections
        if "skills" in profile["sections"]:
            profile["skills"] = profile["sections"]["skills"]
        
        if "experience" in profile["sections"]:
            profile["experience"] = profile["sections"]["experience"]
        
        if "education" in profile["sections"]:
            profile["education"] = profile["sections"]["education"]
        
        return profile
        
    except Exception as e:
        return {"error": f"Analysis error: {str(e)}"}


# Tool metadata for documentation
TOOL_METADATA = {
    "get_github_profile_data": {
        "name": "GitHub Profile Analyzer",
        "description": "Analyzes GitHub profile for technical skills assessment",
        "parameters": ["username"],
        "returns": "Comprehensive GitHub profile data with statistics"
    },
    "trigger_job_search": {
        "name": "Job Requirements Research Trigger",
        "description": "Initiates research for job requirements",
        "parameters": ["company", "role"],
        "returns": "Confirmation with research parameters"
    },
    "analyze_profile_document": {
        "name": "Professional Profile Analyzer",
        "description": "Extracts structured data from resume/profile text",
        "parameters": ["profile_text"],
        "returns": "Structured profile data with sections"
    }
}


def get_tool_info() -> None:
    """Print information about available tools."""
    print("\n" + "=" * 70)
    print("Available Tools")
    print("=" * 70)
    
    for tool_name, metadata in TOOL_METADATA.items():
        print(f"\n📦 {metadata['name']}")
        print(f"   Function: {tool_name}")
        print(f"   Description: {metadata['description']}")
        print(f"   Parameters: {', '.join(metadata['parameters'])}")
        print(f"   Returns: {metadata['returns']}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    # Display tool information when run directly
    get_tool_info()
