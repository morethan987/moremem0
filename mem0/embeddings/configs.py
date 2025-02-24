from typing import Optional, List, Dict

from pydantic import BaseModel, Field, field_validator


class EmbedderConfig(BaseModel):
    provider: str = Field(
        description="Provider of the embedding model (e.g., 'ollama', 'openai')",
        default="siliconflow",
    )
    config: Optional[dict] = Field(description="Configuration for the specific embedding model", default={})

    @field_validator("config")
    def validate_config(cls, v, values):
        provider = values.data.get("provider")
        if provider in ["openai", "ollama", "huggingface", "azure_openai", "gemini", "vertexai", "together", "siliconflow"]:
            return v
        else:
            raise ValueError(f"Unsupported embedding provider: {provider}")
