from bpmn_assistant.config import logger
from bpmn_assistant.core import LLMFacade, MessageItem
from bpmn_assistant.utils import message_history_to_string, prepare_prompt


def define_change_request(
    text_llm_facade: LLMFacade,
    process: list[dict],
    message_history: list[MessageItem],
) -> str:
    """
    Defines the change to be made in the BPMN process based on the message history.
    Args:
        text_llm_facade: The LLMFacade object for text output.
        process: The BPMN process
        message_history: The message history
    Returns:
        str: The change request
    """
    prompt = prepare_prompt(
        "define_change_request.txt",
        process=str(process),
        message_history=message_history_to_string(message_history),
    )

    change_request = text_llm_facade.call(prompt, max_tokens=2000, temperature=0.4)
    logger.info(f"Change request: {change_request}")
    return change_request
