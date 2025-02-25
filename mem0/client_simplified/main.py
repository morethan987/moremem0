import logging
import httpx
from functools import wraps
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class APIError(Exception):
    """API调用过程中发生的异常"""
    pass


def api_error_handler(func):
    """API错误处理装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP错误: {e}")
            raise APIError(f"API请求失败: {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"请求错误: {e}")
            raise APIError(f"请求失败: {str(e)}")
    return wrapper


class MemoryClient:
    """用于与Memory API交互的客户端

    该类提供了创建、获取、搜索和删除记忆的方法。

    属性:
        host (str): Memory API的基础URL
        client (httpx.Client): 用于发送API请求的HTTP客户端
    """

    def __init__(self, host: str = None):
        """初始化MemoryClient

        Args:
            host: Memory API的基础URL, 请自行填写
        """

        if not host:
            raise ValueError("Host url not found!")

        self.host = host
        self.client = httpx.Client(
            base_url=self.host,
            timeout=60.0,
        )

    @api_error_handler
    def configure(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """设置内存配置

        Args:
            config: 包含配置参数的字典

        Returns:
            包含API响应的字典

        Raises:
            APIError: 如果API请求失败
        """
        response = self.client.post("/configure", json=config)
        response.raise_for_status()
        return response.json()

    @api_error_handler
    def add(self, messages: Union[str, List[Dict[str, str]]], **kwargs) -> Dict[str, Any]:
        """添加新记忆

        Args:
            messages: 字符串消息或消息字典列表
            **kwargs: 附加参数，如user_id, agent_id, run_id, metadata

        Returns:
            包含API响应的字典

        Raises:
            APIError: 如果API请求失败
        """
        payload = {}
        
        # 处理messages参数
        if isinstance(messages, str):
            payload["messages"] = [{"role": "user", "content": messages}]
        elif isinstance(messages, list):
            payload["messages"] = messages
            
        # 添加其他参数
        payload.update({k: v for k, v in kwargs.items() if v is not None})
        
        response = self.client.post("/memories", json=payload)
        response.raise_for_status()
        return response.json()

    @api_error_handler
    def get(self, memory_id: str) -> Dict[str, Any]:
        """获取特定记忆

        Args:
            memory_id: 记忆ID

        Returns:
            包含记忆数据的字典

        Raises:
            APIError: 如果API请求失败
        """
        response = self.client.get(f"/memories/{memory_id}")
        response.raise_for_status()
        return response.json()

    @api_error_handler
    def get_all(self, **kwargs) -> List[Dict[str, Any]]:
        """获取所有记忆，可选过滤

        Args:
            **kwargs: 用于过滤的可选参数 (user_id, agent_id, run_id)

        Returns:
            包含记忆的字典列表

        Raises:
            APIError: 如果API请求失败
        """
        params = {k: v for k, v in kwargs.items() if v is not None}
        response = self.client.get("/memories", params=params)
        response.raise_for_status()
        return response.json()

    @api_error_handler
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """基于查询搜索记忆

        Args:
            query: 搜索查询字符串
            **kwargs: 附加参数，如user_id, agent_id, run_id

        Returns:
            包含搜索结果的字典列表

        Raises:
            APIError: 如果API请求失败
        """
        payload = {"query": query}
        payload.update({k: v for k, v in kwargs.items() if v is not None})
        
        response = self.client.post("/search", json=payload)
        response.raise_for_status()
        return response.json()

    @api_error_handler
    def update(self, memory_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """更新记忆

        Args:
            memory_id: 记忆ID
            data: 要更新的数据

        Returns:
            包含API响应的字典

        Raises:
            APIError: 如果API请求失败
        """
        response = self.client.put(f"/memories/{memory_id}", json=data)
        response.raise_for_status()
        return response.json()

    @api_error_handler
    def history(self, memory_id: str) -> List[Dict[str, Any]]:
        """获取特定记忆的历史

        Args:
            memory_id: 记忆ID

        Returns:
            包含记忆历史的字典列表

        Raises:
            APIError: 如果API请求失败
        """
        response = self.client.get(f"/memories/{memory_id}/history")
        response.raise_for_status()
        return response.json()

    @api_error_handler
    def delete(self, memory_id: str) -> Dict[str, str]:
        """删除特定记忆

        Args:
            memory_id: 记忆ID

        Returns:
            包含API响应的字典

        Raises:
            APIError: 如果API请求失败
        """
        response = self.client.delete(f"/memories/{memory_id}")
        response.raise_for_status()
        return response.json()

    @api_error_handler
    def delete_all(self, **kwargs) -> Dict[str, str]:
        """删除所有记忆，可选过滤

        Args:
            **kwargs: 用于过滤的可选参数 (user_id, agent_id, run_id)

        Returns:
            包含API响应的字典

        Raises:
            APIError: 如果API请求失败
        """
        params = {k: v for k, v in kwargs.items() if v is not None}
        response = self.client.delete("/memories", params=params)
        response.raise_for_status()
        return response.json()

    @api_error_handler
    def reset(self) -> Dict[str, str]:
        """重置所有记忆

        Returns:
            包含API响应的字典

        Raises:
            APIError: 如果API请求失败
        """
        response = self.client.post("/reset")
        response.raise_for_status()
        return response.json()