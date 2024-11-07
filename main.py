from src.app_generator import PromptEndpointGenerator
from fastapi import FastAPI

def create_app() -> FastAPI:
    generator = PromptEndpointGenerator()
    return generator.get_app()

if __name__ == "__main__":
    import uvicorn
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)