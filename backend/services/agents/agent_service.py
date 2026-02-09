from typing import Optional

from backend.config import settings


class AgentService:
    """
    LangChain agent service.
    
    Placeholder for Phase 3 implementation.
    """
    
    def __init__(self):
        self.model_name = settings.ollama_model
        self.ollama_host = settings.ollama_host
        self._agent = None
    
    async def initialize(self):
        """Initialize LangChain agent with tools."""
        # TODO: Implement in Phase 3
        pass
    
    async def query(
        self,
        query: str,
        category: Optional[str] = None,
        max_results: int = 5
    ) -> dict:
        """
        Process a user query through the agent.
        
        Returns:
            dict with 'answer', 'sources', 'reasoning_steps'
        """
        # TODO: Implement in Phase 3
        return {
            "answer": "Agent not implemented yet",
            "sources": [],
            "reasoning_steps": ["Placeholder"]
        }


# Singleton instance
agent_service = AgentService()