from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from starlette.middleware.cors import CORSMiddleware

from bpmn_assistant.api.requests import (
    BpmnToJsonRequest,
    ConversationalRequest,
    DetermineIntentRequest,
    ModifyBpmnRequest,
)
from bpmn_assistant.config import logger
from bpmn_assistant.core.enums.models import OpenAIModels
from bpmn_assistant.core.enums.output_modes import OutputMode
from bpmn_assistant.services import (
    BpmnJsonGenerator,
    BpmnModelingService,
    BpmnXmlGenerator,
    ConversationalService,
    determine_intent,
)
from bpmn_assistant.utils import get_available_providers, get_llm_facade

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bpmn_modeling_service = BpmnModelingService()
bpmn_xml_generator = BpmnXmlGenerator()


@app.post("/bpmn_to_json")
def _bpmn_to_json(request: BpmnToJsonRequest) -> JSONResponse:
    """
    Convert the BPMN XML to its JSON representation
    """
    try:
        bpmn_json_generator = BpmnJsonGenerator()
        result = bpmn_json_generator.create_bpmn_json(request.bpmn_xml)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/available_providers")
def _available_providers() -> JSONResponse:
    """
    Get the available LLM providers
    """
    providers = get_available_providers()
    return JSONResponse(content=providers)


def replace_reasoning_model(model: str) -> str:
    """
    Returns GPT-4o if o1-preview is requested, or GPT-4o-mini if o1-mini is requested.
    Otherwise returns the original model.
    """
    if model == OpenAIModels.O1.value:
        return OpenAIModels.GPT_4O.value
    elif model == OpenAIModels.O1_MINI.value:
        return OpenAIModels.GPT_4O_MINI.value
    return model


@app.post("/determine_intent")
async def _determine_intent(request: DetermineIntentRequest) -> JSONResponse:
    """
    Determine the intent of the user query
    """
    try:
        # TODO: fix once o1 API becomes available
        model = replace_reasoning_model(request.model)
        llm_facade = get_llm_facade(model)
        intent = determine_intent(llm_facade, request.message_history)
        return JSONResponse(content=intent)
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/modify")
async def _modify(request: ModifyBpmnRequest) -> JSONResponse:
    """
    Modify the BPMN process based on the user query. If the request does not contain a BPMN JSON,
    then create a new BPMN process. Otherwise, edit the existing BPMN process.
    """
    # TODO: fix once o1 API becomes available
    model = replace_reasoning_model(request.model)
    llm_facade = get_llm_facade(model)
    text_llm_facade = get_llm_facade(request.model, OutputMode.TEXT)
    try:
        if request.process:
            logger.info("Editing the BPMN process...")
            process = bpmn_modeling_service.edit_bpmn(
                llm_facade, text_llm_facade, request.process, request.message_history
            )
        else:
            logger.info("Creating a new BPMN process...")
            process = bpmn_modeling_service.create_bpmn(
                llm_facade, request.message_history
            )

        bpmn_xml_string = bpmn_xml_generator.create_bpmn_xml(process)

        return JSONResponse(content={"bpmn_xml": bpmn_xml_string, "bpmn_json": process})

    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/talk")
async def _talk(request: ConversationalRequest) -> StreamingResponse:
    # o1 is not needed here, and does not support streaming
    model = replace_reasoning_model(request.model)

    conversational_service = ConversationalService(model)

    if request.needs_to_be_final_comment:
        response_generator = conversational_service.make_final_comment(
            request.message_history, request.process
        )
    else:
        response_generator = conversational_service.respond_to_query(
            request.message_history, request.process
        )

    return StreamingResponse(response_generator)
