"""LSP client for testing and validating the training language server."""

import asyncio
import json
import subprocess
import sys
from typing import Any, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path

from lsprotocol.types import (
    ClientCapabilities,
    CompletionParams,
    DidChangeTextDocumentParams,
    DidCloseTextDocumentParams,
    DidOpenTextDocumentParams,
    DidSaveTextDocumentParams,
    DocumentFormattingParams,
    FormattingOptions,
    HoverParams,
    InitializeParams,
    Position,
    PublishDiagnosticsParams,
    SemanticTokensParams,
    TextDocumentContentChangeEvent,
    TextDocumentIdentifier,
    TextDocumentItem,
    VersionedTextDocumentIdentifier,
    WorkspaceFolder,
)


@dataclass
class LSPResponse:
    """Represents an LSP response."""

    id: Optional[int] = None
    result: Optional[Any] = None
    error: Optional[dict[str, Any]] = None
    method: Optional[str] = None
    params: Optional[Any] = None

    @property
    def is_success(self) -> bool:
        """Check if response is successful."""
        return self.error is None

    @property
    def is_notification(self) -> bool:
        """Check if this is a notification (no id)."""
        return self.id is None and self.method is not None


@dataclass
class LSPClientConfig:
    """Configuration for LSP client."""

    server_command: list[str] = field(default_factory=lambda: ["training-lsp"])
    server_path: Optional[Path] = None
    workspace_path: Optional[Path] = None
    trace: str = "off"  # off, messages, verbose
    timeout: float = 5.0


class LSPClientError(Exception):
    """Base exception for LSP client errors."""
    pass


class LSPConnectionError(LSPClientError):
    """Error connecting to LSP server."""
    pass


class LSPServerError(LSPClientError):
    """Error from LSP server."""
    pass


class LSPTimeoutError(LSPClientError):
    """Timeout waiting for LSP response."""
    pass


