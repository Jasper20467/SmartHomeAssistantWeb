"""
Unit tests for LineBotAI/services/agent_service.py

All external dependencies (LLM, LangGraph, HomeAssistantClient) are mocked so
no network calls are made.
"""
import os
import time
import pytest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Shared patch targets
# ---------------------------------------------------------------------------

_PATCH_LLM = "services.agent_service.ChatGoogleGenerativeAI"
_PATCH_REACT = "services.agent_service.create_react_agent"
_PATCH_HA = "services.agent_service.HomeAssistantClient"
_PATCH_TOOLS = "services.agent_service.create_tools"
_PATCH_MEMORY = "services.agent_service.MemorySaver"


@pytest.fixture
def agent_service(monkeypatch):
    """
    Return an AgentService instance with all external dependencies mocked.
    GEMINI_API_KEY is injected via monkeypatch so the warning branch is skipped.
    """
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-test")

    with patch(_PATCH_LLM), \
         patch(_PATCH_REACT) as mock_react, \
         patch(_PATCH_HA), \
         patch(_PATCH_TOOLS, return_value=[]), \
         patch(_PATCH_MEMORY):

        mock_react.return_value = MagicMock()
        from services.agent_service import AgentService
        service = AgentService("http://localhost:8000")
        yield service


# ---------------------------------------------------------------------------
# _thread_id / clear_history
# ---------------------------------------------------------------------------


class TestThreadId:
    def test_initial_thread_id_format(self, agent_service):
        assert agent_service._thread_id("user123") == "user123:0"

    def test_different_users_have_isolated_thread_ids(self, agent_service):
        assert agent_service._thread_id("alice") != agent_service._thread_id("bob")

    def test_same_user_same_thread_id(self, agent_service):
        assert agent_service._thread_id("alice") == agent_service._thread_id("alice")


class TestClearHistory:
    def test_changes_thread_id_for_target_user(self, agent_service):
        before = agent_service._thread_id("alice")
        agent_service.clear_history("alice")
        after = agent_service._thread_id("alice")
        assert before != after

    def test_does_not_affect_other_users(self, agent_service):
        bob_before = agent_service._thread_id("bob")
        agent_service.clear_history("alice")
        bob_after = agent_service._thread_id("bob")
        assert bob_before == bob_after

    def test_can_clear_multiple_times(self, agent_service):
        agent_service.clear_history("alice")
        agent_service.clear_history("alice")
        # version should be 2
        assert agent_service._thread_id("alice") == "alice:2"


# ---------------------------------------------------------------------------
# run()
# ---------------------------------------------------------------------------


class TestRun:
    def test_returns_last_message_content_from_string(self, agent_service):
        msg = MagicMock()
        msg.content = "Hello!"
        agent_service._agent.invoke.return_value = {"messages": [msg]}
        result = agent_service.run("Hi", "user1")
        assert result == "Hello!"

    def test_uses_correct_thread_id_in_config(self, agent_service):
        msg = MagicMock()
        msg.content = "OK"
        agent_service._agent.invoke.return_value = {"messages": [msg]}
        agent_service.run("Hi", "user1")

        _, kwargs = agent_service._agent.invoke.call_args
        config = kwargs.get("config") or agent_service._agent.invoke.call_args[0][1]
        assert config["configurable"]["thread_id"] == "user1:0"

    def test_returns_fallback_when_messages_empty(self, agent_service):
        agent_service._agent.invoke.return_value = {"messages": []}
        result = agent_service.run("Hi", "user1")
        assert "無法處理" in result or len(result) > 0

    def test_returns_error_message_on_exception(self, agent_service):
        agent_service._agent.invoke.side_effect = RuntimeError("boom")
        result = agent_service.run("Hi", "user1")
        assert "錯誤" in result or "抱歉" in result

    def test_message_isolation_between_users(self, agent_service):
        """Different users produce different thread_id configs."""
        msg = MagicMock()
        msg.content = "reply"
        agent_service._agent.invoke.return_value = {"messages": [msg]}

        agent_service.run("Hi", "alice")
        alice_config = agent_service._agent.invoke.call_args[1].get("config") or \
                       agent_service._agent.invoke.call_args[0][1]

        agent_service.run("Hi", "bob")
        bob_config = agent_service._agent.invoke.call_args[1].get("config") or \
                     agent_service._agent.invoke.call_args[0][1]

        assert alice_config["configurable"]["thread_id"] != bob_config["configurable"]["thread_id"]


# ---------------------------------------------------------------------------
# Memory TTL
# ---------------------------------------------------------------------------


