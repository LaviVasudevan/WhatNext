"""
Deployment module for Career Preparation Assistant.

This module handles deployment of the multi-agent system to
Vertex AI Agent Engine.
"""

import asyncio
from typing import Optional
from vertexai.agent_engines import AdkApp

from .config import Config, initialize_vertex_ai
from .agents import create_orchestrator_agent


def create_adk_app(orchestrator_agent = None) -> AdkApp:
    """
    Create AdkApp wrapper for the orchestrator agent.
    
    AdkApp automatically handles:
    - Session management (in-memory locally, cloud-based when deployed)
    - Memory management (switches to Vertex AI Memory Bank when deployed)
    - Production scaling
    
    Args:
        orchestrator_agent: Pre-created orchestrator agent (optional)
        
    Returns:
        AdkApp instance ready for local testing or deployment
    """
    if orchestrator_agent is None:
        orchestrator_agent = create_orchestrator_agent()
    
    app = AdkApp(agent=orchestrator_agent)
    
    print("✅ AdkApp created!")
    print("   - Uses in-memory sessions locally")
    print("   - Will use managed sessions when deployed")
    
    return app


async def test_local_agent(app: AdkApp, test_message: str = None) -> None:
    """
    Test the agent locally before deployment.
    
    Args:
        app: AdkApp instance to test
        test_message: Custom test message (optional)
    """
    if test_message is None:
        test_message = (
            "I want to prepare for a Machine Learning Engineer role at Google. "
            "My GitHub is your-github-username."
        )
    
    print("\n" + "=" * 70)
    print("Testing Local Agent")
    print("=" * 70)
    print(f"Test Message: {test_message}\n")
    
    async for event in app.async_stream_query(
        user_id="test-user",
        message=test_message,
    ):
        if hasattr(event, 'content') and event.content:
            print(event.content)
    
    print("\n✅ Local test complete!")


def deploy_to_vertex_ai(
    app: AdkApp,
    client = None,
    display_name: str = None,
    description: str = None
):
    """
    Deploy the agent to Vertex AI Agent Engine.
    
    Args:
        app: AdkApp instance to deploy
        client: Vertex AI client (will create if not provided)
        display_name: Display name for deployed agent
        description: Description for deployed agent
        
    Returns:
        Deployed agent (remote_agent) instance
    """
    # Initialize client if not provided
    if client is None:
        client = initialize_vertex_ai()
    
    # Validate configuration
    Config.validate()
    
    # Use config values if not provided
    if display_name is None:
        display_name = Config.AGENT_DISPLAY_NAME
    
    if description is None:
        description = Config.AGENT_DESCRIPTION
    
    print("\n" + "=" * 70)
    print("Deploying to Vertex AI Agent Engine")
    print("=" * 70)
    
    # Deploy the agent
    remote_agent = client.agent_engines.create(
        agent=app,
        config={
            "requirements": Config.get_requirements(),
            "staging_bucket": Config.STAGING_BUCKET,
            "display_name": display_name,
            "description": description,
            "labels": Config.DEPLOYMENT_LABELS,
        }
    )
    
    print("✅ Deployment initiated!")
    print(f"   Display Name: {display_name}")
    print(f"   Memory: Auto-managed by Vertex AI Memory Bank")
    print("\n⏳ Deployment may take 5-10 minutes...")
    print("   Building container, installing packages, and starting services...")
    
    return remote_agent


def get_deployed_agent(
    agent_name: str = None,
    client = None
):
    """
    Retrieve a previously deployed agent.
    
    Args:
        agent_name: Full resource name of the agent
                   (e.g., "projects/.../locations/.../reasoningEngines/...")
        client: Vertex AI client (will create if not provided)
        
    Returns:
        Deployed agent instance
        
    Example:
        >>> agent = get_deployed_agent(
        ...     "projects/123/locations/us-central1/reasoningEngines/456"
        ... )
    """
    if client is None:
        client = initialize_vertex_ai()
    
    if agent_name is None:
        raise ValueError(
            "agent_name is required. Use the resource name from deployment."
        )
    
    agent = client.agent_engines.get(name=agent_name)
    
    print(f"✅ Retrieved deployed agent: {agent_name}")
    
    return agent


