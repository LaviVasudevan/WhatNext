"""
Configuration module for Career Preparation Assistant.

This module handles all configuration for Google Cloud Platform
and Vertex AI setup.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for Career Prep Agent."""
    
    # Google Cloud Project Configuration
    PROJECT_ID: str = os.getenv(
        "GCP_PROJECT_ID", 
        "gen-lang-client-0685740442"
    )
    
    LOCATION: str = os.getenv(
        "GCP_LOCATION", 
        "us-central1"
    )
    
    STAGING_BUCKET: str = os.getenv(
        "GCP_STAGING_BUCKET", 
        "gs://career-prep-agent-lv"
    )
    
    # Authentication
    CREDENTIALS_PATH: Optional[str] = os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS"
    )
    
    # Agent Configuration
    MODEL_NAME: str = "gemini-2.0-flash-exp"
    
    # Deployment Configuration
    AGENT_DISPLAY_NAME: str = "Career Preparation Assistant"
    AGENT_DESCRIPTION: str = (
        "Multi-agent system with parallel GitHub/job analysis "
        "and sequential resume processing"
    )
    
    # Labels for organization
    DEPLOYMENT_LABELS: dict = {
        "environment": "production",
        "team": "career-services",
        "version": "v2-parallel"
    }
    
    @classmethod
    def get_requirements(cls) -> list[str]:
        """Get list of Python requirements for deployment."""
        return [
            "google-cloud-aiplatform[agent_engines,adk]>=1.112",
            "requests>=2.31.0",
            "PyPDF2>=3.0.0",
        ]
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that all required configuration is present."""
        if not cls.PROJECT_ID:
            raise ValueError("GCP_PROJECT_ID is not set")
        
        if not cls.STAGING_BUCKET:
            raise ValueError("GCP_STAGING_BUCKET is not set")
        
        if not cls.STAGING_BUCKET.startswith("gs://"):
            raise ValueError("STAGING_BUCKET must start with gs://")
        
        return True
    
    @classmethod
    def display(cls) -> None:
        """Display current configuration (excluding sensitive data)."""
        print("=" * 70)
        print("Configuration")
        print("=" * 70)
        print(f"Project ID:      {cls.PROJECT_ID}")
        print(f"Location:        {cls.LOCATION}")
        print(f"Staging Bucket:  {cls.STAGING_BUCKET}")
        print(f"Model:           {cls.MODEL_NAME}")
        print(f"Credentials:     {'✓ Set' if cls.CREDENTIALS_PATH else '✗ Not Set'}")
        print("=" * 70)


# Create a singleton instance
config = Config()


def setup_credentials(credentials_path: str) -> None:
    """
    Set up Google Cloud credentials.
    
    Args:
        credentials_path: Path to service account JSON file
    """
    if not os.path.exists(credentials_path):
        raise FileNotFoundError(f"Credentials file not found: {credentials_path}")
    
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
    Config.CREDENTIALS_PATH = credentials_path
    print(f"🔐 Service Account authentication configured: {credentials_path}")


def initialize_vertex_ai():
    """Initialize Vertex AI with current configuration."""
    import vertexai
    
    # Validate configuration
    Config.validate()
    
    # Initialize Vertex AI
    vertexai.init(
        project=Config.PROJECT_ID,
        location=Config.LOCATION,
        staging_bucket=Config.STAGING_BUCKET
    )
    
    print("✅ Vertex AI initialized!")
    Config.display()
    
    return vertexai.Client(
        project=Config.PROJECT_ID,
        location=Config.LOCATION,
    )


if __name__ == "__main__":
    # Display configuration when run directly
    Config.display()