class TestMemoryTTL:
    def test_default_ttl_is_one_day(self, agent_service):
        assert agent_service._memory_ttl == 86400

    def test_default_max_messages_is_30(self, agent_service):
        assert agent_service._max_messages == 30

    def test_ttl_read_from_env(self, monkeypatch):
        monkeypatch.setenv("AGENT_MEMORY_TTL_SECONDS", "3600")
        monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
        with patch(_PATCH_LLM), \
             patch(_PATCH_REACT) as mock_react, \
             patch(_PATCH_HA), \
             patch(_PATCH_TOOLS, return_value=[]), \
             patch(_PATCH_MEMORY):
            mock_react.return_value = MagicMock()
            from services.agent_service import AgentService
            svc = AgentService("http://localhost:8000")
        assert svc._memory_ttl == 3600

    def test_max_messages_read_from_env(self, monkeypatch):
        monkeypatch.setenv("AGENT_MAX_MESSAGES", "10")
        monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
        with patch(_PATCH_LLM), \
             patch(_PATCH_REACT) as mock_react, \
             patch(_PATCH_HA), \
             patch(_PATCH_TOOLS, return_value=[]), \
             patch(_PATCH_MEMORY):
            mock_react.return_value = MagicMock()
            from services.agent_service import AgentService
            svc = AgentService("http://localhost:8000")
        assert svc._max_messages == 10

    def test_pre_model_hook_trims_to_max_messages(self, monkeypatch):
        """pre_model_hook should return only the last max_messages messages."""
        monkeypatch.setenv("AGENT_MAX_MESSAGES", "3")
        monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
        captured_hook = {}

        def capture_react(*args, **kwargs):
            captured_hook["hook"] = kwargs.get("pre_model_hook")
            return MagicMock()

        with patch(_PATCH_LLM), \
             patch(_PATCH_REACT, side_effect=capture_react), \
             patch(_PATCH_HA), \
             patch(_PATCH_TOOLS, return_value=[]), \
             patch(_PATCH_MEMORY):
            from services.agent_service import AgentService
            AgentService("http://localhost:8000")

        hook = captured_hook["hook"]
        assert hook is not None

        messages = [MagicMock() for _ in range(5)]
        result = hook({"messages": messages})
        assert result == {"llm_input_messages": messages[-3:]}

    def test_pre_model_hook_keeps_all_when_under_limit(self, monkeypatch):
        """pre_model_hook should not drop messages when count <= max."""
        monkeypatch.setenv("AGENT_MAX_MESSAGES", "10")
        monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
        captured_hook = {}

        def capture_react(*args, **kwargs):
            captured_hook["hook"] = kwargs.get("pre_model_hook")
            return MagicMock()

        with patch(_PATCH_LLM), \
             patch(_PATCH_REACT, side_effect=capture_react), \
             patch(_PATCH_HA), \
             patch(_PATCH_TOOLS, return_value=[]), \
             patch(_PATCH_MEMORY):
            from services.agent_service import AgentService
            AgentService("http://localhost:8000")

        hook = captured_hook["hook"]
        messages = [MagicMock() for _ in range(4)]
        result = hook({"messages": messages})
        assert result == {"llm_input_messages": messages}

    def test_expired_activity_bumps_thread_version(self, agent_service):
        # Simulate activity that happened longer ago than the TTL.
        agent_service._last_activity["alice"] = time.time() - agent_service._memory_ttl - 1
        version_before = agent_service._thread_versions.get("alice", 0)
        agent_service._thread_id("alice")
        version_after = agent_service._thread_versions.get("alice", 0)
        assert version_after == version_before + 1

    def test_expired_activity_clears_last_activity(self, agent_service):
        agent_service._last_activity["alice"] = time.time() - agent_service._memory_ttl - 1
        agent_service._thread_id("alice")
        assert "alice" not in agent_service._last_activity

    def test_recent_activity_keeps_thread_version(self, agent_service):
        agent_service._last_activity["alice"] = time.time() - 10
        version_before = agent_service._thread_versions.get("alice", 0)
        agent_service._thread_id("alice")
        assert agent_service._thread_versions.get("alice", 0) == version_before

    def test_run_updates_last_activity(self, agent_service):
        msg = MagicMock()
        msg.content = "OK"
        agent_service._agent.invoke.return_value = {"messages": [msg]}
        before = time.time()
        agent_service.run("Hi", "alice")
        assert "alice" in agent_service._last_activity
        assert agent_service._last_activity["alice"] >= before


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------


class TestAgentServiceInit:
    def test_logs_warning_when_api_key_missing(self, monkeypatch, caplog):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        import logging
        with patch(_PATCH_LLM), \
             patch(_PATCH_REACT) as mock_react, \
             patch(_PATCH_HA), \
             patch(_PATCH_TOOLS, return_value=[]), \
             patch(_PATCH_MEMORY):
            mock_react.return_value = MagicMock()
            from services.agent_service import AgentService
            with caplog.at_level(logging.WARNING, logger="services.agent_service"):
                AgentService("http://localhost:8000")
        assert any("GEMINI_API_KEY" in r.message for r in caplog.records)
