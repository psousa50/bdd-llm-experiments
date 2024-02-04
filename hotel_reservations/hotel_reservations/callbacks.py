import logging
from typing import Any, Dict, List

from langchain.callbacks.base import BaseCallbackHandler

logger = logging.getLogger(__name__)


class LLMStartHandler(BaseCallbackHandler):
    def __init__(self) -> None:
        super().__init__()
        self.prompt = None

    from langchain_core.messages import BaseMessage

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> Any:
        """Run when LLM starts running."""
        logger.info(f"on_llm_start: {prompts}")

    def on_chat_model_start(
        self,
        serialized: Dict[str, Any],
        messages: List[List[BaseMessage]],
        **kwargs: Any,
    ) -> Any:
        """Run when Chat Model starts running."""
        logger.debug(f"on_chat_model_start: {messages}")

    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> Any:
        """Run when tool starts running."""
        logger.info(f"on_tool_start - serialized: {serialized}")
        logger.info(f"on_tool_start - input_str: {input_str}")
        logger.info(f"on_tool_start - kwargs: {kwargs}")
