"""AI 客户端 — 统一适配 OpenAI 兼容接口

支持所有兼容 OpenAI Chat Completions 接口规范的模型服务：
OpenAI、DeepSeek、通义千问、智谱 GLM、Moonshot 等。
"""

import json
import re

import httpx

from ..config import settings


class AIClient:
    """OpenAI 兼容接口的轻量客户端"""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model_name: str | None = None,
    ):
        self.base_url = (base_url or settings.ai_base_url).rstrip("/")
        self.api_key = api_key or settings.ai_api_key
        self.model_name = model_name or settings.ai_model_name

    async def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        json_mode: bool = False,
    ) -> str:
        """发送聊天请求，返回模型回复文本"""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            body["response_format"] = {"type": "json_object"}

        async with httpx.AsyncClient(timeout=180.0) as client:
            resp = await client.post(url, headers=headers, json=body)
            resp.raise_for_status()
            data = resp.json()

        content = data["choices"][0]["message"]["content"]
        return content

    @staticmethod
    def parse_json(response: str) -> dict:
        """从 AI 回复中提取 JSON（多层容错）"""
        # 1. 尝试直接解析
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        # 2. 提取 ```json ... ``` 代码块
        match = re.search(r"```(?:json)?\s*([\s\S]*?)```", response)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        # 3. 提取第一个 { ... } 块
        match = re.search(r"\{[\s\S]*\}", response)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        raise ValueError(f"无法从 AI 回复中解析 JSON: {response[:200]}...")


default_client = AIClient()
