import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

from models import AskRequest, AskResponse
from service import ask_model, client
from config import settings


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)


app = FastAPI(
    title=" LLM Service",
    version="1.0.0"
)


logger = logging.getLogger("llm_service")


@app.middleware("http")
async def add_request_id(request: Request, call_next):

    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    start = time.perf_counter()

    response = await call_next(request)

    latency_ms = round(
        (time.perf_counter() - start) * 1000,
        2
    )

    response.headers["X-Request-ID"] = request_id

    logger.info(
        "request_completed request_id=%s method=%s path=%s latency_ms=%s",
        request_id,
        request.method,
        request.url.path,
        latency_ms
    )

    return response


@app.post("/chat/ask", response_model=AskResponse)
async def ask(request: Request, req: AskRequest):

    request_id = request.state.request_id

    logger.info(
        "model_call_started request_id=%s model=%s",
        request_id,
        settings.model
    )

    answer = await ask_model(req.prompt)

    logger.info(
        "model_call_completed request_id=%s",
        request_id
    )

    return AskResponse(answer=answer)


@app.post("/chat/stream")
async def stream(request: Request, req: AskRequest):

    request_id = request.state.request_id

    logger.info(
        "stream_started request_id=%s model=%s",
        request_id,
        settings.model
    )

    async def generate():

        response = await client.chat.completions.create(
            model=settings.model,
            temperature=settings.temperature,
            messages=[
                {
                    "role": "user",
                    "content": req.prompt
                }
            ],
            stream=True,
            timeout=settings.request_timeout
        )

        async for chunk in response:

            content = chunk.choices[0].delta.content

            if content:
                yield f"data: {content}\n\n"

        yield "data: [DONE]\n\n"

        logger.info(
            "stream_completed request_id=%s",
            request_id
        )

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )