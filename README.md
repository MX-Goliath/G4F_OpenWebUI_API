# G4F_OpenWebUI_API
A project to integrate neural networks with G4F inside OpenWebUI.

This project utilizes the G4F library, which allows access to neural networks such as GPT-4o, Claude, Llama, and others through third-party providers. The list of available models by default is as follows:

## List of Available Models
```python
AVAILABLE_MODELS = [
    "gpt-4o-mini",
    "claude-3-haiku-20240307",
    "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
    "mistralai/Mixtral-8x7B-Instruct-v0.1",
    "claude-3-5-sonnet",
    "claude-3-opus-20240229-gcp",
    "gpt-4o-2024-08-06",
    "gpt-4",
    "llama-3.1-405b",
]
```

Each model requires a specific provider mapping.

## Model and Provider Mapping
```python
MODEL_PROVIDER_MAP = {
    "gpt-4o-mini": "DDG",  # Replace "Ails" with the appropriate provider
    "claude-3-haiku-20240307": "DDG",
    "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo": "DDG",
    "mistralai/Mixtral-8x7B-Instruct-v0.1": "DDG",
    "claude-3-5-sonnet": "Liaobots",
    "claude-3-opus-20240229-gcp": "Liaobots",
    "gpt-4o-2024-08-06": "Liaobots",
    "gpt-4": "Binjie",
    "llama-3.1-405b": "Blackbox"
}
```

## Required Libraries
To use this project, you need to install the following libraries: `fastapi`, `g4f`, `uvicorn`, `uuid`, and any additional dependencies for `g4f` that may be required. Missing libraries might appear on the first run.
```bash
pip install fastapi uvicorn uuid g4f
```
## Running
```bash
python OpenWebUI_G4F.py
```
## OpenWebUI Integration
To connect this API to OpenWebUI, navigate to **Settings** -> **Connection** and set the **Base API Address** to `http://0.0.0.0:8000/v1`. Leave the API key field empty.
