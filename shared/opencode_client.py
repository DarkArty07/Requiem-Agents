"""OpenCode Go API client — HTTP client for chat completions."""
import os
import httpx
from typing import Optional

OPENCODE_GO_BASE_URL = "https://opencode.ai/zen/go/v1"
DEFAULT_TIMEOUT = 120


async def chat_completion(
    messages: list[dict],
    model: str,
    system_prompt: Optional[str] = None,
    max_tokens: int = 16384,
) -> dict:
    """Make a chat completion request to OpenCode Go API.
    
    Returns dict with: content, input_tokens, output_tokens, model
    """
    api_key = os.environ.get("OPENCODE_GO_API_KEY")
    if not api_key:
        raise ValueError("OPENCODE_GO_API_KEY not set in environment")
    
    full_messages = []
    if system_prompt:
        full_messages.append({"role": "system", "content": system_prompt})
    full_messages.extend(messages)
    
    payload = {
        "model": model,
        "messages": full_messages,
        "max_tokens": max_tokens,
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        response = await client.post(
            f"{OPENCODE_GO_BASE_URL}/chat/completions",
            json=payload,
            headers=headers,
        )
        response.raise_for_status()
        data = response.json()
    
    content = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    
    return {
        "content": content,
        "input_tokens": usage.get("prompt_tokens", 0),
        "output_tokens": usage.get("completion_tokens", 0),
        "model": data.get("model", model),
    }
