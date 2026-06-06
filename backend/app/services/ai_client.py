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
        """从 AI 回复中提取 JSON（多层容错）

        部分模型（尤其是国内模型）即使开了 json_mode 也可能在 JSON
        前后附加说明文字、漏掉闭合括号、或使用中文引号。本方法逐层尝试。
        """
        # 1. 直接解析
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

        # 3. 找到第一个 { 和最后一个 }，提取中间内容
        start = response.find("{")
        end = response.rfind("}")
        if start != -1 and end > start:
            candidate = response[start:end + 1]
            # 清洗常见问题：尾部多余逗号
            candidate = re.sub(r",\s*([}\]])", r"\1", candidate)
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

        # 4. 如果仍然失败，尝试修复不完整的 JSON（补全缺失的闭合括号）
        if start != -1:
            candidate = response[start:]
            # 统计括号数量，自动补全
            open_braces = candidate.count("{") - candidate.count("}")
            open_brackets = candidate.count("[") - candidate.count("]")
            candidate += "}" * open_braces + "]" * open_brackets
            candidate = re.sub(r",\s*([}\]])", r"\1", candidate)
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

        raise ValueError(
            f"无法解析 AI 回复为 JSON。"
            f"前200字符: {response[:200]}\n"
            f"后200字符: {response[-200:] if len(response) > 200 else ''}"
        )


default_client = AIClient()
