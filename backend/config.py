from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # ======================
    # Application
    # ======================
    app_name: str = "Personal Documentation Agent"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # ======================
    # API Settings
    # ======================
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    
    # ======================
    # CORS
    # ======================
    cors_origins: list[str] = ["http://localhost:8501", "http://localhost:3000"]
    
    # ======================
    # Ollama (Local LLM)
    # ======================
    ollama_host: str = "http://ollama:11434"
    ollama_model: str = "mistral"
    
    # ======================
    # ChromaDB (Vector Store)
    # ======================
    chroma_host: str = "chromadb"
    chroma_port: int = 8000
    chroma_collection: str = "pda_documents"
    
    # ======================
    # Data Paths
    # ======================
    data_dir: Path = Path("/data")
    documents_dir: Path = Path("/data/documents")
    chats_dir: Path = Path("/data/chats")
    kiro_dir: Path = Path("/data/kiro")
    invoices_dir: Path = Path("/data/invoices")
    vectordb_dir: Path = Path("/data/vectordb")
    
    # ======================
    # Parser Settings
    # ======================
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # ======================
    # Upload Settings
    # ======================
    max_upload_size_mb: int = 50
    allowed_extensions: list[str] = [
        ".pdf", ".docx", ".doc", ".txt", ".md", ".json", ".jsonl"
    ]
    
    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024
    
    def get_category_dir(self, category: str) -> Path:
        """Get directory path for a document category."""
        category_map = {
            "general": self.documents_dir,
            "ai_chat_history": self.chats_dir,
            "kiro_ide_logs": self.kiro_dir,
            "car_maintenance": self.invoices_dir,
        }
        return category_map.get(category, self.documents_dir)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience instance
settings = get_settings()