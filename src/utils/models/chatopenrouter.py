from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from typing import Optional
from pydantic import Field, SecretStr
from langchain_core.utils.utils import secret_from_env


class ChatOpenRouter(ChatOpenAI):
    openai_api_key: Optional[SecretStr] = Field(
        alias="api_key",
        default_factory=secret_from_env("OPENROUTER_API_KEY", default=None),
    )

    @property
    def lc_secrets(self) -> dict[str, str]:
        return {"openai_api_key": "OPENROUTER_API_KEY"}

    def __init__(self, openai_api_key: Optional[str] = None, **kwargs):
        openai_api_key = (openai_api_key or os.environ.get("OPENROUTER_API_KEY"))
        openai_api_base = os.environ.get("OPENROUTER_API_BASE")
        super().__init__(
            base_url=openai_api_base,
            openai_api_key=openai_api_key,
            **kwargs
        )
