"""Command-line interface for testing LSP features without an editor."""

import asyncio
import json
import sys
from typing import Any, Optional

import click

from lsp.diagnostics import get_diagnostics
from lsp.completion import get_completions
from lsp.hover import get_hover_info
from lsp.formatting import format_document
from lsp.client import LSPClient, LSPClientConfig


@click.group()  # type: ignore
def cli() -> None:
    """Training Language Server CLI - Test LSP features from the command line."""
    pass


@cli.command()  # type: ignore
@click.argument("file", type=click.File("r"))  # type: ignore
def check(file: Any) -> None:
    """Check a training file for syntax errors."""
    text = file.read()
    diagnostics = get_diagnostics(text)

    if not diagnostics:
        click.echo(click.style("✓ No errors found!", fg="green"))
        sys.exit(0)

    click.echo(click.style(f"✗ Found {len(diagnostics)} error(s):", fg="red"))
    for diag in diagnostics:
        line = diag.range.start.line + 1  # Convert to 1-based
        col = diag.range.start.character + 1
        click.echo(f"  Line {line}, Col {col}: {diag.message}")
    sys.exit(1)


@cli.command()  # type: ignore
@click.argument("file", type=click.File("r"))  # type: ignore
@click.option("--output", "-o", type=click.File("w"), help="Output file (default: stdout)")  # type: ignore
def format(file: Any, output: Optional[Any]) -> None:
    """Format a training file."""
    text = file.read()
    edits = format_document(text)

    if not edits:
        click.echo("No formatting needed - file is already formatted.")
        if output:
            output.write(text)
        else:
            click.echo(text)
        return

    # Apply edits to text
    lines = text.split("\n")
    for edit in reversed(edits):  # Apply in reverse to maintain positions
        start_line = edit.range.start.line
        end_line = edit.range.end.line

        if start_line == end_line:
            line = lines[start_line]
            lines[start_line] = (
                line[: edit.range.start.character]
                + edit.new_text
                + line[edit.range.end.character :]
            )
        else:
            # Multi-line edit (rare in our formatter)
            lines[start_line : end_line + 1] = [edit.new_text]

    formatted_text = "\n".join(lines)

    if output:
        output.write(formatted_text)
        click.echo(f"✓ Formatted and written to {output.name}")
    else:
        click.echo(formatted_text)


@cli.command()  # type: ignore
@click.argument("text")  # type: ignore
def complete(text: str) -> None:
    """Get completions for a given text."""
    completions = get_completions(text, len(text))

    if not completions:
        click.echo("No completions available.")
        return

    click.echo(f"Completions for '{text}':")
    for i, comp in enumerate(completions[:10], 1):  # Show first 10
        detail = f" - {comp.detail}" if comp.detail else ""
        click.echo(f"  {i}. {comp.label}{detail}")

    if len(completions) > 10:
        click.echo(f"  ... and {len(completions) - 10} more")


@cli.command()  # type: ignore
@click.argument("file", type=click.File("r"))  # type: ignore
@click.option("--line", "-l", type=int, default=0, help="Line number (0-based)")  # type: ignore
@click.option("--column", "-c", type=int, default=0, help="Column number (0-based)")  # type: ignore
def hover(file: Any, line: int, column: int) -> None:
    """Get hover information for a position in a file."""
    text = file.read()
    hover_info = get_hover_info(text, line, column)

    if not hover_info or not hover_info.contents:
        click.echo("No hover information available at this position.")
        return

    if hasattr(hover_info.contents, "value"):
        click.echo(hover_info.contents.value)
    else:
        click.echo(str(hover_info.contents))


@cli.command()  # type: ignore
@click.argument("file", type=click.File("r"))  # type: ignore
def stats(file: Any) -> None:
    """Show statistics about a training file."""
    text = file.read()
    lines = text.strip().split("\n")

    # Count exercises (non-empty lines)
    exercises = [line for line in lines if line.strip()]

    click.echo(click.style("Training File Statistics:", bold=True))
    click.echo(f"  Total lines: {len(lines)}")
    click.echo(f"  Exercises: {len(exercises)}")

    # Check for errors
    diagnostics = get_diagnostics(text)
    if diagnostics:
        click.echo(click.style(f"  Errors: {len(diagnostics)}", fg="red"))
    else:
        click.echo(click.style("  Errors: 0", fg="green"))


@cli.command()  # type: ignore
@click.option("--timeout", "-t", type=float, default=5.0, help="Connection timeout in seconds")  # type: ignore
def test_connection(timeout: float) -> None:
    """Test connection to the LSP server."""
    async def _test() -> None:
        try:
            config = LSPClientConfig(timeout=timeout)
            async with LSPClient(config) as client:
                click.echo("Starting LSP server...")
                connected = await client.verify_connection()

                if connected:
                    click.echo(click.style("✓ Connection successful!", fg="green"))
                    click.echo(f"Server capabilities: {len(client.server_capabilities or {})} features")

                    if client.server_capabilities:
                        click.echo("\nSupported features:")
                        for key in sorted(client.server_capabilities.keys()):
                            if client.server_capabilities[key]:
                                click.echo(f"  • {key}")
                else:
                    click.echo(click.style("✗ Connection failed", fg="red"))
                    sys.exit(1)
        except Exception as e:
            click.echo(click.style(f"✗ Error: {e}", fg="red"))
            sys.exit(1)

    asyncio.run(_test())


