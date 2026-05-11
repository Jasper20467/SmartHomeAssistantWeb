"""
Unit tests for LineBotAI/services/line_service.py

AgentService and requests.post are mocked so no real LLM or LINE API calls
are made.
"""
import pytest
from unittest.mock import MagicMock, patch


_PATCH_AGENT = "services.line_service.AgentService"
_PATCH_REQUESTS = "services.line_service.requests.post"


@pytest.fixture
def mock_agent():
    return MagicMock()


@pytest.fixture
def line_service(mock_agent):
    """
    Return a LineService with AgentService patched out.
    The mock_agent is stored on service.agent_service so tests can configure it.
    """
    with patch(_PATCH_AGENT, return_value=mock_agent):
        from services.line_service import LineService
        svc = LineService("fake-token", "http://localhost:8000")
    return svc


@pytest.fixture
def line_service_no_backend():
    """LineService initialised without a backend_url → agent_service is None."""
    with patch(_PATCH_AGENT) as mock_cls:
        from services.line_service import LineService
        svc = LineService("fake-token")
    # No backend_url means agent_service should be None
    assert svc.agent_service is None
    return svc


# ---------------------------------------------------------------------------
# __init__
# ---------------------------------------------------------------------------


class TestLineServiceInit:
    def test_creates_agent_service_when_backend_url_given(self, line_service):
        assert line_service.agent_service is not None

    def test_no_agent_service_when_no_backend_url(self, line_service_no_backend):
        assert line_service_no_backend.agent_service is None


# ---------------------------------------------------------------------------
# process_user_message
# ---------------------------------------------------------------------------


class TestProcessUserMessage:
    def test_calls_agent_run_and_replies(self, line_service, mock_agent):
        mock_agent.run.return_value = "行程已建立！"

        with patch(_PATCH_REQUESTS) as mock_post:
            mock_post.return_value = MagicMock(status_code=200)
            mock_post.return_value.raise_for_status = MagicMock()
            line_service.process_user_message("建立行程", "reply-token-1", user_id="user1")

        mock_agent.run.assert_called_once_with("建立行程", "user1")

        call_args = mock_post.call_args
        sent_text = call_args[1]["json"]["messages"][0]["text"]
        assert sent_text == "行程已建立！"

    def test_uses_anonymous_when_user_id_none(self, line_service, mock_agent):
        mock_agent.run.return_value = "OK"

        with patch(_PATCH_REQUESTS) as mock_post:
            mock_post.return_value = MagicMock(status_code=200)
            mock_post.return_value.raise_for_status = MagicMock()
            line_service.process_user_message("Hi", "reply-token-2", user_id=None)

        mock_agent.run.assert_called_once_with("Hi", "anonymous")

    def test_replies_error_message_on_exception(self, line_service, mock_agent):
        mock_agent.run.side_effect = RuntimeError("boom")

        with patch(_PATCH_REQUESTS) as mock_post:
            mock_post.return_value = MagicMock(status_code=200)
            mock_post.return_value.raise_for_status = MagicMock()
            line_service.process_user_message("Hi", "reply-token-3", user_id="user1")

        sent_text = mock_post.call_args[1]["json"]["messages"][0]["text"]
        assert "錯誤" in sent_text or "抱歉" in sent_text

    def test_replies_init_error_when_no_agent(self, line_service_no_backend):
        with patch(_PATCH_REQUESTS) as mock_post:
            mock_post.return_value = MagicMock(status_code=200)
            mock_post.return_value.raise_for_status = MagicMock()
            line_service_no_backend.process_user_message("Hi", "reply-token-4", user_id="user1")

        sent_text = mock_post.call_args[1]["json"]["messages"][0]["text"]
        assert len(sent_text) > 0


# ---------------------------------------------------------------------------
# reply_to_line
# ---------------------------------------------------------------------------


class TestReplyToLine:
    def test_sends_correct_payload(self, line_service):
        with patch(_PATCH_REQUESTS) as mock_post:
            mock_post.return_value = MagicMock(status_code=200)
            mock_post.return_value.raise_for_status = MagicMock()
            line_service.reply_to_line("token-abc", "Hello")

        _, kwargs = mock_post.call_args
        assert kwargs["json"]["replyToken"] == "token-abc"
        assert kwargs["json"]["messages"][0]["text"] == "Hello"
        assert "Bearer fake-token" in kwargs["headers"]["Authorization"]

    def test_handles_request_exception_gracefully(self, line_service):
        with patch(_PATCH_REQUESTS, side_effect=Exception("network error")):
            # Should not raise
            line_service.reply_to_line("token-xyz", "Hello")
