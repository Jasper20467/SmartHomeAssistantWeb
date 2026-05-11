"""
Agent Service

Provides a LangGraph ReAct Agent backed by Google Gemini.
Each LINE user gets an isolated conversation thread via MemorySaver.
"""
import os
import time
import logging
from typing import Dict

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from Home_assistant.client import HomeAssistantClient
from agent.tools import create_tools
from agent.prompts import get_system_prompt


class AgentService:
    """
    Wraps a LangGraph ReAct Agent for use by LineService.

    Each user_id maps to an independent LangGraph thread_id so that
    conversation history is fully isolated between users.
    """

    def __init__(self, backend_url: str):
        """
        Initialize the AgentService.

        Args:
            backend_url: Base URL of the Smart Home Assistant backend API
                         (e.g. "http://backend:8000").
        """
        self.logger = logging.getLogger(__name__)

        # --- LLM ---
        api_key = os.getenv("GEMINI_API_KEY", "")
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

        if not api_key:
            self.logger.warning("GEMINI_API_KEY is not set; Agent calls will fail.")

        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0,
        )

        # --- Tools ---
        ha_client = HomeAssistantClient(backend_url)
        tools = create_tools(ha_client)

        # --- Memory (per-thread, in-process) ---
        self._memory = MemorySaver()

        # --- Message trimming hook ---
        max_messages = int(os.getenv("AGENT_MAX_MESSAGES", "30"))

        def _pre_model_hook(state: dict) -> dict:
            """Keep only the most recent max_messages before calling the LLM."""
            msgs = state.get("messages", [])
            return {"llm_input_messages": msgs[-max_messages:]}

        # --- Agent graph ---
        self._agent = create_react_agent(
            model=llm,
            tools=tools,
            checkpointer=self._memory,
            prompt=get_system_prompt(),
            pre_model_hook=_pre_model_hook,
        )

        # version counter — incrementing it creates a new thread, effectively
        # clearing history for that user without touching other users' threads.
        self._thread_versions: Dict[str, int] = {}

        # Memory TTL: auto-expire conversation history after N seconds of inactivity.
        self._memory_ttl: int = int(os.getenv("AGENT_MEMORY_TTL_SECONDS", "86400"))
        self._last_activity: Dict[str, float] = {}
        self._max_messages: int = max_messages

        self.logger.info(
            "AgentService initialized with model=%s backend=%s tools=%d max_messages=%d ttl=%ds",
            model_name,
            backend_url,
            len(tools),
            max_messages,
            self._memory_ttl,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, user_message: str, user_id: str) -> str:
        """
        Process a user message and return the agent's reply.

        Args:
            user_message: The text message sent by the LINE user.
            user_id: The LINE user ID, used to maintain per-user conversation history.

        Returns:
            The agent's reply as a plain string.
        """
        config = {"configurable": {"thread_id": self._thread_id(user_id)}}
        try:
            result = self._agent.invoke(
                {"messages": [{"role": "user", "content": user_message}]},
                config=config,
            )
            # The last message in the list is the assistant's final reply.
            messages = result.get("messages", [])
            if messages:
                last = messages[-1]
                # LangChain message objects expose .content; dicts use "content" key.
                self._last_activity[user_id] = time.time()
                return last.content if hasattr(last, "content") else last.get("content", "")
            return "抱歉，我無法處理您的請求。"
        except Exception as e:
            self.logger.error("AgentService.run error for user %s: %s", user_id, e)
            return "抱歉，處理您的請求時發生錯誤，請稍後再試。"

    def clear_history(self, user_id: str) -> None:
        """
        Clear the conversation history for a specific user.

        Implemented by bumping the thread version so the next run starts
        a fresh LangGraph thread while existing threads remain intact.

        Args:
            user_id: The LINE user ID whose history should be cleared.
        """
        self._thread_versions[user_id] = self._thread_versions.get(user_id, 0) + 1
        self.logger.info("Cleared history for user %s (new thread version: %d)",
                         user_id, self._thread_versions[user_id])

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _thread_id(self, user_id: str) -> str:
        """Return the current LangGraph thread ID for a given user.

        If the user's last activity exceeds AGENT_MEMORY_TTL_SECONDS, the
        thread version is bumped automatically to clear stale history.
        """
        last = self._last_activity.get(user_id)
        if last is not None and (time.time() - last) > self._memory_ttl:
            self._thread_versions[user_id] = self._thread_versions.get(user_id, 0) + 1
            del self._last_activity[user_id]
            self.logger.info(
                "Memory TTL expired for user %s, cleared history (new thread version: %d)",
                user_id, self._thread_versions[user_id],
            )
        version = self._thread_versions.get(user_id, 0)
        return f"{user_id}:{version}"
