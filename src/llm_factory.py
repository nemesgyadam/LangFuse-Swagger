from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Optional, Dict, Any

class LLMFactory:
    """Factory class to create LLM instances based on model name."""
    
    # Model name patterns for different providers
    MODEL_PATTERNS = {
        "gpt": "openai",
        "claude": "anthropic",
        "gemini": "google",
        "text-": "openai",  # for text-davinci etc
        "ft:gpt": "openai",  # for fine-tuned models
        "j2": "anthropic",   # for potential future claude models
    }
    
    # Default models for each provider
    DEFAULT_MODELS = {
        "openai": "gpt-4o-mini",
        "anthropic": "claude-3-sonnet",
        "google": "gemini-pro"
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
                   **kwargs) -> Any:
        """
        Create an LLM instance based on the model name.
        
        Args:
            model (str, optional): Name of the model (e.g., "gpt-4", "claude-3-opus")
            temperature (float): Temperature for generation
            api_key (str, optional): API key if not set in environment
            **kwargs: Additional provider-specific parameters
            
        Returns:
            An instance of the appropriate LLM
        """
        # Detect provider from model name
        provider = LLMFactory.detect_provider(model) if model else "openai"
        
        # Use default model if none specified
        if not model:
            model = LLMFactory.DEFAULT_MODELS[provider]
        
        # Initialize the appropriate LLM
        if provider == "openai":
            return ChatOpenAI(
                model=model,
                temperature=temperature,
                **kwargs
            )
            
        elif provider == "anthropic":
            return ChatAnthropic(
                model=model,
                temperature=temperature,
                **kwargs
            )
            
        elif provider == "google":
            return ChatGoogleGenerativeAI(
                model=model,
                temperature=temperature,
                **kwargs
            )
            
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

def get_llm(model: str = "", temperature: float = 0.0, **kwargs) -> Any:
    """
    Simple function to get an LLM instance.
    Just pass the model name and it will figure out the provider.
    """
    return LLMFactory.create_llm(model, temperature, **kwargs)