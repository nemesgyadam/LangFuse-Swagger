from langchain.schema import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langfuse import Langfuse
from fastapi import HTTPException
from typing import Dict, Any, List
import logging
import json
from src.llm_factory import get_llm
import traceback
from typing import Optional
from src.utils.cost_tracker import CostTracker

try:
    import tiktoken  # type: ignore
except Exception:  # pragma: no cover
    tiktoken = None  # Fallback if tokenizer is unavailable


class PromptHandler:
    def __init__(
        self, langfuse_client: Langfuse, prompt_config: dict, logger: logging.Logger
    ):
        self.langfuse = langfuse_client
        self.prompt_config = prompt_config
        self.logger = logger
        self.logger.info("Initialized PromptHandler")

    def _create_chain(self, prompt_name: str, is_chat: bool, api_key: str):
        """Create a Langchain chain from Langfuse prompt"""
        self.logger.debug(
            f"Creating chain for prompt '{prompt_name}' (is_chat={is_chat})"
        )

        try:
            langfuse_prompt = self.langfuse.get_prompt(
                prompt_name, type="chat" if is_chat else "text"
            )
            self.logger.debug(f"Retrieved Langfuse prompt for '{prompt_name}'")

            if is_chat:
                messages = [
                    (msg["role"], msg["content"].replace("{{", "{").replace("}}", "}"))
                    for msg in langfuse_prompt.prompt
                ]
                # Anthropic require at least human message
                if not any(msg[0] == "human" for msg in messages):
                    messages.append(("human", "Give me an accurate result!"))
                prompt = ChatPromptTemplate.from_messages(messages)

                self.logger.debug(f"Created chat prompt template for '{prompt_name}'")
            else:
                prompt = PromptTemplate.from_template(
                    langfuse_prompt.prompt.replace("{{", "{").replace("}}", "}")
                )
                self.logger.debug(f"Created text prompt template for '{prompt_name}'")

            config = langfuse_prompt.config or {}
            model_args = {
                "model": config.get("model_name", "gpt-4o-mini"),
                "api_key": api_key,
                "temperature": float(config.get("temperature", 0.7)),
                "output_structure": config.get("output_structure"),
            }
            self.logger.debug(f"Model configuration for '{prompt_name}': {model_args}")

            model = get_llm(**model_args)
            self.logger.info(f"Successfully created chain for '{prompt_name}'")
            if model_args["output_structure"] is None:
                return prompt, model, StrOutputParser()
            else:
                return prompt, model

        except Exception as e:
            self.logger.error(f"Error creating chain for '{prompt_name}': {str(e)}")
            raise

    async def run_prompt(self, prompt_file, context, model="gpt-4o-mini"):
        self.logger.info(f"Running prompt from file: {prompt_file}")
        try:
            # Read prompt file
            prompt = open(prompt_file).read()
            self.logger.debug(f"Successfully read prompt file: {prompt_file}")

            # Create prompt template and model
            prompt_template = ChatPromptTemplate.from_template(prompt)
            llm = get_llm(model=model)

            self.logger.debug(f"Created prompt template and model (model={model})")

            # Format prompt with context and get response
            formatted_prompt = prompt_template.format_messages(context=context)
            self.logger.debug("Formatted prompt with context")
            response = llm.invoke(formatted_prompt)
            self.logger.info("Successfully received response from LLM")

            return response.content

        except Exception as e:
            self.logger.error(f"Error running prompt from file {prompt_file}: {str(e)}")
            raise

    def _create_trace(self, prompt_name: str, prompt, input_dict: dict):
        """Create and initialize tracing."""
        trace = self.langfuse.trace(name=prompt_name)
        trace.update(prompt=prompt)
        trace.update(input=input_dict)
        return trace

    def _extract_model_info(self, model):
        """Extract model name and parameters safely."""
        try:
            model_name = model.model_name
            model_params = {"maxTokens": model.max_tokens, "temperature": model.temperature}
        except:
            model_name = model.model
            model_params = {"maxTokens": model.max_tokens, "temperature": model.temperature}
        return model_name, model_params

    def _extract_model_info_structured_output(self, model):
        """Extract model name and parameters safely."""
        model_name = model.model_name
        model_params = {"temperature": model.temperature}
        return model_name, model_params

    def _record_generation(self, trace, prompt_name, model_name, model_params, prompt, input_dict):
        """Record generation details in the trace."""
        return trace.generation(
            name=f"{prompt_name}-generation",
            model=model_name,
            model_parameters=model_params,
            input=prompt.format(**input_dict),
            metadata={"interface": "Swagger"},
        )

    def _estimate_tokens(self, text: str, model_name: Optional[str]) -> int:
        """Estimate token count for given text and model.

        Tries to use tiktoken when available; otherwise falls back to a crude heuristic.
        """
        if not text:
            return 0
        if tiktoken is None:
            # Heuristic approximation: ~4 chars per token
            return max(1, len(text) // 4)

        # Normalize model name to an OpenAI-compatible encoding when possible
        encoding_name = "cl100k_base"
        try:
            if model_name and isinstance(model_name, str):
                # Strip provider prefix used by OpenRouter, e.g. "openai/gpt-4o-mini" -> "gpt-4o-mini"
                normalized = model_name.split("/")[-1]
                encoding = tiktoken.encoding_for_model(normalized)
            else:
                encoding = tiktoken.get_encoding(encoding_name)
        except Exception:
            encoding = tiktoken.get_encoding(encoding_name)

        try:
            return len(encoding.encode(text))
        except Exception:
            return max(1, len(text) // 4)

    async def handle_prompt(self, prompt_name: str, input_data: Any, variables: List[str], api_key: str):
        """Handle prompt execution and tracing"""
        self.logger.info(f"Handling prompt: {prompt_name}")
        try:
            # Convert input data to dictionary
            input_dict = {var: getattr(input_data, var) for var in variables}
            self.logger.debug(f"Input data for {prompt_name}: {input_dict}")

            self.logger.debug(f"Creating chain components for {prompt_name}")

            is_chat = self.prompt_config[prompt_name]["is_chat"]
            components = self._create_chain(prompt_name, is_chat=is_chat, api_key=api_key)

            # Create chain components
            if len(components) == 3:
                prompt, model, output_parser = components
                chain = prompt | model | output_parser
                # Handle various providers
                model_name, model_params = self._extract_model_info(model)
            else:
                prompt, model = components
                chain = prompt | model
                # Handle various providers
                model_name, model_params = self._extract_model_info_structured_output(model)

            # Create trace
            trace = self._create_trace(prompt_name, prompt, input_dict)

            # Record generation
            self.logger.debug(f"Recording generation for {prompt_name}")
            generation = self._record_generation(trace, prompt_name, model_name, model_params, prompt, input_dict)

            # Execute chain
            self.logger.debug(f"Executing chain for {prompt_name}")
            response = chain.invoke(input=input_dict)
            # Estimate usage for cost tracking in Langfuse
            try:
                formatted_input = prompt.format(**input_dict)
                output_text = response.content if hasattr(response, "content") else str(response)
                # Use CostTracker for usage + cost
                tracker = CostTracker(model_name)
                usage = tracker.compute_usage_and_cost(
                    input_messages=[formatted_input],
                    output_text=output_text,
                )
                generation.end(output=response, usage=usage)
            except Exception as usage_err:
                self.logger.warning(f"Failed to attach usage to generation: {str(usage_err)}")
                generation.end(output=response)
            trace.update(output=response)

            self.logger.info(f"Successfully processed prompt {prompt_name}. Trace URL: {trace.get_trace_url()}")

            return {"response": response} if len(components) == 3 else json.loads(response.content)

        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            filename, lineno, _, _ = tb[-1]
            self.logger.error(
                f"Error handling prompt {prompt_name} in {filename} at line {lineno}: {str(e)}"
            )
            raise HTTPException(status_code=500, detail=str(e))