async def query_deployed_agent(
    remote_agent,
    user_id: str,
    message: str,
    session_id: Optional[str] = None
) -> None:
    """
    Query a deployed agent and stream responses.
    
    Args:
        remote_agent: Deployed agent instance
        user_id: User identifier for session management
        message: Query message
        session_id: Optional session ID for continuing conversations
    """
    print("\n" + "=" * 70)
    print("Querying Deployed Agent")
    print("=" * 70)
    print(f"User: {user_id}")
    print(f"Message: {message}\n")
    
    async for event in remote_agent.async_stream_query(
        user_id=user_id,
        message=message,
        session_id=session_id,
    ):
        if hasattr(event, 'content') and event.content:
            print(event.content)
    
    print("\n✅ Query complete!")


def list_agent_operations(remote_agent) -> None:
    """
    List all available operations for a deployed agent.
    
    Args:
        remote_agent: Deployed agent instance
    """
    print("\n" + "=" * 70)
    print("Deployed Agent Operations")
    print("=" * 70)
    
    operations = remote_agent.operation_schemas()
    
    print("\nAvailable operations:")
    for op in operations:
        print(f"\n📍 {op['name']}")
        if 'description' in op:
            desc = op['description'].split('\n')[0]  # First line only
            print(f"   {desc}")


def delete_deployed_agent(remote_agent) -> None:
    """
    Delete a deployed agent.
    
    WARNING: This will permanently delete the agent and all its
    managed sessions.
    
    Args:
        remote_agent: Deployed agent instance to delete
    """
    print("\n" + "=" * 70)
    print("⚠️  Deleting Deployed Agent")
    print("=" * 70)
    
    confirm = input("Are you sure you want to delete this agent? (yes/no): ")
    
    if confirm.lower() == 'yes':
        remote_agent.delete()
        print("✅ Agent deleted successfully!")
        print("   - Reasoning Engine removed")
        print("   - Managed sessions deleted")
        print("   - Billing stopped")
    else:
        print("❌ Deletion cancelled")


# ============================================================================
# Main Deployment Script
# ============================================================================

async def main():
    """
    Main deployment workflow.
    
    This function:
    1. Creates the orchestrator agent
    2. Wraps it in AdkApp
    3. Tests locally
    4. Deploys to Vertex AI
    5. Tests the deployed version
    """
    print("\n" + "=" * 70)
    print("Career Preparation Assistant - Deployment")
    print("=" * 70)
    
    # Step 1: Create orchestrator agent
    print("\n📦 Creating orchestrator agent...")
    orchestrator = create_orchestrator_agent()
    print("✅ Orchestrator created!")
    
    # Step 2: Wrap in AdkApp
    print("\n📦 Creating AdkApp...")
    app = create_adk_app(orchestrator)
    
    # Step 3: Test locally
    print("\n🧪 Testing locally...")
    await test_local_agent(app)
    
    # Step 4: Deploy to Vertex AI
    print("\n🚀 Deploying to Vertex AI...")
    client = initialize_vertex_ai()
    remote_agent = deploy_to_vertex_ai(app, client)
    
    # Step 5: Show deployment info
    print("\n📋 Deployment Information:")
    print(f"   Resource Name: {remote_agent.resource_name}")
    print(f"   Project: {Config.PROJECT_ID}")
    print(f"   Location: {Config.LOCATION}")
    
    # Step 6: Test deployed agent
    print("\n🧪 Testing deployed agent...")
    await query_deployed_agent(
        remote_agent,
        user_id="production-test-user",
        message="Hi! I want to prepare for ML Engineer at Google. GitHub: your-github-username"
    )
    
    print("\n" + "=" * 70)
    print("🎉 Deployment Complete!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Monitor in Vertex AI console")
    print("2. Integrate into your application")
    print("3. Set up CI/CD for updates")
    print(f"\nConsole: https://console.cloud.google.com/vertex-ai/agent-engine")
    

if __name__ == "__main__":
    # Run the deployment
    asyncio.run(main())
