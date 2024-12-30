from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
import g4f
import uvicorn
import uuid
import json
import time
import logging

app = FastAPI()

API_KEY = None

AVAILABLE_MODELS = [
    "gpt-4o-mini",
    "claude-3-haiku-20240307",
    "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
    "mistralai/Mixtral-8x7B-Instruct-v0.1",
    "claude-sonnet-3.5",
    "gpt-4",
    "nemotron-70b",
    "command-r-plus",
    "Qwen/QwQ-32B-Preview",
    "meta-llama/Llama-3.3-70B-Instruct",
]

MODEL_PROVIDER_MAP = {
    "gpt-4o-mini": "DDG",
    "claude-3-haiku-20240307": "DDG",
    "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo": "DDG",
    "mistralai/Mixtral-8x7B-Instruct-v0.1": "DDG",
    "claude-sonnet-3.5": "Blackbox AI",
    "gpt-4": "Binjie",
    "nemotron-70b": "HuggingChat",
    "command-r-plus": "HuggingChat",
    "Qwen/QwQ-32B-Preview": "HuggingChat",
    "meta-llama/Llama-3.3-70B-Instruct": "HuggingChat",
}


@app.get("/v1/models")
async def get_models(authorization: str = Header(None)):
    if API_KEY:
        if not authorization or authorization != f"Bearer {API_KEY}":
            raise HTTPException(status_code=401, detail="Unauthorized")

    models = {
        "data": [
            {
                "id": model_name,
                "object": "model",
                "created": 0,
                "owned_by": "organization-owner",
                "permission": [],
            } for model_name in AVAILABLE_MODELS
        ],
        "object": "list",
    }
    return JSONResponse(content=models)

@app.post("/v1/chat/completions")
async def chat_completions(request: Request, authorization: str = Header(None)):
    try:
        if API_KEY:
            if not authorization or authorization != f"Bearer {API_KEY}":
                raise HTTPException(status_code=401, detail="Unauthorized")

        data = await request.json()
        messages = data.get("messages")
        model = data.get("model", "gpt-4o-mini")
        stream = data.get("stream", False)
        temperature = data.get("temperature", 1.0)
        top_p = data.get("top_p", 1.0)
        n = data.get("n", 1)
        max_tokens = data.get("max_tokens", None)
        stop = data.get("stop", None)
        frequency_penalty = data.get("frequency_penalty", 0.0)
        presence_penalty = data.get("presence_penalty", 0.0)

        if model not in AVAILABLE_MODELS:
            raise HTTPException(status_code=400, detail=f"Model '{model}' is not available.")

        provider = MODEL_PROVIDER_MAP.get(model)
        if not provider:
            raise HTTPException(status_code=500, detail=f"No provider found for model '{model}'.")

        completion_params = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "provider": provider,
        }

        try:
            response = g4f.ChatCompletion.create(**completion_params)
        except Exception as e:
            logging.error(f"Error calling g4f.ChatCompletion.create: {e}")
            raise HTTPException(status_code=500, detail="Error occurred while processing the completion request.")

        if stream:
            def message_stream():
                for message in response:
                    chunk = {
                        "id": f"chatcmpl-{uuid.uuid4()}",
                        "object": "chat.completion.chunk",
                        "created": int(time.time()),
                        "model": model,
                        "choices": [{
                            "delta": {"content": message},
                            "index": 0,
                            "finish_reason": None
                        }]
                    }
                    yield f"data: {json.dumps(chunk)}\n\n"
                chunk = {
                    "id": f"chatcmpl-{uuid.uuid4()}",
                    "object": "chat.completion.chunk",
                    "created": int(time.time()),
                    "model": model,
                    "choices": [{
                        "delta": {},
                        "index": 0,
                        "finish_reason": "stop"
                    }]
                }
                yield f"data: {json.dumps(chunk)}\n\n"
                yield "data: [DONE]\n\n"

            return StreamingResponse(message_stream(), media_type="text/event-stream")
        else:
            content = ''.join(response)
            resp = {
                "id": f"chatcmpl-{uuid.uuid4()}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model,
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": content
                    },
                    "finish_reason": "stop",
                    "index": 0
                }],
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            }
            return JSONResponse(content=resp)

    except HTTPException as http_exc:
        logging.error(f"HTTP Exception: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logging.error(f"Unhandled Exception: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred. Please try again later."}
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
