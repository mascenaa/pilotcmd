#!/usr/bin/env python3

import asyncio
from typing import List, Optional

import typer
from rich.console import Console
from rich.panel import Panel

from pilotcmd.os_utils.detector import OSDetector
from pilotcmd.models.factory import ModelFactory
from pilotcmd.nlp.parser import NLPParser
from pilotcmd.nlp.simple_parser import SimpleParser
from pilotcmd.executor.command_executor import CommandExecutor
from pilotcmd.context_db.manager import ContextManager

app = typer.Typer(
    name="pilotcmd",
    help="🚁 Your AI-powered terminal copilot",
    add_completion=False,
    rich_markup_mode="rich",
)

console = Console()


@app.callback()
def main(
    ctx: typer.Context,
    model: str = typer.Option(
        "openai", "--model", "-m", help="AI model to use (openai, ollama)"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-d", help="Show commands without executing"
    ),
    auto_run: bool = typer.Option(
        False, "--run", "-r", help="Execute without confirmation"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    thinking: bool = typer.Option(
        False, "--thinking", help="Enable multi-step planning mode"
    ),
) -> None:
    """🚁 Your AI-powered terminal copilot"""

    # Store options in context for subcommands to access
    ctx.ensure_object(dict)
    ctx.obj["model"] = model
    ctx.obj["dry_run"] = dry_run
    ctx.obj["auto_run"] = auto_run
    ctx.obj["verbose"] = verbose
    ctx.obj["thinking"] = thinking


@app.command("run", help="Execute a natural language command")
def run_command(
    ctx: typer.Context,
    prompt: str = typer.Argument(..., help="Natural language command prompt"),
    model: Optional[str] = typer.Option(
        None, "--model", "-m", help="AI model to use (openai, ollama)"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-d", help="Show commands without executing"
    ),
    auto_run: bool = typer.Option(
        False, "--run", "-r", help="Execute without confirmation"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    thinking: bool = typer.Option(
        False, "--thinking", help="Enable multi-step planning mode"
    ),
) -> None:
    """
    Convert natural language prompts into system commands and execute them safely.

    Example:
        pilotcmd run "list all Python files in current directory"
        pilotcmd run "change network IP to 192.168.1.100" --dry-run
        pilotcmd run "install docker" --model ollama
    """

    # Use local options if provided, otherwise fallback to context
    model = model or ctx.obj.get("model", "openai")
    dry_run = dry_run or ctx.obj.get("dry_run", False)
    auto_run = auto_run or ctx.obj.get("auto_run", False)
    verbose = verbose or ctx.obj.get("verbose", False)

    # Prioritize the thinking flag from the command if set, otherwise use the global flag.
    thinking_is_set = thinking or ctx.obj.get("thinking", False)

    try:
        if verbose:
            console.print(
                Panel(
                    "[bold blue]🚁 PilotCmd v0.1.0[/bold blue]\n"
                    "[dim]Your AI-powered terminal copilot[/dim]",
                    border_style="blue",
                )
            )
        if thinking_is_set:
            console.print(
                "[yellow]🧠 Thinking mode enabled - this uses more tokens[/yellow]"
            )

        # Initialize components
        os_detector = OSDetector()
        model_factory = ModelFactory()
        context_manager = ContextManager()

        # Get OS info
        os_info = os_detector.detect()
        if verbose:
            console.print(f"[dim]→ Detected OS: {os_info.name} {os_info.version}[/dim]")

        # Get AI model
        try:
            ai_model = model_factory.get_model(
                model,
                max_tokens=3000 if thinking_is_set else 1000,
                thinking=thinking_is_set,
            )
            if verbose:
                console.print(f"[dim]→ Using model: {model}[/dim]")

            # Create NLP parser with AI model
            parser = NLPParser(ai_model, os_info)
        except Exception as e:
            if verbose:
                console.print(
                    f"[dim]→ AI model not available ({str(e)}), using simple parser[/dim]"
                )

            # Fallback to simple parser
            parser = SimpleParser(os_info)

        # Parse the prompt
        commands = asyncio.run(parser.parse(prompt))

        if verbose and getattr(parser, "last_usage", None):
            usage = parser.last_usage
            console.print(
                f"[dim]→ Token usage: input {usage['prompt_tokens']}, output {usage['completion_tokens']}, total {usage['total_tokens']}[/dim]"
            )

        if not commands:
            console.print(
                "[yellow]❓ Could not understand the prompt. Please try rephrasing.[/yellow]"
            )
            return

        # Show suggested commands
        console.print("→ Suggested commands:")
        for i, cmd in enumerate(commands, 1):
            console.print(f"  {i}. [cyan]{cmd.command}[/cyan]")

        if dry_run:
            console.print("[yellow]🔍 Dry run mode - commands not executed[/yellow]")
            # Save to history even in dry run mode
            context_manager.save_prompt(prompt, commands, os_info)
            return

        # Ask for confirmation unless auto-run is enabled
        if not auto_run:
            if not typer.confirm(f"→ Run these commands?"):
                console.print("[yellow]Operation cancelled[/yellow]")
                return

        # Execute commands
        executor = CommandExecutor(os_info)

        # Save prompt before execution
        context_manager.save_prompt(prompt, commands, os_info)

        results = asyncio.run(executor.execute_commands(commands))

        # Show results
        success_count = sum(1 for result in results if result.success)
        failed_count = len(results) - success_count

        if failed_count == 0:
            console.print(
                f"[green]✅ All {len(results)} commands executed successfully[/green]"
            )
        else:
            console.print(
                f"[yellow]⚠️  {success_count} succeeded, {failed_count} failed[/yellow]"
            )

        for result in results:
            if result.success:
                if result.stdout:
                    console.print(
                        Panel(
                            result.stdout.strip(),
                            title=f"[bold green]Output for: {result.command.command}[/bold green]",
                            border_style="green",
                            expand=False,
                        )
                    )
                if result.stderr:
                    console.print(
                        Panel(
                            result.stderr.strip(),
                            title=f"[bold yellow]Warnings for: {result.command.command}[/bold yellow]",
                            border_style="yellow",
                            expand=False,
                        )
                    )
            else:
                console.print(f"[red]❌ Failed: {result.command}[/red]")
                if result.stderr:
                    console.print(
                        Panel(
                            result.stderr.strip(),
                            title=f"[bold red]Error for: {result.command.command}[/bold red]",
                            border_style="red",
                            expand=False,
                        )
                    )
                if result.error_message:
                    console.print(f"   [dim]Reason: {result.error_message}[/dim]")

        # Save execution results to history
        context_manager.save_execution_results(results)

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        if verbose:
            console.print_exception()
        else:
            console.print(f"[red]❌ Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command("history")
def show_history(
    limit: int = typer.Option(
        10, "--limit", "-l", help="Number of recent commands to show"
    ),
    search: Optional[str] = typer.Option(
        None, "--search", "-s", help="Search in command history"
    ),
) -> None:
    """Show command history"""
    try:
        context_manager = ContextManager()
        history = context_manager.get_history(limit=limit, search=search)

        if not history:
            console.print("[yellow]No command history found[/yellow]")
            return

        console.print(
            f"[bold blue]📚 Command History (last {len(history)} entries)[/bold blue]"
        )
        console.print()

        for entry in history:
            console.print(f"[dim]{entry.timestamp}[/dim]")
            console.print(f"[bold]Prompt:[/bold] {entry.prompt}")
            console.print(f"[cyan]Commands:[/cyan]")
            for cmd in entry.commands:
                console.print(f"  • {cmd}")
            console.print()

    except Exception as e:
        console.print(f"[red]❌ Error accessing history: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command("explain")
def explain_command(
    ctx: typer.Context,
    prompt: str = typer.Argument(
        ..., help="Natural language command prompt to explain"
    ),
    model: Optional[str] = typer.Option(
        None, "--model", "-m", help="AI model to use (openai, ollama)"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
) -> None:
    """Explain what commands would be executed without running them (educational mode)"""
    try:
        # Get context values
        ctx_model = ctx.obj.get("model", "openai") if ctx.obj else "openai"
        ctx_verbose = ctx.obj.get("verbose", False) if ctx.obj else False

        # Use command-specific options or fall back to context
        final_model = model or ctx_model
        final_verbose = verbose or ctx_verbose

        # Get OS information
        from pilotcmd.os_utils.detector import OSDetector

        os_detector = OSDetector()
        os_info = os_detector.detect()

        if final_verbose:
            console.print(f"[dim]→ OS detected: {os_info.name} {os_info.version}[/dim]")

        # Initialize context manager
        context_manager = ContextManager()

        # Try to create AI model
        try:
            model_factory = ModelFactory()
            ai_model = model_factory.create_model(final_model)

            if final_verbose:
                console.print(f"[dim]→ Using model: {final_model}[/dim]")

            # Create NLP parser with AI model
            parser = NLPParser(ai_model, os_info)
        except Exception as e:
            if final_verbose:
                console.print(
                    f"[dim]→ AI model not available ({str(e)}), using simple parser[/dim]"
                )

            # Fallback to simple parser
            parser = SimpleParser(os_info)

        # Parse the prompt
        commands = asyncio.run(parser.parse(prompt))

        if final_verbose and getattr(parser, "last_usage", None):
            usage = parser.last_usage
            console.print(
                f"[dim]→ Token usage: input {usage['prompt_tokens']}, output {usage['completion_tokens']}, total {usage['total_tokens']}[/dim]"
            )

        if not commands:
            console.print(
                "[yellow]❓ Could not understand the prompt. Please try rephrasing.[/yellow]"
            )
            return

        # Show explanation in educational format
        console.print(
            f'[bold blue]📚 Explaining: [/bold blue][italic]"{prompt}"[/italic]'
        )
        console.print()

        if len(commands) == 1:
            cmd = commands[0]
            console.print(
                f"[green]→ This would execute:[/green] [cyan]{cmd.command}[/cyan]"
            )
            console.print(f"[green]→ Explanation:[/green] {cmd.explanation}")

            if cmd.requires_sudo:
                console.print(
                    "[yellow]⚠️  This command requires administrator privileges[/yellow]"
                )

            # Handle both enum and string safety levels
            safety_level = (
                cmd.safety_level.value
                if hasattr(cmd.safety_level, "value")
                else cmd.safety_level
            )
            if safety_level == "caution":
                console.print(
                    "[yellow]⚠️  Exercise caution when running this command[/yellow]"
                )
            elif safety_level == "dangerous":
                console.print("[red]🚨 WARNING: This command could be dangerous![/red]")
        else:
            console.print(
                f"[green]→ This would execute {len(commands)} commands:[/green]"
            )
            for i, cmd in enumerate(commands, 1):
                console.print(f"  [bold]{i}.[/bold] [cyan]{cmd.command}[/cyan]")
                console.print(f"     [dim]{cmd.explanation}[/dim]")

                if cmd.requires_sudo:
                    console.print(
                        "     [yellow]⚠️  Requires administrator privileges[/yellow]"
                    )

                # Handle both enum and string safety levels
                safety_level = (
                    cmd.safety_level.value
                    if hasattr(cmd.safety_level, "value")
                    else cmd.safety_level
                )
                if safety_level == "caution":
                    console.print("     [yellow]⚠️  Exercise caution[/yellow]")
                elif safety_level == "dangerous":
                    console.print("     [red]🚨 WARNING: Potentially dangerous![/red]")
                console.print()

        console.print(
            '[dim]💡 To actually run these commands, use: [bold]pilotcmd run[/bold] "[italic]your prompt[/italic]"[/dim]'
        )

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        if final_verbose:
            console.print_exception()
        else:
            console.print(f"[red]❌ Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command("config")
def configure(
    model: Optional[str] = typer.Option(
        None, "--model", "-m", help="Set default AI model"
    ),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="Set OpenAI API key"),
    show: bool = typer.Option(False, "--show", help="Show current configuration"),
) -> None:
    """Configure PilotCmd settings"""
    try:
        from pilotcmd.config.manager import ConfigManager

        config_manager = ConfigManager()

        if show:
            config = config_manager.get_config()
            console.print("[bold blue]🔧 Current Configuration[/bold blue]")
            console.print(f"Default model: [cyan]{config.default_model}[/cyan]")
            console.print(
                f"API key set: [cyan]{'Yes' if config.openai_api_key else 'No'}[/cyan]"
            )
            return

        if model:
            config_manager.set_default_model(model)
            console.print(f"[green]✅ Default model set to: {model}[/green]")

        if api_key:
            config_manager.set_openai_api_key(api_key)
            console.print("[green]✅ OpenAI API key updated[/green]")

        if not model and not api_key:
            console.print(
                "[yellow]No configuration changes specified. Use --help for options.[/yellow]"
            )

    except Exception as e:
        console.print(f"[red]❌ Error updating configuration: {str(e)}[/red]")
        raise typer.Exit(1)


# For backwards compatibility, also accept direct prompts as the default command
@app.command("prompt", hidden=True)
def prompt_command(
    ctx: typer.Context,
    prompt: str = typer.Argument(..., help="Natural language command prompt"),
) -> None:
    """Hidden backwards compatibility command"""
    run_command(ctx, prompt)


if __name__ == "__main__":
    app()