class LSPClient:
    """Client for interacting with the training language server."""

    def __init__(self, config: Optional[LSPClientConfig] = None) -> None:
        """Initialize the LSP client.

        Args:
            config: Client configuration. Uses defaults if not provided.
        """
        self.config = config or LSPClientConfig()
        self.process: Optional[subprocess.Popen[bytes]] = None
        self.request_id = 0
        self.is_initialized = False
        self.server_capabilities: Optional[dict[str, Any]] = None
        self.pending_responses: dict[int, asyncio.Future[LSPResponse]] = {}
        self.notification_handlers: dict[str, Callable[[Any], None]] = {}
        self.diagnostics_cache: dict[str, list[Any]] = {}

    async def start(self) -> None:
        """Start the LSP server process."""
        if self.process is not None:
            raise LSPClientError("Server already started")

        try:
            self.process = subprocess.Popen(
                self.config.server_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except FileNotFoundError as e:
            raise LSPConnectionError(
                f"Failed to start server: {self.config.server_command[0]} not found"
            ) from e
        except Exception as e:
            raise LSPConnectionError(f"Failed to start server: {e}") from e

        # Start reading responses
        asyncio.create_task(self._read_responses())

    async def stop(self) -> None:
        """Stop the LSP server process."""
        if self.process is not None:
            self.process.terminate()
            try:
                await asyncio.wait_for(
                    asyncio.to_thread(self.process.wait),
                    timeout=2.0
                )
            except asyncio.TimeoutError:
                self.process.kill()
                await asyncio.to_thread(self.process.wait)

            self.process = None
            self.is_initialized = False
            self.server_capabilities = None

    def _next_request_id(self) -> int:
        """Get next request ID."""
        self.request_id += 1
        return self.request_id

    async def _send_message(self, message: dict[str, Any]) -> None:
        """Send a JSON-RPC message to the server."""
        if self.process is None or self.process.stdin is None:
            raise LSPConnectionError("Server not started")

        content = json.dumps(message)
        header = f"Content-Length: {len(content)}\r\n\r\n"

        try:
            self.process.stdin.write(header.encode("utf-8"))
            self.process.stdin.write(content.encode("utf-8"))
            self.process.stdin.flush()
        except Exception as e:
            raise LSPConnectionError(f"Failed to send message: {e}") from e

    async def _read_responses(self) -> None:
        """Read responses from the server."""
        if self.process is None or self.process.stdout is None:
            return

        while self.process.poll() is None:
            try:
                # Read header
                headers: dict[str, str] = {}
                while True:
                    line_bytes = await asyncio.to_thread(self.process.stdout.readline)
                    if not line_bytes:
                        return

                    line = line_bytes.decode("utf-8").strip()
                    if not line:
                        break

                    key, value = line.split(":", 1)
                    headers[key.strip()] = value.strip()

                # Read content
                content_length = int(headers.get("Content-Length", "0"))
                if content_length == 0:
                    continue

                content = await asyncio.to_thread(
                    self.process.stdout.read, content_length
                )

                if not content:
                    return

                # Parse JSON
                message = json.loads(content.decode("utf-8"))

                # Handle message
                await self._handle_message(message)

            except Exception as e:
                if self.process and self.process.poll() is None:
                    print(f"Error reading response: {e}", file=sys.stderr)
                return

    async def _handle_message(self, message: dict[str, Any]) -> None:
        """Handle a message from the server."""
        # Check if it's a response to a request
        if "id" in message and message["id"] in self.pending_responses:
            response = LSPResponse(
                id=message["id"],
                result=message.get("result"),
                error=message.get("error"),
            )
            future = self.pending_responses.pop(message["id"])
            future.set_result(response)

        # Check if it's a notification
        elif "method" in message and "id" not in message:
            method = message["method"]
            params = message.get("params")

            # Handle diagnostics notifications
            if method == "textDocument/publishDiagnostics":
                self._handle_diagnostics(params)

            # Call registered handler
            if method in self.notification_handlers:
                self.notification_handlers[method](params)

    def _handle_diagnostics(self, params: Any) -> None:
        """Handle diagnostics notification."""
        if params and "uri" in params:
            self.diagnostics_cache[params["uri"]] = params.get("diagnostics", [])

    async def _send_request(
        self, method: str, params: Any = None
    ) -> LSPResponse:
        """Send a request and wait for response."""
        request_id = self._next_request_id()
        message = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {},
        }

        # Create future for response
        future: asyncio.Future[LSPResponse] = asyncio.Future()
        self.pending_responses[request_id] = future

        # Send request
        await self._send_message(message)

        # Wait for response with timeout
        try:
            response = await asyncio.wait_for(future, timeout=self.config.timeout)

            if response.error:
                raise LSPServerError(
                    f"{method} failed: {response.error.get('message', 'Unknown error')}"
                )

            return response
        except asyncio.TimeoutError as e:
            self.pending_responses.pop(request_id, None)
            raise LSPTimeoutError(f"Timeout waiting for {method} response") from e

    async def _send_notification(self, method: str, params: Any = None) -> None:
        """Send a notification (no response expected)."""
        message = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
        }
        await self._send_message(message)

    def register_notification_handler(
        self, method: str, handler: Callable[[Any], None]
    ) -> None:
        """Register a handler for notifications."""
        self.notification_handlers[method] = handler

    async def initialize(
        self,
        root_uri: Optional[str] = None,
        workspace_folders: Optional[list[WorkspaceFolder]] = None,
    ) -> dict[str, Any]:
        """Initialize the language server.

        Args:
            root_uri: Root URI of the workspace
            workspace_folders: Workspace folders

        Returns:
            Server capabilities
        """
        if self.process is None:
            await self.start()

        params = InitializeParams(
            process_id=None,
            root_uri=root_uri,
            workspace_folders=workspace_folders,
            capabilities=ClientCapabilities(),
            trace=self.config.trace,
        )

        response = await self._send_request("initialize", params)

        if response.result:
            self.server_capabilities = response.result.get("capabilities", {})
            self.is_initialized = True

            # Send initialized notification
            await self._send_notification("initialized", {})

            return self.server_capabilities

        raise LSPServerError("Initialize failed: no capabilities returned")

    async def shutdown(self) -> None:
        """Shutdown the language server."""
        await self._send_request("shutdown")
        await self._send_notification("exit")

    async def open_document(
        self, uri: str, language_id: str, version: int, text: str
    ) -> None:
        """Open a text document.

        Args:
            uri: Document URI
            language_id: Language identifier (e.g., "training")
            version: Document version
            text: Document content
        """
        params = DidOpenTextDocumentParams(
            text_document=TextDocumentItem(
                uri=uri, language_id=language_id, version=version, text=text
            )
        )
        await self._send_notification("textDocument/didOpen", params)

        # Give server time to process and send diagnostics
        await asyncio.sleep(0.1)

    async def change_document(
        self, uri: str, version: int, text: str
    ) -> None:
        """Change a text document.

        Args:
            uri: Document URI
            version: New document version
            text: New document content
        """
        params = DidChangeTextDocumentParams(
            text_document=VersionedTextDocumentIdentifier(uri=uri, version=version),
            content_changes=[
                TextDocumentContentChangeEvent(text=text)
            ],
        )
        await self._send_notification("textDocument/didChange", params)

        # Give server time to process and send diagnostics
        await asyncio.sleep(0.1)

    async def save_document(self, uri: str, text: Optional[str] = None) -> None:
        """Save a text document.

        Args:
            uri: Document URI
            text: Optional document content
        """
        params = DidSaveTextDocumentParams(
            text_document=TextDocumentIdentifier(uri=uri),
            text=text,
        )
        await self._send_notification("textDocument/didSave", params)

        # Give server time to process and send diagnostics
        await asyncio.sleep(0.1)

    async def close_document(self, uri: str) -> None:
        """Close a text document.

        Args:
            uri: Document URI
        """
        params = DidCloseTextDocumentParams(
            text_document=TextDocumentIdentifier(uri=uri)
        )
        await self._send_notification("textDocument/didClose", params)

    async def completion(
        self, uri: str, line: int, character: int
    ) -> list[Any]:
        """Request completion items.

        Args:
            uri: Document URI
            line: Line number (0-based)
            character: Character position (0-based)

        Returns:
            Completion items
        """
        params = CompletionParams(
            text_document=TextDocumentIdentifier(uri=uri),
            position=Position(line=line, character=character),
        )

        response = await self._send_request("textDocument/completion", params)

        if response.result:
            items: list[Any] = response.result.get("items", [])
            return items

        return []

    async def hover(
        self, uri: str, line: int, character: int
    ) -> Optional[dict[str, Any]]:
        """Request hover information.

        Args:
            uri: Document URI
            line: Line number (0-based)
            character: Character position (0-based)

        Returns:
            Hover information or None
        """
        params = HoverParams(
            text_document=TextDocumentIdentifier(uri=uri),
            position=Position(line=line, character=character),
        )

        response = await self._send_request("textDocument/hover", params)
        return response.result

    async def formatting(
        self, uri: str, tab_size: int = 4, insert_spaces: bool = True
    ) -> list[Any]:
        """Request document formatting.

        Args:
            uri: Document URI
            tab_size: Tab size
            insert_spaces: Use spaces instead of tabs

        Returns:
            Text edits
        """
        params = DocumentFormattingParams(
            text_document=TextDocumentIdentifier(uri=uri),
            options=FormattingOptions(
                tab_size=tab_size, insert_spaces=insert_spaces
            ),
        )

        response = await self._send_request("textDocument/formatting", params)
        return response.result or []

    async def semantic_tokens(self, uri: str) -> Optional[dict[str, Any]]:
        """Request semantic tokens.

        Args:
            uri: Document URI

        Returns:
            Semantic tokens or None
        """
        params = SemanticTokensParams(
            text_document=TextDocumentIdentifier(uri=uri)
        )

        response = await self._send_request(
            "textDocument/semanticTokens/full", params
        )
        return response.result

    def get_diagnostics(self, uri: str) -> list[Any]:
        """Get cached diagnostics for a document.

        Args:
            uri: Document URI

        Returns:
            List of diagnostics
        """
        return self.diagnostics_cache.get(uri, [])

    async def verify_connection(self) -> bool:
        """Verify connection to the server.

        Returns:
            True if server is responsive
        """
        try:
            if not self.is_initialized:
                await self.initialize()
            return True
        except Exception:
            return False

    async def verify_source_parsing(self, source: str) -> dict[str, Any]:
        """Verify that source code can be parsed.

        Args:
            source: Source code to parse

        Returns:
            Dictionary with parsing results including errors
        """
        uri = "file:///test/verify.training"

        # Open document with source
        await self.open_document(uri, "training", 1, source)

        # Get diagnostics
        diagnostics = self.get_diagnostics(uri)

        # Close document
        await self.close_document(uri)

        return {
            "source": source,
            "diagnostics": diagnostics,
            "has_errors": len(diagnostics) > 0,
            "error_count": len(diagnostics),
        }

    async def verify_all_features(self, source: str) -> dict[str, Any]:
        """Verify all LSP features with given source.

        Args:
            source: Source code to test

        Returns:
            Dictionary with all feature verification results
        """
        uri = "file:///test/verify_all.training"

        results: dict[str, Any] = {
            "source": source,
            "features": {},
        }

        # Open document
        await self.open_document(uri, "training", 1, source)

        # Test diagnostics
        diagnostics = self.get_diagnostics(uri)
        results["features"]["diagnostics"] = {
            "supported": True,
            "count": len(diagnostics),
            "items": diagnostics,
        }

        # Test completion
        try:
            completions = await self.completion(uri, 0, 0)
            results["features"]["completion"] = {
                "supported": True,
                "count": len(completions),
                "sample": completions[:3] if completions else [],
            }
        except Exception as e:
            results["features"]["completion"] = {
                "supported": False,
                "error": str(e),
            }

        # Test hover
        try:
            hover_result = await self.hover(uri, 0, 5)
            results["features"]["hover"] = {
                "supported": True,
                "has_content": hover_result is not None,
                "content": hover_result,
            }
        except Exception as e:
            results["features"]["hover"] = {
                "supported": False,
                "error": str(e),
            }

        # Test formatting
        try:
            edits = await self.formatting(uri)
            results["features"]["formatting"] = {
                "supported": True,
                "edit_count": len(edits),
                "edits": edits,
            }
        except Exception as e:
            results["features"]["formatting"] = {
                "supported": False,
                "error": str(e),
            }

        # Test semantic tokens
        try:
            tokens = await self.semantic_tokens(uri)
            results["features"]["semantic_tokens"] = {
                "supported": True,
                "has_tokens": tokens is not None,
                "token_count": len(tokens.get("data", [])) if tokens else 0,
            }
        except Exception as e:
            results["features"]["semantic_tokens"] = {
                "supported": False,
                "error": str(e),
            }

        # Close document
        await self.close_document(uri)

        return results

    async def __aenter__(self) -> "LSPClient":
        """Context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        try:
            if self.is_initialized:
                await self.shutdown()
        except Exception:
            pass
        finally:
            await self.stop()
