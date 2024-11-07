from fastapi import FastAPI, Security
from langfuse.client import Langfuse
from langfuse.callback import CallbackHandler
import os
import asyncio
from dotenv import load_dotenv
from typing import Dict
from src.models.api_models import RequestModelGenerator, ResponseModel
from src.services.prompt_handler import PromptHandler
from src.utils.langfuse_utils import get_prompt_variables, get_project_name
from src.utils.api_key import get_api_key


class PromptEndpointGenerator:
    def __init__(self):
        load_dotenv()
        self.langfuse = Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
        )

        project_name = get_project_name(self.langfuse)

        self.app = FastAPI(
            title=f"{project_name} API",
            description="API for using Langfuse prompts",
            version="1.0.0",
        )

        self.callback_handler = CallbackHandler()

        tags = os.getenv("LANGFUSE_TAGS", "").strip()
        tag_list = [tag.strip() for tag in tags.split(",")] if tags else None
        print(f"Tag list: {tag_list}")
        self.prompt_config = get_prompt_variables(self.langfuse, tag=tag_list)
        self.prompt_handler = PromptHandler(self.langfuse, self.prompt_config)
        self._generate_endpoints()

    def _generate_endpoint_handler(self, prompt_name: str, variables: list):
        """Generate an endpoint handler for a specific prompt"""
        request_model = RequestModelGenerator.create_request_model(
            prompt_name, variables
        )

        async def handler(input_data: request_model):
            return await self.prompt_handler.handle_prompt(
                prompt_name, input_data, variables
            )

        return handler

    def _generate_endpoints(self):
        """Generate endpoints for each prompt in the configuration"""

        async def get_description(prompt_name):
            print(f"Getting description for {prompt_name}")
            return await self.prompt_handler.run_prompt(
                "prompts/extract_description.txt",
                self.langfuse.get_prompt(prompt_name).prompt,
            )

        # Create tasks for all descriptions
        description_tasks = [
            get_description(prompt_name) for prompt_name in self.prompt_config.keys()
        ]

        # Create event loop and run tasks
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        descriptions = loop.run_until_complete(asyncio.gather(*description_tasks))
        loop.close()

        # Create endpoints using the descriptions
        for (prompt_name, meta_data), description in zip(
            self.prompt_config.items(), descriptions
        ):
            variables = meta_data["variables"]
            print(f"Description for {prompt_name}: {description[:100]}...")

            # Create the endpoint handler
            handler = self._generate_endpoint_handler(prompt_name, variables)

            # Register the endpoint
            self.app.post(
                f"/prompt/{prompt_name.lower()}",
                response_model=ResponseModel,
                summary=f"Compile a {prompt_name} prompt with variables: {', '.join(variables)}",
                description=description,
                tags=["Prompts"],
                dependencies=[Security(get_api_key)],
            )(handler)

    def get_app(self):
        return self.app
