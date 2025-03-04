from typing import AsyncGenerator, Dict, List
import os
from openai import AsyncOpenAI
import anthropic

async def handle_openai_chat(messages: List[Dict[str, str]], model_id: str, api_key: str) -> AsyncGenerator[str, None]:
    client = AsyncOpenAI(api_key=api_key)
    try:
        stream = await client.chat.completions.create(
            model=model_id,
            messages=messages,
            stream=True
        )
        
        async for chunk in stream:
            if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        yield f"Error: {str(e)}"

async def handle_claude_chat(messages: List[Dict[str, str]], model_id: str, api_key: str) -> AsyncGenerator[str, None]:
    client = anthropic.AsyncAnthropic(api_key=api_key)
    
    system_prompt = "You are Claude, an AI assistant. Be helpful and honest."
    formatted_messages = "\n\n".join([
        f"Human: {msg['content']}" if msg['role'] == 'user' else f"Assistant: {msg['content']}"
        for msg in messages
    ])
    
    try:
        stream = await client.messages.create(
            model=model_id,
            max_tokens=2048,
            system=system_prompt,
            messages=[{"role": "user", "content": formatted_messages}],
            stream=True
        )
        
        async for chunk in stream:
            if chunk.type == "content_block_delta" and chunk.delta.text:
                yield chunk.delta.text
    except Exception as e:
        yield f"Error: {str(e)}"