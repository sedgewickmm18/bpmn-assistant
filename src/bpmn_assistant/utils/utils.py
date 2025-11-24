import os
import json

from dotenv import load_dotenv

import litellm

for mod in litellm.model_list_set:
    if mod.startswith('olla'): print(mod)

from bpmn_assistant.core import LLMFacade, MessageItem
from bpmn_assistant.core.enums import (
    AnthropicModels,
    FireworksAIModels,
    GoogleModels,
    OpenAIModels,
    OutputMode,
    Provider,
)


def get_llm_facade(model: str, output_mode: OutputMode = OutputMode.JSON) -> LLMFacade:
    """
    Get the LLM facade based on the model type
    Args:
        model: The model to use
        output_mode: The output mode for the LLM response (JSON or text)
    Returns:
        LLMFacade: The LLM facade
    Raises:
        Exception: If the model is invalid or if the required API key is not set
    """
    load_dotenv(override=True)

    #print('MODEL', model)

    if is_openai_model(model):
        api_key = os.getenv("OPENAI_API_KEY")
        provider = Provider.OPENAI
    elif is_anthropic_model(model):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        provider = Provider.ANTHROPIC
    elif is_google_model(model):
        api_key = os.getenv("GEMINI_API_KEY")
        provider = Provider.GOOGLE
    elif is_fireworks_ai_model(model):
        api_key = os.getenv("FIREWORKS_AI_API_KEY")
        provider = Provider.FIREWORKS_AI
    elif model.startswith('ollama'):
        api_key='sk-3456'           # satisfy LiteLLM
        provider = Provider.OLLAMA
    else:
        raise Exception("Invalid model")

    if not api_key:
        raise Exception(f"API key not found for provider {provider}")

    return LLMFacade(
        provider,
        api_key,
        model,
        output_mode=output_mode,
    )


def get_available_providers() -> dict:
    load_dotenv(override=True)
    openai_api_key = os.getenv("OPENAI_API_KEY")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    fireworks_api_key = os.getenv("FIREWORKS_AI_API_KEY")

    if openai_api_key is not None and len(openai_api_key) > 0:
        openai_present = []
        for mod in litellm.model_list_set:
            if mod.startswith("openai"):
                openai_present.append(mod)
    else: openai_present = False
    if is_port_in_use(11434):
        ollama_present = []
        for mod in litellm.model_list_set:
            if mod.startswith("ollama_chat/"):
                ollama_present.append(mod)
    else: ollama_present = False

    #openai_present = openai_api_key is not None and len(openai_api_key) > 0
    anthropic_present = anthropic_api_key is not None and len(anthropic_api_key) > 0
    google_present = gemini_api_key is not None and len(gemini_api_key) > 0
    fireworks_ai_present = fireworks_api_key is not None and len(fireworks_api_key) > 0
    #ollama_present = is_port_in_use(11434)
    #openai_present |= ollama_present  # TODO make ollama a separate provider

    dct = { 
        "ollama" : ollama_present,
        "openai": openai_present,
        "anthropic": anthropic_present,
        "google": google_present,
        "fireworks_ai": fireworks_ai_present,
    }
    return dct

def is_port_in_use(port: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        in_use = False
        try:
            in_use = s.connect_ex(('localhost', port)) == 0
        except Exception as conexc:
            pass
        return in_use

def replace_reasoning_model(model: str) -> str:
    """
    Replaces reasoning models with more lightweight models.
    """
    if model in [
        FireworksAIModels.DEEPSEEK_R1.value,
        FireworksAIModels.QWEN_3_235B.value,
    ]:
        return FireworksAIModels.LLAMA_4_MAVERICK.value
    return model


def is_openai_model(model: str) -> bool:
    return model in [model.value for model in OpenAIModels]


def is_anthropic_model(model: str) -> bool:
    return model in [model.value for model in AnthropicModels]


def is_google_model(model: str) -> bool:
    return model in [model.value for model in GoogleModels]


def is_fireworks_ai_model(model: str) -> bool:
    return model in [model.value for model in FireworksAIModels]


def message_history_to_string(message_history: list[MessageItem]) -> str:
    """
    Convert a message history list into a formatted string.
    """
    return "\n".join(
        f"{message.role.capitalize()}: {message.content}" for message in message_history
    )
