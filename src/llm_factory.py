from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Optional, Dict, Any
import json
from src.utils.models.chatopenrouter import ChatOpenRouter

class LLMFactory:
    """Factory class to create LLM instances based on model name."""

    @staticmethod
    def prepare_extra_kwargs(output_structure: dict, api_key: str = None) -> dict:
        """
            Transforms the output_structure into the appropriate JSON schema for extra_kwargs.
            If the api_key is provided, it is also added to the dictionary.

            :param output_structure: The expected output structure containing field names and their types.
            :param api_key: Optional API key to be added to extra_kwargs.
            :return: A dictionary formatted according to the extra_kwargs structure.
            """
        extra_kwargs = {}

        if output_structure:
            extra_kwargs["extra_body"] = {
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": output_structure["name"],
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": output_structure["properties"],
                            "required": list(output_structure["properties"].keys()),
                            "additionalProperties": False
                        }
                    }
                }
            }

        if api_key is not None:
            extra_kwargs["api_key"] = api_key

        return extra_kwargs

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
        extra_kwargs = LLMFactory.prepare_extra_kwargs(output_structure=output_structure, api_key=api_key)

        llm = ChatOpenRouter(model_name=model, temperature=temperature, **extra_kwargs)
        return llm


def get_llm(model: str = "", api_key: Optional[str] = None, temperature: float = 0.0, output_structure: Optional[dict] = None, **kwargs) -> Any:
    """
    Simple function to get an LLM instance.
    Just pass the model name and it will figure out the provider.
    """
    return LLMFactory.create_llm(model, temperature, output_structure=output_structure, api_key=api_key, **kwargs)
