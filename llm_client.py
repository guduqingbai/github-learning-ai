#!/usr/bin/env python3
"""
🤖 LLM 客户端 — Ollama API 封装
为自主思考系统提供本地大模型调用能力。

设计原则：
1. 零外部依赖 — 只用标准库 urllib
2. 容错 — 所有失败返回 LLMResult(success=False)，绝不抛异常
3. 缓存健康检查 — is_available() 60 秒内不重复请求
4. 超时保护 — 短思考 30s，长分析 60s
"""
import json
import time
import logging
import urllib.request
import urllib.error
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger("llm_client")


@dataclass
class LLMResult:
    """LLM 调用结果"""
    content: str = ""
    success: bool = False
    duration: float = 0.0
    error: str = ""


class LLMClient:
    """Ollama API 客户端"""

    def __init__(self, base_url: str = "http://localhost:11434",
                 model: str = "qwen3:8b",
                 timeout: float = 30.0,
                 temperature: float = 0.7,
                 max_retries: int = 2):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.temperature = temperature
        self.max_retries = max_retries

        # 健康检查缓存
        self._available: Optional[bool] = None
        self._last_health_check: float = 0.0
        self._health_cache_ttl: float = 60.0

    # ── 公开 API ──

    def chat(self, system_prompt: str, user_message: str,
             timeout: Optional[float] = None) -> LLMResult:
        """发送对话请求到 Ollama"""
        start = time.time()
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "stream": False,
            "temperature": self.temperature,
            "options": {
                "num_predict": 2048,
            },
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url, data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        last_error = ""
        for attempt in range(1, self.max_retries + 2):
            try:
                resp = urllib.request.urlopen(req, timeout=timeout or self.timeout)
                body = resp.read().decode("utf-8")
                result = json.loads(body)
                content = result.get("message", {}).get("content", "")
                duration = time.time() - start
                logger.info(f"LLM 调用成功 ({duration:.1f}s, {len(content)} 字符)")
                return LLMResult(content=content, success=True, duration=duration)
            except urllib.error.HTTPError as e:
                last_error = f"HTTP {e.code}: {e.reason}"
                logger.warning(f"LLM 调用 HTTP 错误 (尝试 {attempt}): {last_error}")
            except urllib.error.URLError as e:
                last_error = f"连接失败: {e.reason}"
                logger.warning(f"LLM 连接失败 (尝试 {attempt}): {last_error}")
            except json.JSONDecodeError as e:
                last_error = f"响应解析失败: {e}"
                logger.warning(f"LLM 响应解析失败 (尝试 {attempt}): {last_error}")
            except Exception as e:
                last_error = f"未知错误: {e}"
                logger.warning(f"LLM 调用异常 (尝试 {attempt}): {last_error}")

            if attempt <= self.max_retries:
                time.sleep(0.5 * attempt)  # 递增等待

        duration = time.time() - start
        self._available = False  # 连续失败标记不可用
        logger.error(f"LLM 调用彻底失败 ({duration:.1f}s): {last_error}")
        return LLMResult(success=False, duration=duration, error=last_error)

    def is_available(self) -> bool:
        """检查 Ollama 是否可用（60 秒缓存）"""
        now = time.time()
        if self._available is not None and (now - self._last_health_check) < self._health_cache_ttl:
            return self._available
        return self._check_health()

    def check_health(self) -> dict:
        """详细健康诊断"""
        url = f"{self.base_url}/api/tags"
        start = time.time()
        try:
            req = urllib.request.Request(url)
            resp = urllib.request.urlopen(req, timeout=5)
            body = json.loads(resp.read().decode("utf-8"))
            models = [m["name"] for m in body.get("models", [])]
            return {
                "available": True,
                "response_time": round(time.time() - start, 2),
                "models": models,
                "model_loaded": self.model in models,
            }
        except Exception as e:
            return {
                "available": False,
                "response_time": round(time.time() - start, 2),
                "error": str(e),
            }

    def _check_health(self) -> bool:
        """内部健康检查，写入缓存"""
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags")
            resp = urllib.request.urlopen(req, timeout=5)
            self._available = resp.status == 200
        except Exception:
            self._available = False
        self._last_health_check = time.time()
        if not self._available:
            logger.debug("Ollama 不可用")
        return self._available

    def reset_health_cache(self):
        """强制清除健康检查缓存（下一次调用会重新检查）"""
        self._available = None
        self._last_health_check = 0.0


# 全局单例（延迟初始化）
_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """获取 LLM 客户端单例"""
    global _client
    if _client is None:
        _client = LLMClient()
    return _client


if __name__ == "__main__":
    import sys
    client = get_llm_client()
    health = client.check_health()
    print(f"Ollama 状态: {'✅ 可用' if health['available'] else '❌ 不可用'}")
    if health.get("models"):
        print(f"已安装模型: {', '.join(health['models'])}")
    if health.get("model_loaded"):
        print(f"目标模型 {client.model}: ✅ 已安装")
    if not health["available"]:
        print("请确保 Ollama 已启动")
        sys.exit(1)
    print("\n测试推理...")
    result = client.chat("你是一个助手", "用一句话介绍你自己。")
    if result.success:
        print(f"回复: {result.content[:100]}...")
        print(f"耗时: {result.duration:.1f}s")
    else:
        print(f"失败: {result.error}")
