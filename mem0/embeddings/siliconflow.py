import os
import requests
from typing import Optional

from mem0.configs.embeddings.base import BaseEmbedderConfig
from mem0.embeddings.base import EmbeddingBase


class SiliconFlowEmbedding(EmbeddingBase):
    def __init__(self, config: Optional[BaseEmbedderConfig] = None):
        super().__init__(config)

        self.config.model = self.config.model or "BAAI/bge-m3"
        self.config.embedding_dims = self.config.embedding_dims or 1024

        self.api_key = self.config.api_key or os.getenv("SILICONFLOW_API_KEY")
        self.base_url = self.config.siliconflow_base_url or os.getenv("SILICONFLOW_API_BASE")

    def embed(self, text):
        """
        Get the embedding for the given text using SiliconFlow.

        Args:
            text (str): The text to embed.

        Returns:
            list: The embedding vector.
        """
        text = text.replace("\n", " ")
        payload = {
            "model": self.config.model,
            "input": text,
            "encoding_format": "float"
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        return requests.request("POST", self.base_url, json=payload, headers=headers).json()['data'][0]['embedding']
