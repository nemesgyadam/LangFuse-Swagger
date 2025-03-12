from fastapi import FastAPI, Security
from langfuse.client import Langfuse
from langfuse.callback import CallbackHandler
import os
import asyncio
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict
from src.models.api_models import RequestModelGenerator, ResponseModelGenerator
from src.services.prompt_handler import PromptHandler
from src.utils.langfuse_utils import get_prompt_variables, get_project_name
from src.utils.api_key import get_api_key


def setup_logging():
    """Configure logging with both file and console handlers"""
    # Get log level from environment variable, default to INFO
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Create a formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Set up file handler with rotation
    file_handler = RotatingFileHandler(
        filename=f'logs/app_{datetime.now().strftime("%Y%m%d")}.log',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # Set up console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))  # Set level from environment
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level: {log_level}")
    
    return root_logger

class PromptEndpointGenerator:
    def __init__(self):
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing PromptEndpointGenerator")
        
        load_dotenv()
        self.logger.debug("Environment variables loaded")
        
        # Initialize Langfuse client
        try:
            self.langfuse = Langfuse(
                public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
                secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
                host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
            )
            self.logger.info("Langfuse client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Langfuse client: {str(e)}")
            raise

        project_name = get_project_name(self.langfuse)
        self.logger.info(f"Project name retrieved: {project_name}")

        self.app = FastAPI(
            title=f"{project_name} API",
            description="API for using Langfuse prompts",
            version="1.0.0",
        )
        self.logger.info("FastAPI application initialized")

        self.callback_handler = CallbackHandler()
        
        # Process tags
        tags = os.getenv("LANGFUSE_TAGS", "").strip()
        tag_list = [tag.strip() for tag in tags.split(",")] if tags else None
        self.logger.info(f"Configured tags: {tag_list}")
        
        # Get prompt configuration
        try:
            self.prompt_config = get_prompt_variables(self.langfuse, tag=tag_list)
            self.logger.info(f"Retrieved {len(self.prompt_config)} prompt configurations")
        except Exception as e:
            self.logger.error(f"Failed to get prompt variables: {str(e)}")
            raise
            
        self.prompt_handler = PromptHandler(self.langfuse, self.prompt_config, self.logger)
        self._generate_endpoints()

    def _extract_api_key(self, input_data):
        """
        Extracts the API key from the given input data.

        Args:
            input_data (object): An object that may contain an `API_KEY` attribute.

        Returns:
            str or None: The extracted API key if present, otherwise None.
        """
        if hasattr(input_data, "API_KEY") and input_data.API_KEY:
            return input_data.API_KEY

    def _generate_endpoint_handler(self, prompt_name: str, variables: list):
        """Generate an endpoint handler for a specific prompt"""
        self.logger.debug(f"Generating endpoint handler for prompt: {prompt_name}")
        
        request_model = RequestModelGenerator.create_request_model(
            prompt_name, variables
        )
        self.logger.debug(f"Created request model for {prompt_name} with variables: {variables}")

        async def handler(input_data: request_model):
            self.logger.info(f"Handling request for prompt: {prompt_name}")
            api_key_info = self._extract_api_key(input_data)

            try:
                result = await self.prompt_handler.handle_prompt(
                    prompt_name, input_data, variables, api_key_info
                )
                self.logger.info(f"Successfully processed prompt: {prompt_name}")
                return result
            except Exception as e:
                self.logger.error(f"Error processing prompt {prompt_name}: {str(e)}")
                raise

        return handler

    def _generate_endpoints(self):
        """Generate endpoints for each prompt in the configuration"""
        self.logger.info("Starting endpoint generation process")

        async def get_description(prompt_name):
            self.logger.debug(f"Fetching description for prompt: {prompt_name}")
            try:
                description = await self.prompt_handler.run_prompt(
                    "prompts/extract_description.txt",
                    self.langfuse.get_prompt(prompt_name).prompt,
                    self.langfuse.get_prompt(prompt_name).config.get("model_name")
                )
                self.logger.debug(f"Retrieved description for {prompt_name}")
                return description
            except Exception as e:
                self.logger.error(f"Failed to get description for {prompt_name}: {str(e)}")
                raise

        # Create tasks for all descriptions
        description_tasks = [
            get_description(prompt_name) for prompt_name in self.prompt_config.keys()
        ]
        self.logger.info(f"Created {len(description_tasks)} description tasks")

        # Create event loop and run tasks
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            descriptions = loop.run_until_complete(asyncio.gather(*description_tasks))
            loop.close()
            self.logger.info("Successfully retrieved all prompt descriptions")
        except Exception as e:
            self.logger.error(f"Failed to retrieve prompt descriptions: {str(e)}")
            raise

        # Create endpoints using the descriptions
        for (prompt_name, meta_data), description in zip(
            self.prompt_config.items(), descriptions
        ):
            variables = meta_data["variables"]
            output_structure = self.langfuse.get_prompt(prompt_name).config.get("output_structure", None)
            self.logger.info(f"Creating endpoint for prompt: {prompt_name}")
            self.logger.debug(f"Description for {prompt_name}: {description[:100]}...")
            try:
                handler = self._generate_endpoint_handler(prompt_name, variables)

                # Register the endpoint
                self.app.post(
                    f"/prompt/{prompt_name.lower()}",
                    response_model=ResponseModelGenerator.create_response_model(prompt_name, output_structure),
                    summary=f"Compile a {prompt_name} prompt with variables: {', '.join(variables)}",
                    description=description,
                    tags=["Prompts"],
                    dependencies=[Security(get_api_key)],
                )(handler)
                self.logger.info(f"Successfully created endpoint for {prompt_name}")
            except Exception as e:
                self.logger.error(f"Failed to create endpoint for {prompt_name}: {str(e)}")
                raise

    def get_app(self):
        return self.app

# Initialize logging when the module is imported
logger = setup_logging()