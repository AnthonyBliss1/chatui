from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class ModelConfig:
    name: str
    api_type: str 
    model_id: str
    display_name: str
    
AVAILABLE_MODELS = {
    "gpt-4o": ModelConfig(
        name="gpt-4o",
        api_type="openai",
        model_id="gpt-4o",
        display_name="gpt-4o"
    ),
    "o1-preview": ModelConfig(
        name="o1-preview",
        api_type="openai",
        model_id="o1-preview",
        display_name="o1-preview"
    ),
    "o1-mini": ModelConfig(
        name="o1-mini",
        api_type="openai",
        model_id="o1-mini",
        display_name="o1-mini"
    ),
    "claude-3-5-sonnet-20241022": ModelConfig(
        name="claude-3-5-sonnet-20241022",
        api_type="anthropic",
        model_id="claude-3-5-sonnet-20241022",
        display_name="claude-3-5-sonnet"
    ),
    "claude-3-7-sonnet-latest": ModelConfig(
    name="claude-3-7-sonnet-latest",
    api_type="anthropic",
    model_id="claude-3-7-sonnet-latest",
    display_name="claude-3-7-sonnet"
    )
}

DEFAULT_MODEL = "gpt-4o"