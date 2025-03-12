from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Optional, Dict, Any
import json

class LLMFactory:
    """Factory class to create LLM instances based on model name."""
    
    # Model name patterns for different providers
    MODEL_PATTERNS = {
        "gpt": "openai",
        "claude": "anthropic",
        "gemini": "google_vertexai",
        "text-": "openai",  # for text-davinci etc
        "ft:gpt": "openai",  # for fine-tuned models
        "j2": "anthropic",   # for potential future claude models
    }
    
    # Default models for each provider
    DEFAULT_MODELS = {
        "openai": "gpt-4o-mini",
        "anthropic": "claude-3-sonnet",
        "google_vertexai": "gemini-pro"
    }

    @staticmethod
    def detect_provider(model: str) -> str:
        """
        Detect the provider based on the model name.
        
        Args:
            model (str): Name of the model
            
        Returns:
            str: Provider name
        """
        if not model:
            return "openai"  # default provider
            
        model_lower = model.lower()
        for pattern, provider in LLMFactory.MODEL_PATTERNS.items():
            if model_lower.startswith(pattern):
                return provider
                
        raise ValueError(f"Unable to detect provider for model: {model}")

    @staticmethod
    def create_llm(model: Optional[str] = None, 
                   temperature: float = 0.0,
                   output_structure: Optional[dict] = None,
                   api_key: Optional[str] = None,
                   **kwargs) -> Any:
        """
        Create an LLM instance based on the model name.
        
        Args:
            model (str, optional): Name of the model (e.g., "gpt-4", "claude-3-opus")
            temperature (float): Temperature for generation
            output_structure (dict, optional): The structure of the output
            api_key (str, optional): API key if not set in environment
            **kwargs: Additional provider-specific parameters
            
        Returns:
            An instance of the appropriate LLM
        """
        # Detect provider from model name
        provider = LLMFactory.detect_provider(model) if model else "openai"

        extra_kwargs = {"api_key": api_key} if api_key is not None else {}

        # Use default model if none specified
        if not model:
            model = LLMFactory.DEFAULT_MODELS[provider]
        
        # Initialize the appropriate LLM
        if provider == "openai":
            llm = ChatOpenAI(
                model=model,
                temperature=temperature,
                **extra_kwargs,
                **kwargs
            )
            
        elif provider == "anthropic":
            llm = ChatAnthropic(
                model=model,
                temperature=temperature,
                **extra_kwargs,
                **kwargs
            )
            
        elif provider == "google":
            llm = ChatGoogleGenerativeAI(
                model=model,
                temperature=temperature,
                **extra_kwargs,
                **kwargs
            )
            
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

        if output_structure:
            try:
                json_schema = json.loads(output_structure) if isinstance(output_structure, str) else output_structure
                llm = llm.with_structured_output(json_schema)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON schema for structured output")

        return llm


def get_llm(model: str = "", api_key: Optional[str] = None, temperature: float = 0.0, output_structure: Optional[dict] = None, **kwargs) -> Any:
    """
    Simple function to get an LLM instance.
    Just pass the model name and it will figure out the provider.
    """
    return LLMFactory.create_llm(model, temperature, output_structure=output_structure, api_key=api_key, **kwargs)
