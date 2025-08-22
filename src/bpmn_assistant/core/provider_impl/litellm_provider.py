
# fix slightly incorrect json documents from LLMs
#  https://github.com/mangiucugna/json_repair
import json_repair as json

import os
import re
from typing import Any, Generator

import litellm
from litellm import completion
from pydantic import BaseModel

from bpmn_assistant.config import logger
from bpmn_assistant.core.enums.message_roles import MessageRole
from bpmn_assistant.core.enums.models import (
    FireworksAIModels,
    GoogleModels,
    OpenAIModels,
)
from bpmn_assistant.core.enums.output_modes import OutputMode
from bpmn_assistant.core.llm_provider import LLMProvider

# make sure we select the right provider in litellm_core_utils/get_llm_provider_logic.py
#  add granite4 to list of known models supported by ollama
litellm.ollama_models.append('granite4')
litellm.model_list.append('ollama')
litellm.model_list_set = set(litellm.model_list)
#print('OLLAMA MODELS', litellm.ollama_models)



class LiteLLMProvider(LLMProvider):
    def __init__(self, api_key: str, output_mode: OutputMode = OutputMode.JSON):
        self.output_mode = output_mode
        os.environ["FIREWORKS_AI_API_KEY"] = api_key
        os.environ["OPENAI_API_KEY"] = api_key
        os.environ["GEMINI_API_KEY"] = api_key

    def call(
        self,
        model: str,
        messages: list[dict[str, str]],
        max_tokens: int,
        temperature: float,
        structured_output: BaseModel | None = None,
    ) -> str | dict[str, Any]:
        params: dict[str, Any] = {
            "model": model,
            "messages": messages,
        }

        #print('RESPONSE PARMS PRE', model)

        if model.startswith('ollama'):
            params['api_base'] = 'http://0.0.0.0:11434'
            params['model'] = model
            params['api_key'] = 'sk-1234'

        if structured_output is not None or self.output_mode == OutputMode.JSON:
            params["response_format"] = {"type": "json_object"}

        params["max_tokens"] = max_tokens

        # GPT-5 models only support temperature=1
        if model in [OpenAIModels.GPT_5.value, OpenAIModels.GPT_5_MINI.value]:
            params["temperature"] = 1
        else:
            params["temperature"] = temperature

        #print('RESPONSE PARMS', params)
        response = completion(**params)

        if not response.choices:
            logger.error(f"Emtpy response from model: {response.choices}")
            raise Exception("Empty response from model")

        raw_output = response.choices[0].message.content
        #print('RETURNED', raw_output)

        # TODO: make sure to strip think patterns for qwen3 and deepseek models run locally
        if model in [
            FireworksAIModels.DEEPSEEK_R1.value,
            FireworksAIModels.QWEN_3_235B.value,
        ]:
            # Extract thinking phase and clean output
            think_pattern = r"<think>(.*?)</think>"
            think_match = re.search(think_pattern, raw_output, re.DOTALL)

            if think_match:
                thinking = think_match.group(1).strip()
                logger.info(f"Model thinking phase: {thinking}")
                raw_output = re.sub(
                    think_pattern, "", raw_output, flags=re.DOTALL
                ).strip()

        # for granite4 and qwen3 settle for the last json in raw output
        if model.startswith('ollama'):
            raw_output = raw_output[raw_output.rfind('```json\n') + 8:raw_output.rfind('```\n')]
            #print('RETURNED after stripping', raw_output)

        return self._process_response(raw_output)

    def stream(
        self,
        model: str,
        messages: list[dict[str, str]],
        max_tokens: int,
        temperature: float,
    ) -> Generator[str, None, None]:
        # GPT-5 models only support temperature=1
        if model in [OpenAIModels.GPT_5.value, OpenAIModels.GPT_5_MINI.value]:
            temperature = 1

        params: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True
        }

        #print('STREAM', model)
        if model.startswith('ollama'):
            params['api_base'] = 'http://0.0.0.0:11434'
            params['model'] = model
            params['api_key'] = 'sk-1234'

        response = completion(**params)

        open_tag, close_tag = "<think>", "</think>"
        inside_think = False
        thought_parts: list[str] = []
        buffer = ""
        first_payload_sent = False

        try:
            for chunk in response:
                fragment = chunk.choices[0].delta.content or ""
                if not fragment:
                    continue

                #print('RETURNED STREAM FRAGMENT', fragment)
                buffer += fragment
                while buffer:
                    if inside_think:
                        end_idx = buffer.find(close_tag)
                        if end_idx == -1:
                            thought_parts.append(buffer)
                            buffer = ""
                        else:
                            thought_parts.append(buffer[:end_idx])
                            buffer = buffer[end_idx + len(close_tag) :]
                            inside_think = False
                    else:
                        start_idx = buffer.find(open_tag)
                        if start_idx == -1:
                            payload = buffer
                            buffer = ""
                        else:
                            payload = buffer[:start_idx]
                            buffer = buffer[start_idx + len(open_tag) :]
                            inside_think = True

                        if payload:
                            if not first_payload_sent:
                                payload = payload.lstrip("\n")
                                if not payload:
                                    continue
                                first_payload_sent = True
                            #print('RETURNED STREAM PAYLOAD', payload)
                            yield payload
        finally:
            thought = "".join(thought_parts).strip()
            if thought:
                logger.info(f"Model thinking phase: {thought}")

    def get_initial_messages(self) -> list[dict[str, str]]:
        return (
            [
                {
                    "role": "system",
                    "content": "You are a helpful assistant designed to output JSON.",
                }
            ]
            if self.output_mode == OutputMode.JSON
            else []
        )

    def check_model_compatibility(self, model: str) -> bool:
        return (
            model in [m.value for m in FireworksAIModels]
            or model in [m.value for m in OpenAIModels]
            or model in [m.value for m in GoogleModels]
            or model.startswith('ollama')     # support locally run models
        )

    def _process_response(self, raw_output: str) -> str | dict[str, Any]:
        """
        Process the raw output from the model. Returns the appropriate response based on the output mode.
        If the output mode is JSON, the raw output is parsed and returned as a dict.
        If the output mode is text, the raw output is returned as is.
        """
        #print('RESPONSE', raw_output)
        if self.output_mode == OutputMode.JSON:
            try:
                result = json.loads(raw_output)

                if not isinstance(result, dict):
                    raise ValueError(f"Invalid JSON response from LLM: {result}")

                return result
            except json.decoder.JSONDecodeError as e:
                logger.error(f"JSONDecodeError: {e}")
                logger.error(f"Raw output: {raw_output}")
                raise Exception("Invalid JSON response from LLM") from e
        elif self.output_mode == OutputMode.TEXT:
            return raw_output
        else:
            raise ValueError(f"Unsupported output mode: {self.output_mode}")
