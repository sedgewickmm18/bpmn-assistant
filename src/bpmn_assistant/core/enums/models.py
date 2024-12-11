from enum import Enum


class OpenAIModels(Enum):
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4O = "gpt-4o"


class AnthropicModels(Enum):
    HAIKU_3_5 = "claude-3-5-haiku-20241022"
    SONNET_3_5 = "claude-3-5-sonnet-20241022"


class GoogleModels(Enum):
    GEMINI_1_5_FLASH = "gemini-1.5-flash"
    GEMINI_1_5_PRO = "gemini-1.5-pro"
