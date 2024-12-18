import traceback

from pydantic import BaseModel

from bpmn_assistant.config import logger
from bpmn_assistant.core import LLMFacade, MessageItem
from bpmn_assistant.utils import message_history_to_string, prepare_prompt


class DefineChangeRequestResponse(BaseModel):
    change_request: str


def _validate_define_change_request(response: dict) -> None:
    """
    Validate the response from the define_change_request function.
    Args:
        response: The response to validate
    Raises:
        ValueError: If the response is invalid
    """
    if "change_request" not in response:
        raise ValueError("Invalid response: 'change_request' key not found")


def define_change_request(
    llm_facade: LLMFacade,
    process: list[dict],
    message_history: list[MessageItem],
    max_retries: int = 3,
) -> str:
    """
    Defines the change to be made in the BPMN process based on the message history.
    Args:
        llm_facade: The LLM facade object
        process: The BPMN process
        message_history: The message history
        max_retries: The maximum number of retries in case of failure
    Returns:
        str: The change request
    """
    prompt = prepare_prompt(
        "define_change_request.txt",
        process=str(process),
        message_history=message_history_to_string(message_history),
    )

    attempts = 0

    while attempts < max_retries:

        attempts += 1

        try:
            json_object = llm_facade.call(prompt, max_tokens=100, temperature=0.4)
            _validate_define_change_request(json_object)
            logger.info(f"Change request: {json_object['change_request']}")
            return json_object["change_request"]
        except Exception as e:
            logger.warning(
                f"Validation error (attempt {attempts}): {str(e)}\n"
                f"Traceback: {traceback.format_exc()}"
            )

            prompt = f"Error: {str(e)}. Try again."

    raise Exception(
        "Maximum number of retries reached. Could not define change request."
    )