@cli.command()  # type: ignore
@click.argument("file", type=click.File("r"))  # type: ignore
@click.option("--json-output", "-j", is_flag=True, help="Output as JSON")  # type: ignore
def verify(file: Any, json_output: bool) -> None:
    """Verify source code using the LSP server."""
    async def _verify() -> None:
        text = file.read()

        try:
            async with LSPClient() as client:
                await client.initialize()
                result = await client.verify_source_parsing(text)

                if json_output:
                    click.echo(json.dumps(result, indent=2))
                else:
                    if result["has_errors"]:
                        click.echo(click.style(f"✗ Found {result['error_count']} error(s):", fg="red"))
                        for diag in result["diagnostics"]:
                            line = diag["range"]["start"]["line"] + 1
                            col = diag["range"]["start"]["character"] + 1
                            click.echo(f"  Line {line}, Col {col}: {diag['message']}")
                        sys.exit(1)
                    else:
                        click.echo(click.style("✓ No errors found!", fg="green"))
        except Exception as e:
            click.echo(click.style(f"✗ Error: {e}", fg="red"))
            sys.exit(1)

    asyncio.run(_verify())


@cli.command()  # type: ignore
@click.argument("file", type=click.File("r"))  # type: ignore
@click.option("--json-output", "-j", is_flag=True, help="Output as JSON")  # type: ignore
def test_all(file: Any, json_output: bool) -> None:
    """Test all LSP features with a source file."""
    async def _test() -> None:
        text = file.read()

        try:
            async with LSPClient() as client:
                await client.initialize()
                result = await client.verify_all_features(text)

                if json_output:
                    click.echo(json.dumps(result, indent=2))
                else:
                    click.echo(click.style("LSP Feature Test Results:", bold=True))
                    click.echo()

                    for feature_name, feature_data in result["features"].items():
                        if feature_data.get("supported"):
                            status = click.style("✓", fg="green")
                        else:
                            status = click.style("✗", fg="red")

                        click.echo(f"{status} {feature_name}")

                        if "count" in feature_data:
                            click.echo(f"    Items: {feature_data['count']}")

                        if "error" in feature_data:
                            click.echo(f"    Error: {feature_data['error']}")

                    click.echo()

                    # Summary
                    total = len(result["features"])
                    supported = sum(1 for f in result["features"].values() if f.get("supported"))

                    if supported == total:
                        click.echo(click.style(f"All {total} features supported!", fg="green"))
                    else:
                        click.echo(
                            click.style(f"{supported}/{total} features supported", fg="yellow")
                        )
        except Exception as e:
            click.echo(click.style(f"✗ Error: {e}", fg="red"))
            sys.exit(1)

    asyncio.run(_test())


@cli.command()  # type: ignore
@click.argument("source")  # type: ignore
@click.option("--line", "-l", type=int, default=0, help="Line number (0-based)")  # type: ignore
@click.option("--char", "-c", type=int, default=0, help="Character position (0-based)")  # type: ignore
def test_completion(source: str, line: int, char: int) -> None:
    """Test completion feature with LSP server."""
    async def _test() -> None:
        try:
            async with LSPClient() as client:
                await client.initialize()

                uri = "file:///test/completion.training"
                await client.open_document(uri, "training", 1, source + "\n")

                completions = await client.completion(uri, line, char)

                if completions:
                    click.echo(f"Found {len(completions)} completion(s):")
                    for i, comp in enumerate(completions[:20], 1):
                        label = comp.get("label", "")
                        detail = comp.get("detail", "")
                        click.echo(f"  {i}. {label}")
                        if detail:
                            click.echo(f"      {detail}")
                else:
                    click.echo("No completions found.")

                await client.close_document(uri)
        except Exception as e:
            click.echo(click.style(f"✗ Error: {e}", fg="red"))
            sys.exit(1)

    asyncio.run(_test())


@cli.command()  # type: ignore
@click.argument("source")  # type: ignore
@click.option("--line", "-l", type=int, default=0, help="Line number (0-based)")  # type: ignore
@click.option("--char", "-c", type=int, default=0, help="Character position (0-based)")  # type: ignore
def test_hover(source: str, line: int, char: int) -> None:
    """Test hover feature with LSP server."""
    async def _test() -> None:
        try:
            async with LSPClient() as client:
                await client.initialize()

                uri = "file:///test/hover.training"
                await client.open_document(uri, "training", 1, source + "\n")

                hover = await client.hover(uri, line, char)

                if hover and hover.get("contents"):
                    contents = hover["contents"]
                    if isinstance(contents, dict):
                        value = contents.get("value", str(contents))
                    else:
                        value = str(contents)

                    click.echo("Hover information:")
                    click.echo(value)
                else:
                    click.echo("No hover information available.")

                await client.close_document(uri)
        except Exception as e:
            click.echo(click.style(f"✗ Error: {e}", fg="red"))
            sys.exit(1)

    asyncio.run(_test())


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
