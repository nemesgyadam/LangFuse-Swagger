from langchain.schema import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_openai import ChatOpenAI
from langfuse.client import Langfuse
from fastapi import HTTPException
from typing import Dict, Any, List


class PromptHandler:
    def __init__(self, langfuse_client: Langfuse, prompt_config: dict):
        self.langfuse = langfuse_client
        self.prompt_config = prompt_config

    def _create_chain(self, prompt_name: str, is_chat: bool):
        """Create a Langchain chain from Langfuse prompt"""
        langfuse_prompt = self.langfuse.get_prompt(
            prompt_name, type="chat" if is_chat else "text"
        )
        if is_chat:
            prompt = ChatPromptTemplate.from_messages(
                [
                    (msg["role"], msg["content"].replace("{{", "{").replace("}}", "}"))
                    for msg in langfuse_prompt.prompt
                ]
            )
        else:
            prompt = PromptTemplate.from_template(
                langfuse_prompt.prompt.replace("{{", "{").replace("}}", "}")
            )

        config = langfuse_prompt.config or {}
        model_args = {
            "model": config.get("model", "gpt-3.5-turbo"),
            "temperature": float(config.get("temperature", 0.7)),
        }

        model = ChatOpenAI(**model_args)
        return prompt, model, StrOutputParser()

    async def run_prompt(self, prompt_file, context, model="gpt-4o-mini"):
        prompt = open(prompt_file).read()

        # Create prompt template and model
        prompt_template = ChatPromptTemplate.from_template(prompt)
        llm = ChatOpenAI(model=model)

        # Format prompt with context and get response
        formatted_prompt = prompt_template.format_messages(context=context)
        response = llm.invoke(formatted_prompt)

        return response.content

    async def handle_prompt(
        self, prompt_name: str, input_data: Any, variables: List[str]
    ):
        """Handle prompt execution and tracing"""
        try:
            # Convert input data to dictionary
            input_dict = {var: getattr(input_data, var) for var in variables}

            # Create chain components
            prompt, model, output_parser = self._create_chain(
                prompt_name, is_chat=self.prompt_config[prompt_name]["is_chat"]
            )
            chain = prompt | model | output_parser

            # Create trace
            trace = self.langfuse.trace(name=prompt_name)
            trace.update(prompt=prompt)
            trace.update(input=input_dict)

            # Record generation
            generation = trace.generation(
                name=f"{prompt_name}-generation",
                model=model.model_name,
                model_parameters={
                    "maxTokens": model.max_tokens,
                    "temperature": model.temperature,
                },
                input=prompt.format(**input_dict),
                metadata={"interface": "Swagger"},
            )

            # Execute chain
            response = chain.invoke(input=input_dict)

            generation.end(output=response)

            trace.update(output=response)

            print(f"Success! Trace URL: {trace.get_trace_url()}")

            return {"response": response}

        except Exception as e:
            print(f"Error handling prompt: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
