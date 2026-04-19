"""Tests for the LSP client."""

import asyncio
from typing import Any
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import pytest

from lsp.client import (
    LSPClient,
    LSPClientConfig,
    LSPClientError,
    LSPConnectionError,
    LSPServerError,
    LSPTimeoutError,
    LSPResponse,
)


class TestLSPClient:
    """Test LSP client functionality."""

    def test_client_initialization(self) -> None:
        """Test client initialization."""
        client = LSPClient()
        assert client.process is None
        assert client.is_initialized is False
        assert client.server_capabilities is None
        assert client.request_id == 0

    def test_client_initialization_with_config(self) -> None:
        """Test client initialization with custom config."""
        config = LSPClientConfig(
            server_command=["custom-lsp"],
            timeout=10.0,
            trace="verbose"
        )
        client = LSPClient(config)
        assert client.config.server_command == ["custom-lsp"]
        assert client.config.timeout == 10.0
        assert client.config.trace == "verbose"

    def test_next_request_id(self) -> None:
        """Test request ID generation."""
        client = LSPClient()
        assert client._next_request_id() == 1
        assert client._next_request_id() == 2
        assert client._next_request_id() == 3

    def test_diagnostics_cache_empty(self) -> None:
        """Test empty diagnostics cache."""
        client = LSPClient()
        diagnostics = client.get_diagnostics("file:///test.txt")
        assert diagnostics == []

    def test_diagnostics_cache_storage(self) -> None:
        """Test diagnostics cache storage."""
        client = LSPClient()
        test_diagnostics = [{"message": "test error"}]
        client.diagnostics_cache["file:///test.txt"] = test_diagnostics

        diagnostics = client.get_diagnostics("file:///test.txt")
        assert diagnostics == test_diagnostics

    def test_notification_handler_registration(self) -> None:
        """Test notification handler registration."""
        client = LSPClient()
        handler_called = []

        def handler(params: Any) -> None:
            handler_called.append(params)

        client.register_notification_handler("test/notification", handler)
        assert "test/notification" in client.notification_handlers

        # Simulate notification
        client.notification_handlers["test/notification"]({"test": "data"})
        assert len(handler_called) == 1
        assert handler_called[0] == {"test": "data"}

    @pytest.mark.asyncio
    async def test_handle_diagnostics_notification(self) -> None:
        """Test handling of diagnostics notifications."""
        client = LSPClient()

        params = {
            "uri": "file:///test.txt",
            "diagnostics": [{"message": "error"}]
        }

        await client._handle_message({
            "method": "textDocument/publishDiagnostics",
            "params": params
        })

        assert "file:///test.txt" in client.diagnostics_cache
        assert client.diagnostics_cache["file:///test.txt"] == [{"message": "error"}]

    @pytest.mark.asyncio
    async def test_handle_response_message(self) -> None:
        """Test handling of response messages."""
        client = LSPClient()

        # Create a pending request
        future: asyncio.Future[LSPResponse] = asyncio.Future()
        client.pending_responses[1] = future

        # Handle response
        await client._handle_message({
            "jsonrpc": "2.0",
            "id": 1,
            "result": {"key": "value"}
        })

        # Check future was resolved
        assert future.done()
        response = await future
        assert response.id == 1
        assert response.result == {"key": "value"}
        assert response.error is None

    @pytest.mark.asyncio
    async def test_handle_error_response(self) -> None:
        """Test handling of error responses."""
        client = LSPClient()

        # Create a pending request
        future: asyncio.Future[LSPResponse] = asyncio.Future()
        client.pending_responses[2] = future

        # Handle error response
        await client._handle_message({
            "jsonrpc": "2.0",
            "id": 2,
            "error": {"code": -32600, "message": "Invalid request"}
        })

        # Check future was resolved
        assert future.done()
        response = await future
        assert response.id == 2
        assert response.error == {"code": -32600, "message": "Invalid request"}
        assert response.result is None

    @pytest.mark.asyncio
    async def test_send_notification(self) -> None:
        """Test sending notifications."""
        client = LSPClient()

        # Mock the process
        client.process = Mock()
        client.process.stdin = Mock()
        client.process.stdin.write = Mock()
        client.process.stdin.flush = Mock()

        await client._send_notification("test/notification", {"param": "value"})

        # Verify write was called
        assert client.process.stdin.write.called
        assert client.process.stdin.flush.called

    @pytest.mark.asyncio
    async def test_invalid_server_command(self) -> None:
        """Test error handling with invalid server command."""
        config = LSPClientConfig(server_command=["nonexistent-command"])
        client = LSPClient(config)

        with pytest.raises(LSPConnectionError):
            await client.start()

    @pytest.mark.asyncio
    async def test_send_message_without_process(self) -> None:
        """Test sending message without started process."""
        client = LSPClient()

        with pytest.raises(LSPConnectionError):
            await client._send_message({"test": "message"})

    @pytest.mark.asyncio
    async def test_stop_without_process(self) -> None:
        """Test stopping client without started process."""
        client = LSPClient()

        # Should not raise error
        await client.stop()
        assert client.process is None

    def test_response_is_success(self) -> None:
        """Test LSPResponse success check."""
        response = LSPResponse(id=1, result={"key": "value"})
        assert response.is_success is True

        error_response = LSPResponse(id=1, error={"message": "error"})
        assert error_response.is_success is False

    def test_response_is_notification(self) -> None:
        """Test LSPResponse notification check."""
        notification = LSPResponse(method="test/notification", params={})
        assert notification.is_notification is True

        response = LSPResponse(id=1, result={})
        assert response.is_notification is False

    @pytest.mark.asyncio
    async def test_start_already_started(self) -> None:
        """Test starting client that's already started."""
        client = LSPClient()
        client.process = Mock()  # Simulate already started

        with pytest.raises(LSPClientError, match="Server already started"):
            await client.start()

    @pytest.mark.asyncio
    async def test_send_request_creates_future(self) -> None:
        """Test that send_request creates and tracks futures."""
        client = LSPClient()
        client.process = Mock()
        client.process.stdin = Mock()
        client.process.stdin.write = Mock()
        client.process.stdin.flush = Mock()

        # Start the request (will timeout)
        with pytest.raises(LSPTimeoutError):
            await client._send_request("test/method", {})

        # Future should have been created and removed after timeout
        assert len(client.pending_responses) == 0

    def test_config_defaults(self) -> None:
        """Test default configuration."""
        config = LSPClientConfig()
        assert config.server_command == ["training-lsp"]
        assert config.server_path is None
        assert config.workspace_path is None
        assert config.trace == "off"
        assert config.timeout == 5.0

    def test_config_custom(self) -> None:
        """Test custom configuration."""
        from pathlib import Path
        config = LSPClientConfig(
            server_command=["custom-lsp", "--arg"],
            server_path=Path("/custom/path"),
            trace="verbose",
            timeout=15.0
        )
        assert config.server_command == ["custom-lsp", "--arg"]
        assert config.server_path == Path("/custom/path")
        assert config.trace == "verbose"
        assert config.timeout == 15.0


class TestLSPClientConfig:
    """Test LSP client configuration."""

    def test_default_config(self) -> None:
        """Test default configuration."""
        config = LSPClientConfig()

        assert config.server_command == ["training-lsp"]
        assert config.server_path is None
        assert config.workspace_path is None
        assert config.trace == "off"
        assert config.timeout == 5.0

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = LSPClientConfig(
            server_command=["custom-lsp"],
            trace="verbose",
            timeout=10.0,
        )

        assert config.server_command == ["custom-lsp"]
        assert config.trace == "verbose"
        assert config.timeout == 10.0


class TestLSPResponse:
    """Test LSP response handling."""

    def test_response_success(self) -> None:
        """Test successful response."""
        response = LSPResponse(id=1, result={"key": "value"})

        assert response.is_success is True
        assert response.is_notification is False

    def test_response_error(self) -> None:
        """Test error response."""
        response = LSPResponse(
            id=1, error={"code": -32600, "message": "Invalid request"}
        )

        assert response.is_success is False
        assert response.is_notification is False

    def test_notification(self) -> None:
        """Test notification."""
        response = LSPResponse(method="textDocument/publishDiagnostics", params={})

        assert response.is_notification is True
        assert response.is_success is True
