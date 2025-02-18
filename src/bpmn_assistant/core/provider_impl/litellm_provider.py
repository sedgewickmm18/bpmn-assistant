import json
import os
import re
from typing import Any, Generator

from litellm import completion
from pydantic import BaseModel
import csv

from bpmn_assistant.config import logger
from bpmn_assistant.core.enums.message_roles import MessageRole
from bpmn_assistant.core.enums.models import FireworksAIModels, GoogleModels, OpenAIModels
from bpmn_assistant.core.enums.output_modes import OutputMode
from bpmn_assistant.core.llm_provider import LLMProvider
from .token_usage_tracker import TokenUsageTracker


class LiteLLMProvider(LLMProvider):
    def __init__(self, api_key: str, output_mode: OutputMode = OutputMode.JSON):
        self.output_mode = output_mode
        self.token_tracker = TokenUsageTracker()
        os.environ["FIREWORKS_AI_API_KEY"] = api_key
        os.environ["OPENAI_API_KEY"] = api_key
        os.environ["GEMINI_API_KEY"] = api_key

    def start_operation(self, operation_name: str):
        self.token_tracker.start_operation(operation_name)

    def end_operation(self):
        self.token_tracker.end_operation()

    def call(
        self,
        model: str,
        prompt: str,
        messages: list[dict[str, str]],
        max_tokens: int,
        temperature: float,
        structured_output: BaseModel | None = None,
    ) -> str | dict[str, Any]:
        messages.append({"role": "user", "content": prompt})

        # Only use response_format for Fireworks AI models when structured output is needed
        response_format = None
        if structured_output is not None and any(model == m.value for m in FireworksAIModels):
            response_format = structured_output
        elif self.output_mode == OutputMode.JSON:
            response_format = {"type": "json_object"}

        params = {
            "model": model,
            "response_format": response_format,
            "messages": messages,
        }

        if model != OpenAIModels.O3_MINI.value:
            params["max_tokens"] = max_tokens
            params["temperature"] = temperature

        response = completion(**params)

        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens

        self.token_tracker.add_usage(input_tokens, output_tokens, model)

        # file_exists = os.path.isfile("usage.csv")
        # with open("usage.csv", mode="a", newline="") as file:
        #     writer = csv.writer(file)
        #     if not file_exists:
        #         writer.writerow(["model", "input_tokens", "output_tokens"])
        #     writer.writerow([model, input_tokens, output_tokens])

        raw_output = response.choices[0].message.content

        if model == FireworksAIModels.DEEPSEEK_R1.value:
            # Extract thinking phase and clean output
            think_pattern = r"<think>(.*?)</think>"
            think_match = re.search(think_pattern, raw_output, re.DOTALL)

            if think_match:
                thinking = think_match.group(1).strip()
                logger.info(f"Model thinking phase: {thinking}")
                raw_output = re.sub(
                    think_pattern, "", raw_output, flags=re.DOTALL
                ).strip()

        return self._process_response(raw_output)

    def stream(
        self,
        model: str,
        prompt: str,
        messages: list[dict[str, str]],
        max_tokens: int,
        temperature: float,
    ) -> Generator[str, None, None]:
        messages.append({"role": "user", "content": prompt})

        response = completion(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        )

        for chunk in response:
            yield chunk.choices[0].delta.content or ""

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

    def add_message(
        self, messages: list[dict[str, str]], role: MessageRole, content: str
    ) -> None:
        message_role = "assistant" if role == MessageRole.ASSISTANT else "user"
        messages.append({"role": message_role, "content": content})

    def check_model_compatibility(self, model: str) -> bool:
        return model in [m.value for m in FireworksAIModels] or model in [m.value for m in OpenAIModels] or model in [m.value for m in GoogleModels]

    def _process_response(self, raw_output: str) -> str | dict[str, Any]:
        """
        Process the raw output from the model. Returns the appropriate response based on the output mode.
        If the output mode is JSON, the raw output is parsed and returned as a dict.
        If the output mode is text, the raw output is returned as is.
        """
        if self.output_mode == OutputMode.JSON:
            try:
                result = json.loads(raw_output)

                if not isinstance(result, dict):
                    raise ValueError(
                        f"Invalid JSON response from LLM: {result}"
                    )

                return result
            except json.decoder.JSONDecodeError as e:
                logger.error(f"JSONDecodeError: {e}")
                logger.error(f"Raw output: {raw_output}")
                raise Exception("Invalid JSON response from LLM") from e
        elif self.output_mode == OutputMode.TEXT:
            return raw_output
        else:
            raise ValueError(f"Unsupported output mode: {self.output_mode}")
