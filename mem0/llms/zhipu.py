import json
import os
from typing import Dict, List, Optional

from openai import OpenAI

from mem0.configs.llms.base import BaseLlmConfig
from mem0.llms.base import LLMBase


class ZhipuLLM(LLMBase):
    """
    A class to interact with Zhipu's models for generating responses using LLMs.
    """

    def __init__(self, config: Optional[BaseLlmConfig] = None):
        """
        Initializes the ZhipuLLM instance with the given configuration.

        Args:
            config (Optional[BaseLlmConfig]): Configuration settings for the language model.
        """
        super().__init__(config)

        if not self.config.model:
            self.config.model = "glm-4-flash"

        api_key = self.config.api_key or os.getenv("ZHIPU_API_KEY")
        base_url = (
            self.config.aliyun_base_url
            or os.getenv("ZHIPU_API_BASE")
            or "https://open.bigmodel.cn/api/paas/v4"
        )
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        response_format=None,
    ) -> str:
        """
        Generates a response using Aliyun's model based on the provided messages.

        Args:
            messages (List[Dict[str, str]]): A list of dictionaries, each containing a 'role' and 'content' key.

        Returns:
            str: The generated response from the model.
        """
        params = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "top_p": self.config.top_p,
        }

        if response_format:
            params["response_format"] = response_format

        response = self.client.chat.completions.create(**params)
        return response.choices[0].message.content
