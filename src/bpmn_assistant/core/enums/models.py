from enum import Enum


class OpenAIModels(Enum):
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4O = "gpt-4o"
    O1 = "o1-preview"
    O3_MINI = "o3-mini"


class AnthropicModels(Enum):
    HAIKU_3_5 = "claude-3-5-haiku-20241022"
    SONNET_3_5 = "claude-3-5-sonnet-20241022"


class GoogleModels(Enum):
    GEMINI_2_FLASH = "gemini-2.0-flash-exp"
    GEMINI_1_5_PRO = "gemini-1.5-pro"


class FireworksAIModels(Enum):
    LLAMA_3_3_70B = "fireworks_ai/accounts/fireworks/models/llama-v3p3-70b-instruct"
    QWEN_2_5_72B = "fireworks_ai/accounts/fireworks/models/qwen2p5-72b-instruct"
    DEEPSEEK_V3 = "fireworks_ai/accounts/fireworks/models/deepseek-v3"
    DEEPSEEK_R1 = "fireworks_ai/accounts/fireworks/models/deepseek-r1"
