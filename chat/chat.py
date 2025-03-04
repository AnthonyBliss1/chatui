import os
from openai import AsyncOpenAI
from typing import AsyncGenerator, List, Dict
from chat.models import AVAILABLE_MODELS
from chat.model_handlers import handle_openai_chat, handle_claude_chat

async def get_streaming_response(messages: List[Dict[str, str]], api_key: str, model_name: str) -> AsyncGenerator[str, None]:
    model_config = AVAILABLE_MODELS[model_name]
    
    if model_config.api_type == "openai":
        async for chunk in handle_openai_chat(messages, model_config.model_id, api_key):
            yield chunk
    elif model_config.api_type == "anthropic":
        async for chunk in handle_claude_chat(messages, model_config.model_id, api_key):
            yield chunk