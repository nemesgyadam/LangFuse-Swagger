from pydantic import BaseModel, create_model, Field
from typing import List, Dict, Any, Optional

class RequestModelGenerator:
    @staticmethod
    def create_request_model(prompt_name: str, variables: List[str]):
        """Create a Pydantic model for request validation and documentation"""
        model_fields = {
            var_name: (
                str,
                Field(
                    ...,
                    description=f"{var_name} parameter for {prompt_name} prompt",
                    example=f"Example {var_name} value",
                ),
            )
            for var_name in variables
        }

        model_fields["API_KEY"] = (
            Optional[str],
            Field(None, description="Optional OpenAI API Key", example=""),
        )

        Model = create_model(f"{prompt_name}Request", **model_fields)
        Model.Config = type(
            "Config",
            (),
            {
                "json_schema_extra": {
                    "example": {var: f"Example {var} value" for var in variables}
                }
            },
        )
        return Model


class ResponseModelGenerator:
    @staticmethod
    def create_response_model(prompt_name: str, output_structure: Dict[str, Any] = None):
        """Dynamically create a structured response model based on Langfuse config"""

        type_mapping = {
            "string": str,
            "integer": int,
            "float": float,
            "boolean": bool,
            "array": list,
            "object": dict,
            "tuple": tuple
        }

        if output_structure:
            properties = output_structure.get("properties", {})

            model_fields = {}
            for key, value in properties.items():
                json_type = value.get("type", "string")
                field_type = type_mapping.get(json_type, Any)
                description = value.get("description", f"{key} field")
                model_fields[key] = (field_type, Field(description=description))

        else:
            model_fields = {
                "response": (str, Field(..., description="The output of the Agent")),
            }

        Model = create_model(f"{prompt_name}Response", **model_fields)
        Model.Config = type(
            "Config",
            (),
            {"json_schema_extra": {"example": output_structure or {"response": "Super Smart LLM output"}}},
        )
        return Model

