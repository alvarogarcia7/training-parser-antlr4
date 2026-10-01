"""Language Server Protocol implementation for the training language."""

import sys
from typing import Any, Optional

from lsprotocol.types import (
    TEXT_DOCUMENT_CODE_ACTION,
    TEXT_DOCUMENT_COMPLETION,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_SAVE,
    TEXT_DOCUMENT_FORMATTING,
    TEXT_DOCUMENT_HOVER,
    TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
    CodeAction,
    CodeActionParams,
    CompletionList,
    CompletionOptions,
    CompletionParams,
    DidChangeTextDocumentParams,
    DidOpenTextDocumentParams,
    DidSaveTextDocumentParams,
    DocumentFormattingParams,
    Hover,
    HoverParams,
    InitializeParams,
    InitializeResult,
    PublishDiagnosticsParams,
    SemanticTokens,
    SemanticTokensLegend,
    SemanticTokensParams,
    SemanticTokensRegistrationOptions,
    ServerCapabilities,
    TextDocumentSyncKind,
)
from pygls.lsp.server import LanguageServer

from .code_actions import get_code_actions
from .completion import get_completions
from .diagnostics import get_diagnostics
from .formatting import format_document
from .hover import get_hover_info
from .semantic_tokens import get_semantic_tokens, get_semantic_tokens_legend


class TrainingLanguageServer(LanguageServer):  # type: ignore
    """Language server for the training workout DSL."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__("training-lsp", "v0.1.0", *args, **kwargs)


# Create the language server instance
server: TrainingLanguageServer = TrainingLanguageServer()


@server.feature(TEXT_DOCUMENT_DID_OPEN)  # type: ignore
async def did_open(ls: TrainingLanguageServer, params: DidOpenTextDocumentParams) -> None:
    """Handle document open events."""
    text_doc = ls.workspace.get_text_document(params.text_document.uri)
    diagnostics = get_diagnostics(text_doc.source)
    ls.text_document_publish_diagnostics(PublishDiagnosticsParams(uri=text_doc.uri, diagnostics=diagnostics))


@server.feature(TEXT_DOCUMENT_DID_CHANGE)  # type: ignore
async def did_change(
    ls: TrainingLanguageServer, params: DidChangeTextDocumentParams
) -> None:
    """Handle document change events."""
    text_doc = ls.workspace.get_text_document(params.text_document.uri)
    diagnostics = get_diagnostics(text_doc.source)
    ls.text_document_publish_diagnostics(PublishDiagnosticsParams(uri=text_doc.uri, diagnostics=diagnostics))


@server.feature(TEXT_DOCUMENT_DID_SAVE)  # type: ignore
async def did_save(ls: TrainingLanguageServer, params: DidSaveTextDocumentParams) -> None:
    """Handle document save events."""
    text_doc = ls.workspace.get_text_document(params.text_document.uri)
    diagnostics = get_diagnostics(text_doc.source)
    ls.text_document_publish_diagnostics(PublishDiagnosticsParams(uri=text_doc.uri, diagnostics=diagnostics))


@server.feature(  # type: ignore
    TEXT_DOCUMENT_COMPLETION,
    CompletionOptions(trigger_characters=[":", " ", "\n"]),
)
async def completions(
    ls: TrainingLanguageServer, params: CompletionParams
) -> CompletionList:
    """Provide completion items."""
    text_doc = ls.workspace.get_text_document(params.text_document.uri)
    lines = text_doc.source.split("\n")

    line_num = params.position.line
    char_num = params.position.character

    current_line = lines[line_num] if line_num < len(lines) else ""
    items = get_completions(current_line, char_num)

    return CompletionList(is_incomplete=False, items=items)


@server.feature(TEXT_DOCUMENT_HOVER)  # type: ignore
async def hover(ls: TrainingLanguageServer, params: HoverParams) -> Optional[Hover]:
    """Provide hover information."""
    text_doc = ls.workspace.get_text_document(params.text_document.uri)
    return get_hover_info(text_doc.source, params.position.line, params.position.character)


@server.feature(TEXT_DOCUMENT_FORMATTING)  # type: ignore
async def formatting(
    ls: TrainingLanguageServer, params: DocumentFormattingParams
) -> list[Any]:
    """Format the document."""
    text_doc = ls.workspace.get_text_document(params.text_document.uri)
    return format_document(text_doc.source)


@server.feature(  # type: ignore
    TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
    SemanticTokensRegistrationOptions(
        legend=get_semantic_tokens_legend(),
        full=True,
    ),
)
async def semantic_tokens_full(
    ls: TrainingLanguageServer, params: SemanticTokensParams
) -> SemanticTokens:
    """Provide semantic tokens for syntax highlighting."""
    text_doc = ls.workspace.get_text_document(params.text_document.uri)
    return get_semantic_tokens(text_doc.source)


@server.feature(TEXT_DOCUMENT_CODE_ACTION)  # type: ignore
async def code_actions(
    ls: TrainingLanguageServer, params: CodeActionParams
) -> list[CodeAction]:
    """Provide code actions for quick fixes and refactorings."""
    text_doc = ls.workspace.get_text_document(params.text_document.uri)
    return get_code_actions(
        text_doc.uri,
        text_doc.source,
        params.range.start.line,
        params.range.start.character,
        params.range.end.character,
    )


def main() -> None:
    """Main entry point for the language server."""
    server.start_io()


if __name__ == "__main__":
    main()
