from pydantic import BaseModel, create_model, Field
from typing import List

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

class ResponseModel(BaseModel):
    response: str = Field(..., description="The output of the Agent")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "Super Smart LLM output",
            }
        }